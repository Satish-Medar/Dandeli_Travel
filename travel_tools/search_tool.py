# Formats resort search results and fallback responses for the LLM-driven travel assistant.
# File: travel_tools/search_tool.py


import json
import logging
from typing import Optional
from langchain_core.tools import tool

from .search_engine import SearchFilters, extract_filters_async, filter_resorts, retrieve_matching_resorts, load_all_documents

logger = logging.getLogger(__name__)

def get_known_resort_names() -> list[str]:
    return [str(doc["metadata"].get("name")) for doc in load_all_documents() if doc["metadata"].get("name")]


def _build_search_result(doc: dict) -> dict:
    meta = doc["metadata"]
    return {
        "name": meta.get("name"),
        "category": meta.get("category"),
        "location": meta.get("location"),
        "price": meta.get("price"),
        "price_per_person": meta.get("price"),
        "rating": meta.get("rating"),
        "family_friendly": meta.get("family_friendly"),
        "romantic_couples": meta.get("romantic_couples"),
        "contact_phone": meta.get("phone"),
        "contact_email": meta.get("email"),
        "website": meta.get("website"),
        "details": doc["page_content"]
    }


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


def find_resort_by_name(resort_name: str) -> dict | None:
    """Try to find a resort by exact or partial name match."""
    all_docs = load_all_documents()
    search_name = resort_name.lower().strip()
    
    # Remove common suffixes for matching
    suffixes = [" resort", " camp", " stay", " retreat", " lodge", " hotel", " jungle", " nature"]
    search_name_normalized = search_name
    for suffix in suffixes:
        if search_name_normalized.endswith(suffix):
            search_name_normalized = search_name_normalized[:-len(suffix)].strip()
    
    logger.info(f"Searching for resort: '{resort_name}' -> normalized: '{search_name_normalized}'")
    
    # First try exact match
    for doc in all_docs:
        resort_name_normalized = doc["metadata"].get("name", "").lower().strip()
        resort_name_original = resort_name_normalized
        for suffix in suffixes:
            if resort_name_normalized.endswith(suffix):
                resort_name_normalized = resort_name_normalized[:-len(suffix)].strip()
        
        if resort_name_normalized == search_name_normalized:
            logger.info(f"Found exact match: '{doc['metadata'].get('name')}'")
            return _build_search_result(doc)
    
    # Then try partial match
    for doc in all_docs:
        resort_name_in_doc = doc["metadata"].get("name", "").lower().strip()
        if search_name_normalized in resort_name_in_doc or resort_name_in_doc in search_name_normalized:
            logger.info(f"Found partial match: '{doc['metadata'].get('name')}' (search_term: '{search_name_normalized}')")
            return _build_search_result(doc)
    
    logger.warning(f"Resort '{resort_name}' not found. Available resorts: {[doc['metadata'].get('name') for doc in all_docs[:5]]}")
    return None

@tool
async def search_resorts_tool(query: str) -> str:
    """Search Dandeli resorts by rating, price, category, amenities, and traveler needs."""
    try:
        filters = await extract_filters_async(query)
        
        # If user asked for specific resorts by name, try direct lookup first
        if filters.target_resort_names:
            matching_docs = []
            for target_name in filters.target_resort_names:
                found_doc = find_resort_by_name(target_name)
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