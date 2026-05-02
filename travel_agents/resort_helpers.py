import re
from typing import Sequence

from langchain_core.messages import AIMessage, HumanMessage

from .content import extract_content
from travel_tools.search_tool import get_known_resort_names


def find_selected_resort(messages: Sequence) -> str | None:
    lowered_map = {name.lower(): name for name in get_known_resort_names()}
    
    def get_dist_words(name: str) -> set[str]:
        words = set(name.lower().split())
        return words - {"resort", "camp", "stay", "retreat", "jungle", "homestay", "hotel", "eco", "nature", "and", "the", "in", "of"}
        
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            lowered_content = extract_content(msg.content).strip().lower()
            
            if lowered_content in lowered_map:
                return lowered_map[lowered_content]
                
            for lowered_name, original_name in lowered_map.items():
                if lowered_name in lowered_content:
                    return original_name
                    
            best_fuzzy_match = None
            best_fuzzy_score = 0
            content_words = set(lowered_content.split())
            
            for lowered_name, original_name in lowered_map.items():
                dist_words = get_dist_words(lowered_name)
                if not dist_words:
                    continue
                overlap = dist_words.intersection(content_words)
                if len(overlap) >= max(1, len(dist_words) // 2):
                    if any(len(w) >= 4 for w in overlap) or len(overlap) == len(dist_words):
                        score = len(overlap)
                        if score > best_fuzzy_score:
                            best_fuzzy_score = score
                            best_fuzzy_match = original_name
                            
            if best_fuzzy_match:
                return best_fuzzy_match
    return None


def find_last_recommended_resort(messages: Sequence) -> str | None:
    patterns = [r"recommend staying at the \*\*(.+?)\*\*", r"Best choice:\s*(.+)", r"Second-best backup:\s*(.+)", r"^\d+\.\s+(.+)$"]
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = extract_content(msg.content)
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            for pattern in patterns[:3]:
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    return match.group(1).strip().strip("*")
            for line in lines:
                match = re.match(patterns[3], line)
                if match:
                    return match.group(1).strip()
    return None


def resolve_resort_followup_query(messages: Sequence, latest_user_query: str) -> str:
    normalized_query = " ".join(latest_user_query.lower().split())
    markers = ["this resort", "this one", "that resort", "that one", "its website", "its phone", "its email", "its location", "its price", "its rating", "website link", "website of", "phone number", "contact number", "email address", "tell me more", "more about", "details about", "book this", "book it"]
    if not any(marker in normalized_query for marker in markers):
        return latest_user_query
    resort_name = find_selected_resort(messages) or find_last_recommended_resort(messages)
    if not resort_name or resort_name.lower() in normalized_query:
        return latest_user_query
    rewritten = latest_user_query.strip()
    for source in ["this resort", "this one", "that resort", "that one"]:
        rewritten = re.sub(rf"\b{source}\b", resort_name, rewritten, flags=re.IGNORECASE)
    rewritten = re.sub(r"\bits\b", f"{resort_name}'s", rewritten, flags=re.IGNORECASE)
    return rewritten if rewritten != latest_user_query.strip() else f"{latest_user_query.strip()} {resort_name}".strip()
