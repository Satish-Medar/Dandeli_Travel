from typing import Sequence
from langchain_core.messages import BaseMessage, HumanMessage

from .booking_helpers import booking_in_progress

def classify_user_intent(messages: str | Sequence[BaseMessage]) -> str:
    if isinstance(messages, str):
        text = messages
        msg_list = [HumanMessage(content=text)]
    else:
        text = str(getattr(messages[-1], "content", ""))
        msg_list = messages
        
    normalized = " ".join(text.lower().split())
    booking_markers = ["book it", "book this", "i want to book", "book ", "booking", "booking status", "status of my booking", "check my booking", "check booking status", "bk-"]
    planning_markers = ["plan it", "plan a trip", "plan my trip", "itinerary", "2 days", "3 days", "coming alone", "coming solo", "what should i do", "plan it simply"]
    if normalized in {"hi", "hello", "hey"} or any(marker in normalized for marker in ["thanks", "thank you", "help", "what can you do"]):
        return "SmallTalk"
    if booking_in_progress(msg_list) or any(marker in normalized for marker in booking_markers):
        return "Booker"
    if any(marker in normalized for marker in planning_markers):
        return "Planner"
    if any(marker in normalized for marker in ["stay", "trip", "resort", "budget", "rating", "rafting", "bird watching", "nature", "family", "solo"]):
        return "Researcher"
        
    if len(msg_list) >= 2:
        last_ai_msg = msg_list[-2]
        if getattr(last_ai_msg, "name", "") == "Researcher":
            followup_markers = ["price", "cost", "how much", "contact", "phone", "email", "website", "link", "where", "location", "details", "more info", "tell me more", "that one", "the one"]
            if any(marker in normalized for marker in followup_markers):
                return "Researcher"
                
    return "OutOfScope"
