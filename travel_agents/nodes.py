import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .booking_helpers import booking_cancelled, booking_confirmed, current_booking_context, find_booking_id, find_customer_contact
from .content import extract_content
from .date_helpers import find_explicit_booking_dates, find_relative_booking_dates
from .llms import planner_agent, planner_prompt
from .resort_helpers import find_last_recommended_resort, find_selected_resort, resolve_resort_followup_query
from travel_tools.booking_tool import book_resort
from travel_tools.booking_status_tool import get_booking_status
from travel_tools.search_tool import search_resorts


def summarize_guest_details(messages) -> str:
    joined = "\n".join([extract_content(msg.content).lower() for msg in messages if isinstance(msg, HumanMessage)])
    if any(marker in joined for marker in ["coming alone", "solo", "single"]): return "1 person, calm nature trip, bird watching"
    for pattern in [r"family of (\d+)", r"(?:group of|we(?:'|â€™)?re|we are)\s+(\d+)\s+people", r"for (\d+) (?:people|persons|guests)"]:
        match = re.search(pattern, joined)
        if match: return f"{match.group(1)} guests"
    return "Guest details shared in chat"


def smalltalk_node(state):
    latest = next((extract_content(msg.content).strip().lower() for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "")
    if latest in {"thanks", "thank you", "thankyou"}: content = "You're welcome. I can also help you compare resorts, plan an itinerary, or place a booking request."
    elif "help" in latest or "what can you do" in latest: content = "I can help you find resorts in Dandeli, compare options by budget and rating, plan a trip, and place a booking request."
    else: content = "Hi! I can help you find resorts in Dandeli, plan a trip, compare options, or place a booking request. Tell me your budget, group size, dates, or the kind of stay you want."
    return {"messages": [AIMessage(content=content, name="SmallTalk")]}


def out_of_scope_node(state):
    return {"messages": [AIMessage(content="Please ask queries related to Dandeli, resorts, trip planning, pricing, activities, or booking.", name="OutOfScope")]}


def researcher_node(state):
    latest = next((extract_content(msg.content) for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "")
    content = "No user query was available for resort research." if not latest else search_resorts.invoke(resolve_resort_followup_query(state["messages"], latest))
    return {"messages": [AIMessage(content=content, name="Researcher")]}


def planner_node(state):
    latest = next((extract_content(msg.content) for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "")
    research_context = search_resorts.invoke(latest) if latest else ""
    planner_context = f"Use this verified resort research as the factual grounding for the itinerary.\n\n{research_context}" if research_context else "No verified resort research was available."
    result = planner_agent.invoke({"messages": [SystemMessage(content=planner_prompt), SystemMessage(content=planner_context)] + list(state["messages"])})
    return {"messages": [AIMessage(content=extract_content(result["messages"][-1].content), name="Planner")]}


def booker_node(state):
    booking_messages = current_booking_context(state["messages"])
    latest = next((extract_content(msg.content) for msg in reversed(booking_messages) if isinstance(msg, HumanMessage)), "")
    normalized = latest.lower()
    if any(marker in normalized for marker in ["booking status", "status of my booking", "check my booking", "check booking status", "bk-"]):
        booking_id = find_booking_id(booking_messages)
        content = get_booking_status.invoke({"booking_id": booking_id}) if booking_id else "Send your booking ID, for example `BK-0001`, and I will check the latest status."
        return {"messages": [AIMessage(content=content, name="Booker")]}
    if booking_cancelled(booking_messages):
        base_reply = "Okay, I cancelled this booking request draft.\\n\\n"
        if any(marker in normalized for marker in ["find", "search", "show", "instead", "what", "does it"]):
            from travel_tools import search_resorts
            research = search_resorts.invoke(latest)
            return {"messages": [AIMessage(content=f"{base_reply}{research}", name="Booker")]}
        return {"messages": [AIMessage(content=f"{base_reply}If you want to start a new one, tell me the resort and dates.", name="Booker")]}
    explicit_dates = find_explicit_booking_dates(booking_messages) or find_relative_booking_dates(booking_messages)
    if not explicit_dates: return {"messages": [AIMessage(content="Before I place the booking request, send your exact check-in and check-out dates, for example `March 26, 2026 to March 28, 2026`.", name="Booker")]}
    resort_name = find_selected_resort(booking_messages) or find_last_recommended_resort(booking_messages)
    if not resort_name: return {"messages": [AIMessage(content="Tell me which resort you want to book, and I will place the request.", name="Booker")]}
    customer_contact = find_customer_contact(booking_messages)
    if not customer_contact: return {"messages": [AIMessage(content="Before I place the booking request, send your contact number or email so the resort owner can reach you.", name="Booker")]}
    guest_details = summarize_guest_details(booking_messages)
    if not booking_confirmed(booking_messages):
        return {"messages": [AIMessage(content=f"Please confirm this booking:\nResort: {resort_name}\nDates: {explicit_dates}\nGuests: {guest_details}\nContact: {customer_contact}\n\nReply `confirm` to send it.", name="Booker")]}
    return {"messages": [AIMessage(content=book_resort.invoke({"resort_name": resort_name, "check_in_out_dates": explicit_dates, "guest_details": guest_details, "customer_contact": customer_contact}), name="Booker")]}
