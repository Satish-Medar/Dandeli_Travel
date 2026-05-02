from langchain_core.tools import tool

from .search_engine import (
    clean_text,
    dedupe_documents,
    extract_filters,
    find_named_resort,
    format_compound_best_detail_response,
    format_recommendation_summary,
    format_results,
    format_single_resort_detail,
    format_single_resort_field_response,
    hybrid_retrieve_documents,
    is_compound_best_detail_query,
    is_recommendation_query,
    is_single_resort_field_query,
    is_single_resort_followup_query,
    load_all_documents,
    matches_filters,
    normalize_text,
    sort_documents_by_best_to_worst,
    sort_documents_for_query,
    wants_best_first_sort,
)



def get_known_resort_names() -> list[str]:
    return [str(doc["metadata"].get("name")) for doc in load_all_documents() if doc["metadata"].get("name")]


def _find_close_alternatives(all_docs: list[dict], filters: dict, query: str) -> list[dict]:
    relaxed_filters = {k: v for k, v in filters.items() if k not in {"price", "total_budget"}}
    return sort_documents_for_query([doc for doc in all_docs if matches_filters(doc, relaxed_filters)], query)


@tool
def search_resorts(query: str) -> str:
    """Search Dandeli resorts by rating, price, category, amenities, and traveler needs."""
    from .vectorstore_provider import vectorstore
    if not vectorstore:
        return "Resort database unavailable. Please rebuild the index."
    normalized_query, (filters, semantic_query), all_docs = normalize_text(query), extract_filters(query), load_all_documents()
    guest_count, total_budget, named_resort = filters.get("guest_count"), filters.get("total_budget"), find_named_resort(query, all_docs)
    if named_resort and is_single_resort_field_query(normalized_query):
        field_response = format_single_resort_field_response(named_resort, normalized_query)
        if field_response: return field_response
    if named_resort and is_single_resort_followup_query(normalized_query):
        return format_single_resort_detail(named_resort, guest_count=guest_count)
    docs = [doc for doc in all_docs if matches_filters(doc, filters)] if filters else hybrid_retrieve_documents(query, all_docs)
    docs = sort_documents_for_query(docs, semantic_query or query) if (docs and filters) else (docs or sort_documents_for_query(all_docs, query))
    if any(marker in normalized_query for marker in ["expensive", "luxury", "premium", "high-end", "rich"]):
        docs = sorted(docs, key=lambda d: (-(d["metadata"].get("price", 0) or 0), -(d["metadata"].get("rating", 0) or 0), d["metadata"].get("name", "")))
    if wants_best_first_sort(normalized_query):
        docs = sort_documents_by_best_to_worst(docs)
    if not docs:
        if filters and "price" in filters:
            relaxed_docs = _find_close_alternatives(all_docs, filters, semantic_query or query)
            prefix = f"No exact resorts found within a total budget of {total_budget} INR per night for {guest_count} guests. That works out to about {filters['price'][1]} INR per person.\n\n" if total_budget and guest_count else "No exact resorts found within the stated budget.\n\n"
            return prefix + "Closest alternatives:\n\n" + format_results(relaxed_docs[:3], guest_count=guest_count) if relaxed_docs else "No matching resorts found."
        return "No matching resorts found."
    if is_compound_best_detail_query(normalized_query):
        return format_compound_best_detail_response(docs, query, guest_count=guest_count, total_budget=total_budget)
    if named_resort:
        exact_match_docs = [doc for doc in docs if normalize_text(str(doc["metadata"].get("name", ""))) == normalize_text(str(named_resort["metadata"].get("name", "")))]
        if exact_match_docs:
            return format_single_resort_field_response(exact_match_docs[0], normalized_query) or format_single_resort_detail(exact_match_docs[0], guest_count=guest_count)
    if is_recommendation_query(normalized_query):
        return format_recommendation_summary(docs[:5], query, guest_count=guest_count, total_budget=total_budget)
    return format_results(docs[:8], guest_count=guest_count)
