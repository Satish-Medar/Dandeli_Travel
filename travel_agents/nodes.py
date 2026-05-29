# Routes conversation turns into agent nodes and handles booking, planning, research, and small talk.
# File: travel_agents/nodes.py


import re
import json
import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .booking_helpers import current_booking_context
from .content import extract_content
from .llms import planner_agent, planner_prompt
from .resort_helpers import resolve_resort_followup_query
from travel_tools.booking_tool import book_resort
from travel_tools.booking_status_tool import get_booking_status
from travel_tools.search_tool import search_resorts_tool as search_resorts


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


def validate_booking_dates(date_string: str) -> dict:
    """Validate booking dates to ensure they are in the future and valid."""
    from datetime import datetime
    import re
    
    try:
        # Parse date strings like "May 15, 2026 to May 17, 2026",
        # "may 15,2026 to may 17,2026", or "15-05-2026 to 17-05-2026".
        month_pattern = (
            r"((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
            r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|"
            r"dec(?:ember)?)\s+\d{1,2},?\s*\d{4})"
        )
        numeric_pattern = r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
        match = re.search(fr"{month_pattern}\s+(?:to|-)\s+{month_pattern}", date_string, re.IGNORECASE)
        date_format_hint = "Use 'Month DD, YYYY to Month DD, YYYY' or 'DD-MM-YYYY to DD-MM-YYYY'"
        numeric_match = None
        if not match:
            numeric_match = re.search(fr"{numeric_pattern}\s+(?:to|-)\s+{numeric_pattern}", date_string, re.IGNORECASE)
        
        if not match and not numeric_match:
            return {"valid": False, "error": f"Date format not recognized. {date_format_hint}"}
        
        check_in_str = (match or numeric_match).group(1).strip()
        check_out_str = (match or numeric_match).group(2).strip()
        
        def parse_date(value: str):
            cleaned = re.sub(r",\s*", ", ", value.strip())
            cleaned = re.sub(r"\s+", " ", cleaned)
            for fmt in ["%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b %d %Y", "%d-%m-%Y", "%d/%m/%Y"]:
                try:
                    return datetime.strptime(cleaned, fmt)
                except ValueError:
                    continue
            raise ValueError(f"time data '{value}' does not match supported booking date formats")

        check_in = parse_date(check_in_str)
        check_out = parse_date(check_out_str)
        
        # Get today's date without time
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Validation rules
        if check_in <= today:
            return {"valid": False, "error": f"Check-in date ({check_in.strftime('%B %d, %Y')}) cannot be today or in the past."}
        
        if check_out <= check_in:
            return {"valid": False, "error": f"Check-out date ({check_out.strftime('%B %d, %Y')}) must be after check-in date ({check_in.strftime('%B %d, %Y')})."}
        
        # All validations passed
        return {"valid": True, "check_in": check_in, "check_out": check_out}
        
    except ValueError as e:
        return {"valid": False, "error": f"Invalid date: {str(e)}"}
    except Exception as e:
        return {"valid": False, "error": f"Error validating dates: {str(e)}"}


def normalize_date_string(date_str: str, reference_year: int | None = None) -> str | None:
    """Normalize a date phrase into 'Month DD, YYYY'."""
    from datetime import datetime
    import re

    date_str = re.sub(r",\s*", ", ", date_str.strip())
    date_str = re.sub(r"\s+", " ", date_str)
    year_match = re.search(r"\d{4}", date_str)
    if not year_match and reference_year is not None:
        date_str = f"{date_str}, {reference_year}"

    formats = ["%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b %d %Y"]
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime("%B %d, %Y")
        except ValueError:
            continue
    return None


def parse_booking_dates_from_text(text: str) -> str | None:
    """Extract booking dates from natural user text when the LLM does not provide them."""
    import re
    from datetime import datetime

    months = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    date_token = fr"(?P<date>{months} \d{{1,2}}(?:,?\s*\d{{4}})?)"
    check_in_re = fr"check(?:[- ]?in)\s+{date_token}"
    check_out_re = fr"check(?:[- ]?out)\s+{date_token}"

    in_match = re.search(check_in_re, text, re.IGNORECASE)
    out_match = re.search(check_out_re, text, re.IGNORECASE)

    if in_match and out_match:
        check_in_raw = in_match.group("date")
        check_out_raw = out_match.group("date")
        year_match = re.search(r"\d{4}", check_out_raw)
        reference_year = int(year_match.group(0)) if year_match else datetime.now().year
        check_in_norm = normalize_date_string(check_in_raw, reference_year)
        check_out_norm = normalize_date_string(check_out_raw, reference_year)
        if check_in_norm and check_out_norm:
            return f"{check_in_norm} to {check_out_norm}"

    # Fallback for patterns like "May 15 to May 17, 2026"
    fallback_pattern = fr"({months} \d{{1,2}}(?:,?\s*\d{{4}})?)\s*(?:to|-)\s*({months} \d{{1,2}}(?:,?\s*\d{{4}})?)"
    fallback_match = re.search(fallback_pattern, text, re.IGNORECASE)
    if fallback_match:
        start_raw = fallback_match.group(1)
        end_raw = fallback_match.group(2)
        year_match = re.search(r"\d{4}", end_raw) or re.search(r"\d{4}", start_raw)
        reference_year = int(year_match.group(0)) if year_match else datetime.now().year
        start_norm = normalize_date_string(start_raw, reference_year)
        end_norm = normalize_date_string(end_raw, reference_year)
        if start_norm and end_norm:
            return f"{start_norm} to {end_norm}"
        if year_match:
            return f"{start_raw} to {end_raw}"

    numeric_match = re.search(r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})\s*(?:to|-)\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})", text, re.IGNORECASE)
    if numeric_match:
        return f"{numeric_match.group(1)} to {numeric_match.group(2)}"

    return None


def router_node(state):
    last_message = ""
    if state and state.get("messages"):
        last = state["messages"][-1]
        if isinstance(last, tuple) and len(last) >= 2:
            last_message = str(last[1])
        elif hasattr(last, "content"):
            last_message = str(last.content)
        else:
            last_message = str(last)

    text = last_message.lower().strip()
    if any(word in text for word in ["book", "reserve", "booking", "confirm"]):
        return {"next_node": "booker"}
    if any(word in text for word in ["plan", "itinerary", "trip", "day", "duration", "stay"]):
        return {"next_node": "planner"}
    if any(word in text for word in ["hi", "hello", "thanks", "thank you", "thankyou", "help"]):
        return {"next_node": "smalltalk"}
    if any(word in text for word in ["compare", "recommend", "best", "price", "budget", "pool", "wifi", "resort", "search"]):
        return {"next_node": "researcher"}
    return {"next_node": "smalltalk"}

async def smalltalk_node(state):
    latest = next((extract_content(msg.content).strip().lower() for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "")
    if latest in {"thanks", "thank you", "thankyou"}: content = "You're welcome. I can also help you compare resorts, plan an itinerary, or place a booking request."
    elif "help" in latest or "what can you do" in latest: content = "I can help you find resorts in Dandeli, compare options by budget and rating, plan a trip, and place a booking request."
    else: content = "Hi! I can help you find resorts in Dandeli, plan a trip, compare options, or place a booking request. Tell me your budget, group size, dates, or the kind of stay you want."
    return {"messages": [AIMessage(content=content, name="SmallTalk")]}


async def out_of_scope_node(state):
    return {
        "messages": [
            AIMessage(
                content="I can help with Dandeli resorts, pricing, trip planning, activities, and booking requests. "
                        "For questions outside those topics, please ask about resorts, travel options, or booking details.",
                name="OutOfScope",
            )
        ]
    }


async def researcher_node(state):
    latest = next((extract_content(msg.content) for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "")
    if not latest:
        content = "No user query was available for resort research."
        return {"response": content, "messages": [AIMessage(content=content, name="Researcher")]}
        
    try:
        research_context = await search_resorts.ainvoke(resolve_resort_followup_query(state["messages"], latest))
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Resort search error in researcher_node: {e}", exc_info=True)
        content = "I could not complete the resort research right now. Please try again."
        return {"response": content, "messages": [AIMessage(content=content, name="Researcher")]}
    
    # Validate that we got actual resort data
    if not research_context or not research_context.strip():
        content = "No resort data was retrieved. Please try a different search or adjust your filters."
        return {"response": content, "messages": [AIMessage(content=content, name="Researcher")]}
    
    from .llms import groq_llm, groq_70b, gemini_llm, prefer_groq_invoke
    
    # Parse JSON to check if we have actual results
    try:
        research_data = json.loads(research_context)
        top_results = research_data.get("top_results", [])
        
        # If search returned error status with no results, provide helpful feedback
        if not top_results and "Error" in research_data.get("status", ""):
            content = f"I encountered an issue searching for resorts: {research_data.get('status')}. Please try a different search or check back shortly."
            return {"response": content, "messages": [AIMessage(content=content, name="Researcher")]}
    except (json.JSONDecodeError, TypeError) as e:
        content = "I received invalid search results. Please try your search again."
        return {"response": content, "messages": [AIMessage(content=content, name="Researcher")]}
    
    synthesizer = prefer_groq_invoke(groq_70b, prefer_groq_invoke(groq_llm, gemini_llm))
    
    system_prompt = (
        "You are WayFind, a helpful Dandeli Travel Assistant. You will receive raw JSON search results from our database. "
        "Your job is to read the JSON data and answer the user's latest question in a beautiful, natural, conversational format. "
        "Make answers easy and enjoyable to scan. Avoid long paragraphs. Use short sections, bullets, and bold labels. "
        "For comparison questions, use this exact style:\n"
        "**Quick Verdict:** one punchy sentence naming the best pick for the user's likely need.\n"
        "**Snapshot:**\n"
        "- **Price:** Resort A ... | Resort B ...\n"
        "- **Rating:** Resort A ... | Resort B ...\n"
        "- **Best for:** Resort A ... | Resort B ...\n"
        "**Resort A:** 2-4 bullets with strongest facts.\n"
        "**Resort B:** 2-4 bullets with strongest facts.\n"
        "**My Pick:** Give a practical recommendation and mention the tradeoff.\n"
        "For list or recommendation answers, use this exact style:\n"
        "**Top Picks:** one short sentence explaining the list.\n"
        "**1. Resort Name**\n"
        "- **Price:** exact price from data\n"
        "- **Rating:** exact rating from data\n"
        "- **Best for:** one short phrase\n"
        "- **Contact:** phone/email/website if available\n"
        "- **Why choose it:** one short practical reason\n"
        "Repeat for each resort requested, then end with **My Pick:** one practical recommendation. "
        "For non-comparison answers, use a heading, then 3-6 crisp bullets, then a short recommendation when useful. "
        "Never put an entire resort description into one long bullet. Keep each bullet under 22 words when possible. "
        "For SPECIFIC QUESTIONS about a resort's features, answer with CLEAR YES/NO statements: "
        "  - If user asks 'does this resort have non-veg food?', check 'food_options' field and answer directly: 'Yes, Bison River Resort offers both Veg and Non-Veg food options.' "
        "  - If user asks 'what activities does this resort have?', list both 'activities_onsite' and 'activities_nearby' clearly. "
        "  - If user asks 'what amenities' or 'what facilities', list the 'amenities' field clearly. "
        "  - If user asks about rooms, list the 'rooms' field. "
        "  - If user asks about water activities, list 'water_activities' field. "
        "If the user asks for a comparison, logically compare the best options from the JSON using the structured comparison style above. "
        "If the user asks for a specific number of resorts (e.g. 'top 1' or 'just 2'), provide EXACTLY that many. "
        "If the user asks for contact information (phone, email, website), include it prominently in your response. "
        "If the JSON says no resorts were found, apologize and ask them to adjust their budget or requirements. "
        "If the user's question is unrelated to Dandeli resorts, activities, pricing, bookings, or trip planning, say that you can only help with Dandeli travel and resort-related questions. "
        "Do not say 'The JSON data provided...' or otherwise mention internal data availability. "
        "Do not invent details not in the search results. Always cite exact data from the JSON.\n\n"
        f"Search Results JSON:\n{research_context}"
    )
    
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])[-2:]
    try:
        result = await synthesizer.ainvoke(messages)
        content = extract_content(getattr(result, "content", str(result)))
    except Exception:
        content = "I found some resort data, but I couldn't generate a detailed answer right now. Please try again later."

    return {"response": content, "messages": [AIMessage(content=content, name="Researcher")]}


async def planner_node(state):
    latest = next((extract_content(msg.content) for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "")
    try:
        research_context = await search_resorts.ainvoke(latest) if latest else ""
    except Exception:
        research_context = ""

    if not latest:
        content = "Please tell me what kind of Dandeli stay you want, including budget, travelers, activities, or resort preferences."
        return {"response": content, "messages": [AIMessage(content=content, name="Planner")]}
    if not research_context.strip() or "No exact matching resorts found" in research_context:
        content = "I could not find verified resort details for that request. Please share your budget, dates, or preferred resort so I can plan accurately."
        return {"response": content, "messages": [AIMessage(content=content, name="Planner")]}
    from datetime import datetime
    today_date = datetime.now().strftime("%B %d, %Y")
    planner_context = f"Today is {today_date}. Use this JSON resort data as the factual grounding for the itinerary. DO NOT expose JSON to the user, write naturally.\n\n{research_context}"
    try:
        result = await planner_agent.ainvoke({"messages": [SystemMessage(content=planner_prompt), SystemMessage(content=planner_context)] + list(state["messages"])[-1:]})
        content = extract_content(result["messages"][-1].content)
    except Exception:
        content = "I can help plan your Dandeli trip. Consider riverside rafting, guided nature walks, pool time, and a relaxed evening meal at the resort."
    return {"response": content, "messages": [AIMessage(content=content, name="Planner")]}


async def booker_node(state):
    booking_messages = current_booking_context(state["messages"])
    latest_user_text = next((extract_content(msg.content).strip().lower() for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "")
    if any(marker in latest_user_text for marker in ["compare", " vs ", " versus ", "suggest", "recommend", "better price", "best price", "change the resort", "change resort", "different resort"]):
        content = "I still have your booking draft saved. For comparing or changing resorts, ask the resort question directly and I will keep the draft separate until you confirm a new resort."
        return {"response": content, "messages": [AIMessage(content=content, name="Booker")]}
    
    from .llms import gemini_llm, groq_llm, groq_70b, prefer_groq_invoke
    
    groq_70b_extractor = groq_70b.with_structured_output(BookingExtraction)
    groq_8b_extractor = groq_llm.with_structured_output(BookingExtraction)
    gemini_extractor = gemini_llm.with_structured_output(BookingExtraction)
    
    from datetime import datetime
    today_date = datetime.now().strftime("%B %d, %Y")
    
    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", f"Today is {today_date}. Extract booking details from the conversation. IMPORTANT: Convert all relative dates (like 'tomorrow' or 'next Friday') into exact absolute calendar dates. REJECT and return None for check-in dates that are today or in the past - they must be FUTURE dates only. Do NOT accept bookings for past or today. If a value is missing or unclear, set it to None. Intent must be exactly one of: check_status, cancel, book, unknown. If the latest user message asks to compare resorts, asks for recommendations, asks for better price, or says to change resort without explicitly naming a new resort to book, intent must be unknown and you must not combine two resort names into one resort_name."),
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
        content = "I'm having trouble parsing your booking details. Could you please specify the resort and dates again?"
        return {"response": content, "messages": [AIMessage(content=content, name="Booker")]}

    if data.intent == "check_status":
        if data.booking_id:
            response_text = await get_booking_status.ainvoke({"booking_id": data.booking_id})
            return {"response": response_text, "messages": [AIMessage(content=response_text, name="Booker")]}
        response_text = "Send your booking ID, for example `BK-0001`, and I will check the latest status."
        return {"response": response_text, "messages": [AIMessage(content=response_text, name="Booker")]}
        
    if data.intent == "cancel":
        base_reply = "Okay, I cancelled this booking request draft.\n\nIf you want to start a new one, tell me the resort and dates."
        return {"response": base_reply, "messages": [AIMessage(content=base_reply, name="Booker")]}

    if not data.dates:
        booking_text = "\n".join(str(msg.content) for msg in booking_messages if isinstance(msg, HumanMessage))
        parsed_dates = parse_booking_dates_from_text(booking_text)
        if parsed_dates:
            data.dates = parsed_dates
        else:
            content = "Before I place the booking request, send your exact check-in and check-out dates, for example `March 26, 2026 to March 28, 2026`."
            return {"response": content, "messages": [AIMessage(content=content, name="Booker")]}
    
    # Validate booking dates
    from datetime import datetime
    date_validation = validate_booking_dates(data.dates)
    if not date_validation["valid"]:
        content = f"I cannot accept this booking: {date_validation['error']}\n\nPlease provide future dates. For example, if today is {today_date}, you can book from tomorrow onwards."
        return {"response": content, "messages": [AIMessage(content=content, name="Booker")]}
    
    if not data.resort_name:
        content = "Tell me which resort you want to book, and I will place the request."
        return {"response": content, "messages": [AIMessage(content=content, name="Booker")]}
    if not data.contact:
        content = "Before I place the booking request, send your contact number or email so the resort owner can reach you."
        return {"response": content, "messages": [AIMessage(content=content, name="Booker")]}
    if not data.guests:
        content = "Please tell me how many guests will be staying, and if there are any children."
        return {"response": content, "messages": [AIMessage(content=content, name="Booker")]}
        
    from .booking_helpers import booking_confirmed
    if not booking_confirmed(booking_messages):
        content = f"Please confirm this booking:\nResort: {data.resort_name}\nDates: {data.dates}\nGuests: {data.guests}\nContact: {data.contact}\n\nReply `confirm` to send it."
        return {"response": content, "messages": [AIMessage(content=content, name="Booker")]}
        
    response_text = await book_resort.ainvoke({"resort_name": data.resort_name, "check_in_out_dates": data.dates, "guest_details": data.guests, "customer_contact": data.contact})
    return {"response": response_text, "messages": [AIMessage(content=response_text, name="Booker")]}
