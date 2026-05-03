import json
from langchain_core.tools import tool

from .search_engine import extract_filters_async, retrieve_matching_resorts, load_all_documents

def get_known_resort_names() -> list[str]:
    return [str(doc["metadata"].get("name")) for doc in load_all_documents() if doc["metadata"].get("name")]

@tool
async def search_resorts(query: str) -> str:
    """Search Dandeli resorts by rating, price, category, amenities, and traveler needs."""
    try:
        filters = await extract_filters_async(query)
        matching_docs = await retrieve_matching_resorts(query, filters)
        
        if not matching_docs:
            return json.dumps({
                "status": "No exact matching resorts found.",
                "applied_filters": filters.model_dump()
            })
            
        # Format the top matching documents as a clean JSON-like string
        results = []
        for doc in matching_docs[:10]:  # Pass top 10 matches to the LLM
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
                "details": doc["page_content"]
            })
            
        return json.dumps({
            "status": f"Found {len(matching_docs)} matching resorts.",
            "applied_filters": filters.model_dump(),
            "top_results": results
        }, indent=2)
        
    except Exception as e:
        print(f"Search tool error: {e}")
        return json.dumps({"status": f"Error executing search: {str(e)}"})
