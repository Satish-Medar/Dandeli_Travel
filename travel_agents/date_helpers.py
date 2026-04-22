import re
from datetime import datetime, timedelta
from typing import Sequence

from langchain_core.messages import HumanMessage
from .content import extract_content

def find_explicit_booking_dates(messages: Sequence) -> str | None:
    month = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    num = r"\d{1,2}(?:st|nd|rd|th)?"
    
    pattern = re.compile(rf"\b(?:{month}\s+{num}(?:,\s*\d{{4}})?|{num}\s+(?:of\s+)?{month}(?:\s+\d{{4}})?|\d{{4}}-\d{{2}}-\d{{2}}|\d{{1,2}}\s*[/-]\s*\d{{1,2}}\s*[/-]\s*\d{{2,4}})\b", re.IGNORECASE)
    fallback_day = re.compile(rf"\b(?<!\d){num}\b", re.IGNORECASE)
    
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = extract_content(msg.content)
            matches = [m.group(0).strip() for m in pattern.finditer(content)]
            if len(matches) == 1:
                parts = content.lower().split(matches[0].lower(), 1)
                if len(parts) == 2:
                    second_day = fallback_day.search(parts[1])
                    if second_day:
                         matches.append(second_day.group(0).strip() + f" {matches[0][-4:] if matches[0][-4:].isdigit() else '2026'}")
            
            if len(matches) >= 2:
                return f"{matches[0]} to {matches[1]}"
    return None


def find_relative_booking_dates(messages: Sequence) -> str | None:
    now = datetime.now()
    tomorrow_pattern = re.compile(r"tom(?:orrow|morow|morow|morrow)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)?", re.IGNORECASE)
    day_after_pattern = re.compile(r"(?:day after tomorrow|day after tom(?:orrow|morow|morow|morrow))\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)?", re.IGNORECASE)
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = extract_content(msg.content)
            tomorrow_match = tomorrow_pattern.search(content)
            day_after_match = day_after_pattern.search(content)
            if tomorrow_match and day_after_match:
                return f"{_format_relative_datetime(now + timedelta(days=1), tomorrow_match.group(1))} to {_format_relative_datetime(now + timedelta(days=2), day_after_match.group(1))}"
    return None


def _format_relative_datetime(base_date: datetime, time_fragment: str | None) -> str:
    if time_fragment:
        time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", time_fragment.strip().lower().replace(".", ""))
        if time_match:
            hour, minute, meridiem = int(time_match.group(1)), int(time_match.group(2) or 0), time_match.group(3)
            hour = hour + 12 if meridiem == "pm" and hour != 12 else 0 if meridiem == "am" and hour == 12 else hour
            base_date = base_date.replace(hour=hour, minute=minute)
    return base_date.strftime("%B %d, %Y %I:%M %p")
