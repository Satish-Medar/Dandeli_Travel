import json
import os
import re
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

from .vectorstore_provider import get_retriever, get_vectorstore

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
    min_rating: Optional[float] = Field(description="Minimum rating required by the user (1-5)")
    max_budget: Optional[int] = Field(description="Maximum total budget in INR. E.g. 'under 5000' -> 5000")
    guest_count: Optional[int] = Field(description="Number of guests traveling")
    family_friendly: Optional[bool] = Field(description="Whether the user explicitly wants family friendly options")
    target_resort_name: Optional[str] = Field(description="If the user asks about a specific resort by name, extract the name here")


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
        print(f"Filter extraction failed: {e}")
        return SearchFilters()


def _load_local_documents() -> list[dict]:
    try:
        if not RESORT_DATA_PATH.exists(): return []
        with open(RESORT_DATA_PATH, encoding="utf-8-sig") as source:
            resorts = json.load(source)
    except Exception as error:
        print(f"Failed to load local resort data: {error}")
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
        print(f"Failed to load documents from vector store: {e}")
        _cached_all_docs = _load_local_documents()
        return _cached_all_docs


async def retrieve_matching_resorts(query: str, filters: SearchFilters) -> list[dict]:
    all_docs = load_all_documents()
    
    # Apply hard filters first
    filtered_docs = []
    for doc in all_docs:
        meta = doc["metadata"]
        
        # Exact Name Match (if user specified a target resort)
        if filters.target_resort_name:
            # Extract the core name without common suffixes like "resort", "camp", "stay", "retreat"
            query_name = filters.target_resort_name.lower().strip()
            suffixes = [" resort", " camp", " stay", " retreat", " lodge", " hotel"]
            for suffix in suffixes:
                if query_name.endswith(suffix):
                    query_name = query_name[:-len(suffix)].strip()
            
            resort_name = str(meta.get("name", "")).lower().strip()
            # Check if the core names match
            if query_name not in resort_name and resort_name not in query_name:
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
                
        filtered_docs.append(doc)

    # If no filters or specific name, do semantic ranking
    if not filters.target_resort_name:
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
                print(f"Vector search failed: {e}")
                
        # Combine semantic hits first, then the rest of filtered docs
        final_docs = semantic_docs
        seen_names = {d["metadata"].get("name") for d in final_docs}
        for doc in filtered_docs:
            if doc["metadata"].get("name") not in seen_names:
                final_docs.append(doc)
        return final_docs
        
    return filtered_docs

