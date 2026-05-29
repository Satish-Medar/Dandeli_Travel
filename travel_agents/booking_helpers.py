# Extracts booking-specific context and helpers used during booking conversations.
# File: travel_agents/booking_helpers.py


import re
from typing import Sequence

from langchain_core.messages import AIMessage, HumanMessage

from .content import extract_content


def find_customer_contact(messages: Sequence) -> str | None:
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = extract_content(msg.content)
            phone_match = re.search(r"(?<!\w)(?:\+?\d[\d\s-]{7,}\d)", content)
            email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", content)
            if phone_match: return phone_match.group(0).strip()
            if email_match: return email_match.group(0).strip()
    return None


def find_booking_id(messages: Sequence) -> str | None:
    for msg in reversed(messages):
        match = re.search(r"\bBK-\d{4}\b", extract_content(msg.content), re.IGNORECASE)
        if match: return match.group(0).upper()
    return None


def current_booking_context(messages: Sequence) -> list:
    start_index = 0
    start_markers = ["book it", "book this", "book resort", "i want to book", "booking request"]
    terminal_markers = [
        "your booking request has been sent",
        "booking request created",
        "booking id:",
        "cancelled this booking request draft",
    ]
    for index, msg in enumerate(messages):
        if isinstance(msg, AIMessage) and getattr(msg, "name", "") == "Booker" and any(marker in extract_content(msg.content).lower() for marker in terminal_markers):
            start_index = index + 1
        if isinstance(msg, HumanMessage) and any(marker in extract_content(msg.content).lower() for marker in ["cancel", "cancel it", "stop", "never mind", "nevermind"]):
            start_index = index + 1

    for index in range(start_index, len(messages)):
        if isinstance(messages[index], HumanMessage) and any(marker in extract_content(messages[index].content).lower() for marker in start_markers):
            # Keep the whole active booking draft from the first trigger, so repeated
            # "book it" messages do not erase the originally selected resort.
            start_index = max(start_index, max(0, index - 3))
            break
    return list(messages[start_index:])


def booking_in_progress(messages: Sequence) -> bool:
    booking_messages = current_booking_context(messages)
    if not booking_messages:
        return False
    for msg in reversed(booking_messages):
        if isinstance(msg, AIMessage) and getattr(msg, "name", "") == "Booker":
            return not any(marker in extract_content(msg.content).lower() for marker in ["your booking request has been sent", "booking request created", "booking id:", "cancelled this booking request draft"])
        if isinstance(msg, HumanMessage) and any(marker in extract_content(msg.content).lower() for marker in ["book it", "book this", "book resort", "i want to book"]):
            return True
    return False


def booking_confirmed(messages: Sequence) -> bool:
    confirmation_markers = {"confirm", "confiem", "cnfirm", "yes confirm", "confirm booking", "go ahead", "yes go ahead"}
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = " ".join(extract_content(msg.content).lower().split())
            if content in confirmation_markers: return True
            if any(marker in content for marker in ["cancel", "stop", "never mind", "nevermind", "book resort", "book it", "i want to book"]): return False
    return False


def booking_cancelled(messages: Sequence) -> bool:
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = " ".join(extract_content(msg.content).lower().split())
            if any(marker in content for marker in ["cancel", "cancel it", "stop", "never mind", "nevermind"]): return True
            if content in {"confirm", "confiem", "cnfirm", "yes confirm", "confirm booking", "go ahead", "yes go ahead"}: return False
    return False
