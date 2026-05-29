# Formats resort search results and fallback responses for the LLM-driven travel assistant.
# File: travel_tools/search_tool.py

# Simple overview:
# - This module wraps search functionality so the assistant can ask for resorts.
# - It converts raw resort documents into structured results and handles
#   fallback responses when the search fails.


import json
import logging
import re
from typing import Optional
from langchain_core.tools import tool

from .search_engine import SearchFilters, extract_filters_async, filter_resorts, retrieve_matching_resorts, load_all_documents

logger = logging.getLogger(__name__)

# Return a list of resort names known by the search database.
# Used for fallback messages when a requested resort is not found.
def get_known_resort_names() -> list[str]:
    return [str(doc["metadata"].get("name")) for doc in load_all_documents() if doc["metadata"].get("name")]


# Convert an internal resort document into a simple result object.
def _build_search_result(doc: dict) -> dict:
    meta = doc["metadata"]
    return {
        "name": meta.get("name"),
        "category": meta.get("category"),
        "city": meta.get("city"),
        "location": meta.get("location"),
        "latitude": meta.get("latitude"),
        "longitude": meta.get("longitude"),
        "price": meta.get("price"),
        "price_per_person": meta.get("price"),
        "rating": meta.get("rating"),
        "review_count": meta.get("review_count"),
        "family_friendly": meta.get("family_friendly"),
        "romantic_couples": meta.get("romantic_couples"),
        "contact_phone": meta.get("phone"),
        "contact_email": meta.get("email"),
        "website": meta.get("website"),
        "check_in": meta.get("check_in"),
        "check_out": meta.get("check_out"),
        "rooms": meta.get("rooms", []),
        "amenities": meta.get("amenities", []),
        "activities_onsite": meta.get("activities_onsite", []),
        "activities_nearby": meta.get("activities_nearby", []),
        "water_activities": meta.get("water_activities", []),
        "food_options": meta.get("food_options", []),
        "available_rooms": meta.get("available_rooms"),
        "occupied_rooms": meta.get("occupied_rooms"),
        "special_offer": meta.get("special_offer"),
        "availability_status": meta.get("availability_status"),
        "details": doc["page_content"]
    }


def _normalize_resort_name(value: str) -> str:
    normalized = str(value or "").lower().strip()
    suffixes = [" resort", " camp", " stay", " retreat", " lodge", " hotel", " jungle", " nature"]
    for suffix in suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
    return normalized


def _distinctive_name_tokens(value: str) -> set[str]:
    generic_tokens = {
        "resort",
        "camp",
        "stay",
        "retreat",
        "lodge",
        "hotel",
        "jungle",
        "nature",
        "eco",
        "river",
        "riverside",
        "forest",
        "dandeli",
        "the",
        "and",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9]+", str(value or "").lower())
        if len(token) >= 4 and token not in generic_tokens
    }


def _find_resort_document_by_name(resort_name: str) -> dict | None:
    all_docs = load_all_documents()
    search_name_normalized = _normalize_resort_name(resort_name)

    for doc in all_docs:
        resort_name_normalized = _normalize_resort_name(doc["metadata"].get("name", ""))
        if resort_name_normalized == search_name_normalized:
            return doc

    for doc in all_docs:
        doc_name = str(doc["metadata"].get("name", "")).lower().strip()
        if search_name_normalized in doc_name or _normalize_resort_name(doc_name) in search_name_normalized:
            return doc

    return None


def _find_resort_documents_mentioned_in_query(query: str) -> list[dict]:
    query_normalized = str(query or "").lower()
    query_tokens = set(re.findall(r"[a-z0-9]+", query_normalized))
    all_docs = load_all_documents()

    full_name_matches = []
    seen = set()
    for doc in all_docs:
        name = str(doc["metadata"].get("name") or "").strip()
        if not name:
            continue
        name_lower = name.lower()
        if name_lower in query_normalized:
            key = str(doc["metadata"].get("id") or name_lower)
            if key not in seen:
                full_name_matches.append(doc)
                seen.add(key)
    if full_name_matches:
        return full_name_matches

    matches = []
    seen = set()
    for doc in all_docs:
        name = str(doc["metadata"].get("name") or "").strip()
        if not name:
            continue
        name_lower = name.lower()
        distinctive_tokens = _distinctive_name_tokens(name)
        has_distinctive_name = bool(distinctive_tokens) and distinctive_tokens.issubset(query_tokens)
        if has_distinctive_name:
            key = str(doc["metadata"].get("id") or name_lower)
            if key not in seen:
                matches.append(doc)
                seen.add(key)
    return matches


# Synchronous helper for searching resorts.
# This is useful for tests and for code paths that do not use the full LLM tool.
def search_resorts(query: str, filters: Optional[SearchFilters] = None) -> list[dict]:
    """Search resorts synchronously for direct unit testing and helper usage."""
    if filters is None:
        filters = SearchFilters()

    all_docs = load_all_documents()

    if filters.target_resort_names:
        matching_docs = []
        for target_name in filters.target_resort_names:
            found_doc = find_resort_by_name(target_name)
            if found_doc:
                matching_docs.append(found_doc)
        if matching_docs:
            results = []
            for doc in matching_docs[:5]:
                if isinstance(doc, dict) and "metadata" in doc:
                    results.append(_build_search_result(doc))
                else:
                    results.append(doc)
            return results

    filtered_docs = filter_resorts(all_docs, filters)
    return [_build_search_result(doc) for doc in filtered_docs[:5]]


# Try to find a resort by exact or partial name match.
# This helps the assistant when users name a resort directly.
def find_resort_by_name(resort_name: str) -> dict | None:
    """Try to find a resort by exact or partial name match."""
    doc = _find_resort_document_by_name(resort_name)
    if doc:
        logger.info(f"Found resort match: '{doc['metadata'].get('name')}'")
        return _build_search_result(doc)

    logger.warning(f"Resort '{resort_name}' not found. Available resorts: {get_known_resort_names()[:5]}")
    return None

# LLM tool wrapper for searching resorts.
# Returns a JSON string so the assistant can read structured results.
@tool
async def search_resorts_tool(query: str) -> str:
    """Search Dandeli resorts by rating, price, category, amenities, and traveler needs."""
    try:
        direct_name_matches = _find_resort_documents_mentioned_in_query(query)
        if direct_name_matches:
            results = []
            for doc in direct_name_matches[:5]:
                meta = doc["metadata"]
                results.append({
                    "name": meta.get("name"),
                    "category": meta.get("category"),
                    "location": meta.get("location"),
                    "price_per_person": meta.get("price"),
                    "rating": meta.get("rating"),
                    "family_friendly": meta.get("family_friendly"),
                    "romantic_couples": meta.get("romantic_couples"),
                    "contact_phone": meta.get("phone"),
                    "contact_email": meta.get("email"),
                    "website": meta.get("website"),
                    "food_options": meta.get("food_options", []),
                    "rooms": meta.get("rooms", []),
                    "activities_onsite": meta.get("activities_onsite", []),
                    "activities_nearby": meta.get("activities_nearby", []),
                    "water_activities": meta.get("water_activities", []),
                    "amenities": meta.get("amenities", []),
                    "available_rooms": meta.get("available_rooms"),
                    "occupied_rooms": meta.get("occupied_rooms"),
                    "special_offer": meta.get("special_offer"),
                    "availability_status": meta.get("availability_status"),
                    "details": doc["page_content"]
                })
            return json.dumps({
                "status": f"Found {len(direct_name_matches)} matching resort by name.",
                "applied_filters": {"target_resort_names": [item["metadata"].get("name") for item in direct_name_matches]},
                "top_results": results
            }, indent=2)

        filters = await extract_filters_async(query)
        
        # If user asked for specific resorts by name, try direct lookup first
        if filters.target_resort_names:
            matching_docs = []
            for target_name in filters.target_resort_names:
                found_doc = _find_resort_document_by_name(target_name)
                if found_doc:
                    matching_docs.append(found_doc)
            
            # If we didn't find any by direct lookup, fall back to normal search
            if not matching_docs:
                matching_docs = await retrieve_matching_resorts(query, filters)
        else:
            matching_docs = await retrieve_matching_resorts(query, filters)
        
        if not matching_docs:
            # If we had target resort names, provide specific feedback
            if filters.target_resort_names:
                return json.dumps({
                    "status": f"Requested resorts not found in our database: {', '.join(filters.target_resort_names)}",
                    "available_resorts": get_known_resort_names()[:20]
                })
            return json.dumps({
                "status": "No exact matching resorts found.",
                "applied_filters": filters.model_dump()
            })
            
        # Format the top matching documents as a clean JSON-like string
        results = []
        for doc in matching_docs[:5]:  # Pass top 5 matches to the LLM (reduced to save tokens)
            meta = doc["metadata"]
            results.append({
                "name": meta.get("name"),
                "category": meta.get("category"),
                "location": meta.get("location"),
                "price_per_person": meta.get("price"),
                "rating": meta.get("rating"),
                "family_friendly": meta.get("family_friendly"),
                "romantic_couples": meta.get("romantic_couples"),
                "contact_phone": meta.get("phone"),
                "contact_email": meta.get("email"),
                "website": meta.get("website"),
                "food_options": meta.get("food_options", []),
                "rooms": meta.get("rooms", []),
                "activities_onsite": meta.get("activities_onsite", []),
                "activities_nearby": meta.get("activities_nearby", []),
                "water_activities": meta.get("water_activities", []),
                "amenities": meta.get("amenities", []),
                "details": doc["page_content"]
            })
            
        return json.dumps({
            "status": f"Found {len(matching_docs)} matching resorts.",
            "applied_filters": filters.model_dump(),
            "top_results": results
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Search tool error: {e}", exc_info=True)
        # Return fallback with local data to avoid empty responses
        fallback_docs = load_all_documents()
        fallback_results = []
        if fallback_docs:
            for doc in fallback_docs[:5]:
                meta = doc["metadata"]
                fallback_results.append({
                    "name": meta.get("name"),
                    "category": meta.get("category"),
                    "location": meta.get("location"),
                    "price_per_person": meta.get("price"),
                    "rating": meta.get("rating"),
                    "family_friendly": meta.get("family_friendly"),
                    "romantic_couples": meta.get("romantic_couples"),
                    "contact_phone": meta.get("phone"),
                    "contact_email": meta.get("email"),
                    "website": meta.get("website"),
                    "details": doc["page_content"]
                })
        return json.dumps({
            "status": f"Search encountered an error. Showing available resorts: {str(e)}",
            "applied_filters": filters.model_dump() if filters else {},
            "top_results": fallback_results
        })
