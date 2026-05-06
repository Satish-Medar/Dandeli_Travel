import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .booking_helpers import current_booking_context
from .content import extract_content
from .llms import planner_agent, planner_prompt
from .resort_helpers import resolve_resort_followup_query
from travel_tools.booking_tool import book_resort
from travel_tools.booking_status_tool import get_booking_status
from travel_tools.search_tool import search_resorts


from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .llms import groq_llm

class BookingExtraction(BaseModel):
    intent: str = Field(description="The user's intent. Must be one of: 'check_status', 'cancel', 'book', 'unknown'")
    booking_id: str | None = Field(description="The booking ID if mentioned (e.g. BK-0001), else None")
    resort_name: str | None = Field(description="The name of the resort they want to book, else None")
    dates: str | None = Field(description="Explicit check-in and check-out dates if mentioned, else None")
    contact: str | None = Field(description="Customer phone number or email, else None")
    guests: str | None = Field(description="Number of guests and details, else None")
    is_confirmed: bool = Field(description="True ONLY if the user explicitly confirms they want to send the booking request now")

def summarize_guest_details(messages) -> str:
    # Deprecated: Handled by BookingExtraction
    pass

async def smalltalk_node(state):
    latest = next((extract_content(msg.content).strip().lower() for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "")
    if latest in {"thanks", "thank you", "thankyou"}: content = "You're welcome. I can also help you compare resorts, plan an itinerary, or place a booking request."
    elif "help" in latest or "what can you do" in latest: content = "I can help you find resorts in Dandeli, compare options by budget and rating, plan a trip, and place a booking request."
    else: content = "Hi! I can help you find resorts in Dandeli, plan a trip, compare options, or place a booking request. Tell me your budget, group size, dates, or the kind of stay you want."
    return {"messages": [AIMessage(content=content, name="SmallTalk")]}


async def out_of_scope_node(state):
    return {"messages": [AIMessage(content="Please ask queries related to Dandeli, resorts, trip planning, pricing, activities, or booking.", name="OutOfScope")]}


async def researcher_node(state):
    latest = next((extract_content(msg.content) for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "")
    if not latest:
        return {"messages": [AIMessage(content="No user query was available for resort research.", name="Researcher")]}
        
    research_context = await search_resorts.ainvoke(resolve_resort_followup_query(state["messages"], latest))
    
    from .llms import groq_llm, groq_70b, gemini_llm, prefer_groq_invoke
    synthesizer = prefer_groq_invoke(groq_70b, prefer_groq_invoke(groq_llm, gemini_llm))
    
    system_prompt = (
        "You are Vana, a helpful Dandeli Travel Assistant. You will receive raw JSON search results from our database. "
        "Your job is to read the JSON data and answer the user's latest question in a beautiful, natural, conversational format. "
        "If the user asks for a comparison, logically compare the best options from the JSON. "
        "If the user asks for a specific number of resorts (e.g. 'top 1' or 'just 2'), provide EXACTLY that many. "
        "If the user asks for contact information (phone, email, website), include it prominently in your response. "
        "If the JSON says no resorts were found, apologize and ask them to adjust their budget or requirements. "
        "Do not invent details not in the search results.\n\n"
        f"Search Results JSON:\n{research_context}"
    )
    
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])[-5:]
    result = await synthesizer.ainvoke(messages)
    
    return {"messages": [AIMessage(content=extract_content(getattr(result, "content", str(result))), name="Researcher")]}


async def planner_node(state):
    latest = next((extract_content(msg.content) for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "")
    research_context = await search_resorts.ainvoke(latest) if latest else ""
    if not latest:
        return {"messages": [AIMessage(content="Please tell me what kind of Dandeli stay you want, including budget, travelers, activities, or resort preferences.", name="Planner")]}
    if not research_context.strip() or "No exact matching resorts found" in research_context:
        return {"messages": [AIMessage(content="I could not find verified resort details for that request. Please share your budget, dates, or preferred resort so I can plan accurately.", name="Planner")]}
    from datetime import datetime
    today_date = datetime.now().strftime("%B %d, %Y")
    planner_context = f"Today is {today_date}. Use this JSON resort data as the factual grounding for the itinerary. DO NOT expose JSON to the user, write naturally.\n\n{research_context}"
    result = await planner_agent.ainvoke({"messages": [SystemMessage(content=planner_prompt), SystemMessage(content=planner_context)] + list(state["messages"])})
    return {"messages": [AIMessage(content=extract_content(result["messages"][-1].content), name="Planner")]}


async def booker_node(state):
    booking_messages = current_booking_context(state["messages"])
    
    from .llms import gemini_llm, groq_llm, groq_70b, prefer_groq_invoke
    
    groq_70b_extractor = groq_70b.with_structured_output(BookingExtraction)
    groq_8b_extractor = groq_llm.with_structured_output(BookingExtraction)
    gemini_extractor = gemini_llm.with_structured_output(BookingExtraction)
    
    from datetime import datetime
    today_date = datetime.now().strftime("%B %d, %Y")
    
    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", f"Today is {today_date}. Extract booking details from the conversation. Convert all relative dates (like 'tomorrow' or 'next Friday') into exact absolute calendar dates. If a value is missing or unclear, set it to None. Intent must be exactly one of: check_status, cancel, book, unknown"),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    # Try 70B, fallback to 8B, fallback to Gemini
    chain = prefer_groq_invoke(
        extraction_prompt | groq_70b_extractor, 
        prefer_groq_invoke(extraction_prompt | groq_8b_extractor, extraction_prompt | gemini_extractor)
    )
    
    try:
        data = await chain.ainvoke({"messages": booking_messages}) # pass full booking context to prevent forgetting resort name
    except Exception as e:
        return {"messages": [AIMessage(content="I'm having trouble parsing your booking details. Could you please specify the resort and dates again?", name="Booker")]}

    if data.intent == "check_status":
        if data.booking_id:
            return {"messages": [AIMessage(content=await get_booking_status.ainvoke({"booking_id": data.booking_id}), name="Booker")]}
        return {"messages": [AIMessage(content="Send your booking ID, for example `BK-0001`, and I will check the latest status.", name="Booker")]}
        
    if data.intent == "cancel":
        base_reply = "Okay, I cancelled this booking request draft.\n\nIf you want to start a new one, tell me the resort and dates."
        return {"messages": [AIMessage(content=base_reply, name="Booker")]}

    if not data.dates:
        return {"messages": [AIMessage(content="Before I place the booking request, send your exact check-in and check-out dates, for example `March 26, 2026 to March 28, 2026`.", name="Booker")]}
    if not data.resort_name:
        return {"messages": [AIMessage(content="Tell me which resort you want to book, and I will place the request.", name="Booker")]}
    if not data.contact:
        return {"messages": [AIMessage(content="Before I place the booking request, send your contact number or email so the resort owner can reach you.", name="Booker")]}
    if not data.guests:
        return {"messages": [AIMessage(content="Please tell me how many guests will be staying, and if there are any children.", name="Booker")]}
        
    from .booking_helpers import booking_confirmed
    if not booking_confirmed(booking_messages):
        return {"messages": [AIMessage(content=f"Please confirm this booking:\nResort: {data.resort_name}\nDates: {data.dates}\nGuests: {data.guests}\nContact: {data.contact}\n\nReply `confirm` to send it.", name="Booker")]}
        
    return {"messages": [AIMessage(content=await book_resort.ainvoke({"resort_name": data.resort_name, "check_in_out_dates": data.dates, "guest_details": data.guests, "customer_contact": data.contact}), name="Booker")]}
