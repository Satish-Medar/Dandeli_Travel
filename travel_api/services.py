# Defines backend service logic for travel booking and resort data operations.
# File: travel_api/services.py

# Simple overview (plain words):
# - This module contains business logic used by the HTTP handlers in
# - travel_api.app. Keep lightweight helpers here: recording messages,
# - serializing session summaries, and calling the agent graph to generate
# - assistant replies.
# - Important: functions should avoid HTTP details and focus on data logic.


import os
import re
from pathlib import Path

from fastapi import HTTPException
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from travel_agents import graph
from .models import AppConfig, AssistantTurn, SessionSummary
from .store import list_sessions_for_user, utc_now

BASE_DIR = Path(__file__).resolve().parent.parent
RECENT_CONTEXT_MESSAGES = int(os.getenv("ASSISTANT_RECENT_CONTEXT_MESSAGES", "80"))
OLDER_MEMORY_CHAR_LIMIT = int(os.getenv("ASSISTANT_OLDER_MEMORY_CHAR_LIMIT", "8000"))


def record_message(session: dict, role: str, content: str, name: str = "") -> None:
    session.setdefault("messages", []).append({"role": role, "content": content, "name": name, "created_at": utc_now()})
    if role == "user" and (not session.get("title") or session.get("title") == "New conversation"):
        session["title"] = (" ".join(content.split())[:48] + ("..." if len(" ".join(content.split())) > 48 else "")) or "New conversation"
    session["updated_at"] = utc_now()


def serialize_session_summary(session_id: str, session: dict) -> SessionSummary:
    preview = next((" ".join(item.get("content", "").split())[:80] for item in reversed(session.get("messages", [])) if item.get("role") == "user"), "")
    return SessionSummary(session_id=session_id, title=session.get("title") or "New conversation", preview=preview, updated_at=session.get("updated_at", utc_now()))


def app_config_payload() -> AppConfig:
    publishable_key = os.getenv("CLERK_PUBLISHABLE_KEY") or os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
    env_path = BASE_DIR / ".env"
    if not publishable_key and env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line.startswith("CLERK_PUBLISHABLE_KEY=") or line.startswith("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="):
                publishable_key = line.split("=", 1)[1].strip() or None
                break
    return AppConfig(clerk_publishable_key=publishable_key, clerk_enabled=bool(publishable_key))


async def invoke_assistant(session: dict, user_message: str) -> tuple[str, str]:
    messages = [HumanMessage(content=item["content"], name=item.get("name") or "") if item.get("role") == "user" else AIMessage(content=item["content"], name=item.get("name") or "") if item.get("role") == "assistant" else SystemMessage(content=item["content"], name=item.get("name") or "") for item in session.get("messages", [])]
    return await invoke_assistant_from_messages(messages, user_message)


async def invoke_assistant_from_turns(messages: list[AssistantTurn], user_message: str) -> tuple[str, str]:
    prior_messages = []
    for item in messages:
        if item.role == "user":
            prior_messages.append(HumanMessage(content=item.content, name=item.name or ""))
        elif item.role == "assistant":
            prior_messages.append(AIMessage(content=item.content, name=item.name or ""))
        else:
            prior_messages.append(SystemMessage(content=item.content, name=item.name or ""))
    return await invoke_assistant_from_messages(prior_messages, user_message)


def _message_text(message) -> str:
    return " ".join(str(getattr(message, "content", "") or "").split())


def _find_known_resorts_in_messages(messages) -> list[str]:
    text = "\n".join(_message_text(message) for message in messages).lower()
    if not text:
        return []

    try:
        from travel_tools.search_tool import get_known_resort_names
        known_resorts = get_known_resort_names()
    except Exception:
        known_resorts = []

    found = []
    for resort_name in known_resorts:
        cleaned = str(resort_name or "").strip()
        if cleaned and cleaned.lower() in text and cleaned not in found:
            found.append(cleaned)
    return found[:12]


def _extract_booking_memory(messages) -> list[str]:
    facts = []
    combined = "\n".join(_message_text(message) for message in messages)

    date_matches = re.findall(
        r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
        r"sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2},?\s+\d{4}\s+(?:to|-)\s+"
        r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
        r"sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2},?\s*\d{4}\b",
        combined,
        flags=re.IGNORECASE,
    )
    if date_matches:
        facts.append(f"Dates mentioned: {date_matches[-1]}")

    contact_match = None
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            text = _message_text(message)
            contact_match = (
                re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
                or re.search(r"(?<!\w)(?:\+?\d[\d\s-]{7,}\d)", text)
            )
            if contact_match:
                break
    if contact_match:
        facts.append(f"Customer contact mentioned: {contact_match.group(0).strip()}")

    return facts


def build_long_term_memory(messages) -> SystemMessage | None:
    if not messages:
        return None

    user_turns = [_message_text(message) for message in messages if isinstance(message, HumanMessage)]
    first_user_turn = next((turn for turn in user_turns if turn), "")
    known_resorts = _find_known_resorts_in_messages(messages)
    booking_facts = _extract_booking_memory(messages)

    older_turns = []
    for message in messages:
        role = "User" if isinstance(message, HumanMessage) else "Assistant" if isinstance(message, AIMessage) else "System"
        name = getattr(message, "name", "") or ""
        text = _message_text(message)
        if text:
            older_turns.append(f"{role}{f'/{name}' if name else ''}: {text}")

    transcript = "\n".join(older_turns)
    if len(transcript) > OLDER_MEMORY_CHAR_LIMIT:
        transcript = transcript[:OLDER_MEMORY_CHAR_LIMIT].rstrip() + "\n[Earlier-memory transcript truncated by character budget.]"

    memory_lines = [
        "Long-term memory from earlier turns in this same chat.",
        "Use this memory to answer follow-ups; do not ask again for details that are already present unless they are invalid or ambiguous.",
    ]
    if first_user_turn:
        memory_lines.append(f"First user request: {first_user_turn}")
    if known_resorts:
        memory_lines.append(f"Resorts already discussed: {', '.join(known_resorts)}")
    memory_lines.extend(booking_facts)
    if transcript:
        memory_lines.append("Earlier transcript:")
        memory_lines.append(transcript)

    return SystemMessage(content="\n".join(memory_lines))


def build_agent_context(messages):
    if len(messages) <= RECENT_CONTEXT_MESSAGES:
        return list(messages)

    older_messages = list(messages)[:-RECENT_CONTEXT_MESSAGES]
    recent_messages = list(messages)[-RECENT_CONTEXT_MESSAGES:]
    memory_message = build_long_term_memory(older_messages)
    if memory_message:
        return [memory_message] + recent_messages
    return recent_messages


async def invoke_assistant_from_messages(messages, user_message: str) -> tuple[str, str]:
    working_messages = build_agent_context(messages)
    working_messages.append(HumanMessage(content=user_message))
    assistant_reply = ""
    node_name = ""
    async for event in graph.astream({"messages": working_messages}):
        for node_state in event.values():
            if "messages" in node_state:
                last_msg = node_state["messages"][-1]
                assistant_reply = str(last_msg.content)
                node_name = getattr(last_msg, "name", "")
    if not assistant_reply:
        raise HTTPException(status_code=500, detail="Assistant did not return a response.")
    return assistant_reply, node_name


def list_user_sessions(user_id: str):
    summaries = [serialize_session_summary(session_id, session) for session_id, session in list_sessions_for_user(user_id).items()]
    summaries.sort(key=lambda item: item.updated_at, reverse=True)
    return summaries
