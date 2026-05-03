import os
from pathlib import Path

from fastapi import HTTPException
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from travel_agents import graph
from .models import AppConfig, AssistantTurn, SessionSummary
from .store import list_sessions_for_user, utc_now

BASE_DIR = Path(__file__).resolve().parent.parent


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


async def invoke_assistant_from_messages(messages, user_message: str) -> tuple[str, str]:
    # Sliding window: Keep only the most recent 30 messages (15 turns) to prevent context overflow while maintaining deep booking history
    working_messages = list(messages)[-30:]
    if len(messages) > 30:
        while working_messages and not isinstance(working_messages[0], HumanMessage):
            working_messages.pop(0)
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
