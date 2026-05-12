import json
import logging
import os
import re
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

from .vectorstore_provider import get_retriever, get_vectorstore

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
RESORT_DATA_PATH = BASE_DIR / "data" / "json_files" / "resorts.json"


def clean_text(value: str) -> str:
    if value is None: return ""
    replacements = {"Ã¢â‚¬â€œ": "-", "Ã¢â‚¬â€ ": "-", "Ã¢â‚¬â„¢": "'", "Ã¢â‚¬Ëœ": "'", "Ã¢â‚¬Å“": '"', "Ã¢â‚¬Â ": '"'}
    cleaned = str(value)
    for bad, good in replacements.items():
        cleaned = cleaned.replace(bad, good)
    return cleaned


class SearchFilters(BaseModel):
    min_rating: Optional[float] = Field(default=None, description="Minimum rating required by the user (1-5)")
    max_budget: Optional[int] = Field(default=None, description="Maximum total budget in INR. E.g. 'under 5000' -> 5000")
    guest_count: Optional[int] = Field(default=None, description="Number of guests traveling")
    family_friendly: Optional[bool] = Field(default=None, description="Whether the user explicitly wants family friendly options")
    target_resort_names: Optional[list[str]] = Field(default=None, description="If the user asks about specific resorts by name, extract all names here (e.g., for 'compare X, Y, and Z', extract ['X', 'Y', 'Z'])")
    required_amenities: Optional[list[str]] = Field(default=None, description="List of required amenities like 'swimming pool', 'wifi', 'restaurant', 'parking', etc. Only extract what user explicitly asks for.")
    required_activities: Optional[list[str]] = Field(default=None, description="List of required activities like 'jungle safari', 'river rafting', 'bird watching', etc.")
    budget_type: Optional[str] = Field(default="per_person", description="Whether budget is 'per_person' or 'total' for group")
    adventure_level: Optional[str] = Field(default=None, description="Adventure level: 'mild', 'moderate', 'extreme'")
    accommodation_type: Optional[str] = Field(default=None, description="Type of accommodation: 'cottage', 'tent', 'villa', etc.")


def _normalize_amenities(amenities):
    if not amenities:
        return []
    return [str(item).lower().strip() for item in amenities if isinstance(item, str)]


def _extract_amenities_from_content(content: str) -> list[str]:
    if not content:
        return []
    for line in content.splitlines():
        if line.lower().startswith("amenities:"):
            return _normalize_amenities(line.split(":", 1)[1].split(","))
    return []


def _matches_filters(resort: dict, filters: SearchFilters) -> bool:
    if not filters:
        return True

    # Support both raw resorts and LangChain doc metadata structures
    if "metadata" in resort:
        data = resort["metadata"]
    else:
        data = resort

    price = data.get("price") or 0
    rating = data.get("rating") or 0
    amenities = _normalize_amenities(data.get("amenities") or resort.get("amenities"))
    activities_onsite = _normalize_amenities(data.get("activities_onsite") or [])
    activities_nearby = _normalize_amenities(data.get("activities_nearby") or [])
    all_activities = activities_onsite + activities_nearby
    family = data.get("family_friendly")
    resort_name = str(data.get("name", "")).lower().strip()

    # Budget filtering with group calculation
    if filters.max_budget is not None and filters.guest_count:
        if filters.budget_type == "total":
            total_cost = price * filters.guest_count
            if total_cost > filters.max_budget:
                return False
        else:  # per_person budget
            if price > filters.max_budget:
                return False
    elif filters.max_budget is not None:
        if price > filters.max_budget:
            return False

    if filters.min_rating is not None:
        if rating < filters.min_rating:
            return False

    if filters.family_friendly is not None:
        if filters.family_friendly:
            if family is False:
                return False
        else:
            if family is True:
                return False

    # Enhanced amenity matching with fuzzy logic
    if filters.required_amenities:
        for required in filters.required_amenities:
            req_norm = str(required).lower().strip()
            found = False
            for amen in amenities:
                if req_norm in amen or amen in req_norm:
                    found = True
                    break
            if not found:
                return False

    # Activity matching
    if filters.required_activities:
        for required in filters.required_activities:
            req_norm = str(required).lower().strip()
            found = False
            for activity in all_activities:
                if req_norm in activity or activity in req_norm:
                    found = True
                    break
            if not found:
                return False

    if filters.target_resort_names:
        matches_name = False
        for target_name in filters.target_resort_names:
            target = str(target_name).lower().strip()
            if target in resort_name or resort_name in target:
                matches_name = True
                break
        if not matches_name:
            return False

    return True


def filter_resorts(resorts: list[dict], filters: SearchFilters) -> list[dict]:
    """Filter a list of resorts or resort docs by SearchFilters."""
    if not filters:
        return resorts
    return [resort for resort in resorts if _matches_filters(resort, filters)]


async def extract_filters_async(query: str) -> SearchFilters:
    from travel_agents.llms import groq_llm, groq_70b, gemini_llm, prefer_groq_invoke
    from langchain_core.prompts import ChatPromptTemplate
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract search constraints from the user query. If a constraint is not mentioned, set it to null/None."),
        ("human", "{query}")
    ])
    
    chain = prefer_groq_invoke(
        prompt | groq_70b.with_structured_output(SearchFilters),
        prefer_groq_invoke(
            prompt | groq_llm.with_structured_output(SearchFilters),
            prompt | gemini_llm.with_structured_output(SearchFilters)
        )
    )
    
    try:
        result = await chain.ainvoke({"query": query})
        return result
    except Exception as e:
        logger.error(f"Filter extraction failed: {e}")
        return SearchFilters()


def _load_local_documents() -> list[dict]:
    try:
        if not RESORT_DATA_PATH.exists(): return []
        with open(RESORT_DATA_PATH, encoding="utf-8-sig") as source:
            resorts = json.load(source)
    except Exception as error:
        logger.error(f"Failed to load local resort data: {error}")
        return []

    rows = []
    for resort in resorts:
        metadata = {
            "id": resort.get("id"),
            "name": clean_text(resort.get("name")),
            "category": clean_text(resort.get("category")),
            "city": clean_text(resort.get("city")),
            "location": clean_text(resort.get("location")),
            "price": resort.get("price"),
            "rating": resort.get("rating"),
            "family_friendly": bool(resort.get("family_friendly", False)),
            "romantic_couples": bool(resort.get("romantic_couples", False)),
            "amenities": _normalize_amenities(resort.get("amenities", [])),
            "phone": clean_text(resort.get("phone")),
            "email": clean_text(resort.get("email")),
            "website": clean_text(resort.get("website")),
        }
        
        content = (
            f"Resort Name: {metadata['name']}\n"
            f"Category: {metadata['category']}\n"
            f"Location: {metadata['location']}, {metadata['city']}\n"
            f"Description: {clean_text(resort.get('description'))}\n"
            f"Unique Features: {clean_text(resort.get('unique_features'))}\n"
            f"Amenities: {', '.join(map(str, resort.get('amenities', [])))}\n"
            f"Activities: {', '.join(map(str, resort.get('activities_onsite', []) + resort.get('activities_nearby', [])))}\n"
            f"Price: {metadata['price']} INR per day per person\n"
            f"Rating: {metadata['rating']} based on {resort.get('review_count', 'N/A')} reviews\n"
        )
        rows.append({"page_content": content, "metadata": metadata})
    return rows


_cached_all_docs = None

def load_all_documents() -> list[dict]:
    global _cached_all_docs
    if _cached_all_docs is not None:
        return _cached_all_docs

    vectorstore = get_vectorstore()
    if not vectorstore:
        _cached_all_docs = _load_local_documents()
        return _cached_all_docs

    try:
        # Retrieve a large number to cache locally
        docs = vectorstore.similarity_search("resort", k=100)
        rows, seen = [], set()
        for doc in docs:
            name = doc.metadata.get("name")
            if name and name not in seen:
                seen.add(name)
                rows.append({
                    "page_content": clean_text(doc.page_content),
                    "metadata": {k: clean_text(v) if isinstance(v, str) else v for k, v in doc.metadata.items()},
                })
        if not rows: return _load_local_documents()
        _cached_all_docs = rows
        return rows
    except Exception as e:
        logger.error(f"Failed to load documents from vector store: {e}")
        _cached_all_docs = _load_local_documents()
        return _cached_all_docs


async def retrieve_matching_resorts(query: str, filters: SearchFilters) -> list[dict]:
    all_docs = load_all_documents()
    
    # Apply hard filters first
    filtered_docs = []
    for doc in all_docs:
        meta = doc["metadata"]
        
        # Exact Name Match (if user specified target resort(s))
        if filters.target_resort_names:
            resort_name = str(meta.get("name", "")).lower().strip()
            suffixes = [" resort", " camp", " stay", " retreat", " lodge", " hotel"]
            
            # Remove suffixes from resort name for matching
            resort_name_normalized = resort_name
            for suffix in suffixes:
                if resort_name_normalized.endswith(suffix):
                    resort_name_normalized = resort_name_normalized[:-len(suffix)].strip()
            
            # Check if this resort matches any of the requested names
            found_match = False
            for target_name in filters.target_resort_names:
                query_name = target_name.lower().strip()
                # Remove suffixes from query name too
                for suffix in suffixes:
                    if query_name.endswith(suffix):
                        query_name = query_name[:-len(suffix)].strip()
                
                # Check for match (exact or partial)
                if query_name == resort_name_normalized or query_name in resort_name_normalized or resort_name_normalized in query_name:
                    found_match = True
                    break
            
            if not found_match:
                continue
                
        # Rating Filter
        if filters.min_rating is not None:
            if (meta.get("rating") or 0) < filters.min_rating:
                continue
                
        # Family Friendly Filter
        if filters.family_friendly:
            is_family = meta.get("family_friendly", False)
            if not is_family and "family-friendly" not in doc["page_content"].lower():
                continue
                
        # Price Filter
        if filters.max_budget is not None:
            guest_count = filters.guest_count or 1
            max_price_per_person = filters.max_budget / guest_count
            if (meta.get("price") or 100000) > max_price_per_person:
                continue
        
        # Amenities Filter
        if filters.required_amenities:
            resort_amenities = [a.lower().strip() for a in doc["page_content"].lower().split("amenities:")[-1].split("\n")[0].split(",") if a.strip()]
            if not resort_amenities:
                resort_amenities = [a.lower().strip() for a in doc.get("metadata", {}).get("amenities", [])]
            
            missing_amenity = False
            for required_amenity in filters.required_amenities:
                required_normalized = required_amenity.lower().strip()
                # Check if any resort amenity matches the requirement
                found = False
                for resort_amenity in resort_amenities:
                    if required_normalized in resort_amenity or resort_amenity in required_normalized:
                        found = True
                        break
                
                # Also check in page content directly
                if not found and required_normalized not in doc["page_content"].lower():
                    missing_amenity = True
                    break
            
            if missing_amenity:
                continue
                
        filtered_docs.append(doc)

    # If no filters or specific names, do semantic ranking
    if not filters.target_resort_names:
        retriever = get_retriever()
        semantic_docs = []
        if retriever:
            try:
                # Retriever might be sync, but langchain retrievers support ainvoke usually. 
                # SelfQueryRetriever does.
                retrieved = await retriever.ainvoke(query)
                retrieved_names = {d.metadata.get("name") for d in retrieved}
                # prioritize vector hits
                for doc in filtered_docs:
                    if doc["metadata"].get("name") in retrieved_names:
                        semantic_docs.append(doc)
            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                
        # Combine semantic hits first, then the rest of filtered docs
        final_docs = semantic_docs
        seen_names = {d["metadata"].get("name") for d in final_docs}
        for doc in filtered_docs:
            if doc["metadata"].get("name") not in seen_names:
                final_docs.append(doc)
        return final_docs
        
    return filtered_docs

