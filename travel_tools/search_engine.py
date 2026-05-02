import re
from typing import Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from .vectorstore_provider import retriever, vectorstore

# ==========================================
# 1. TEXT UTILS
# ==========================================
def normalize_text(value: str) -> str:
    return " ".join(value.lower().split())

def clean_text(value: str) -> str:
    replacements = {
        "Ã¢â‚¬â€œ": "-",
        "Ã¢â‚¬â€ ": "-",
        "Ã¢â‚¬â„¢": "'",
        "Ã¢â‚¬Ëœ": "'",
        "Ã¢â‚¬Å“": '"',
        "Ã¢â‚¬Â ": '"',
    }
    cleaned = value
    for bad, good in replacements.items():
        cleaned = cleaned.replace(bad, good)
    return cleaned

def build_preview_text(value: str, limit: int = 220) -> str:
    cleaned = clean_text(value).strip()
    if len(cleaned) <= limit: return cleaned
    truncated = cleaned[:limit].rstrip(" ,;:-")
    last_space = truncated.rfind(" ")
    return truncated[:last_space] if last_space > 0 else truncated

def extract_labeled_field(value: str, label: str) -> str | None:
    cleaned = clean_text(value)
    match = re.search(rf"{re.escape(label)}:\s*(.+)", cleaned, re.IGNORECASE)
    if not match: return None
    extracted = match.group(1)
    for next_label in ["Unique Features:", "Description:", "Location:", "Category:", "Phone:", "Email:", "Website:"]:
        if next_label.lower() != f"{label.lower()}:":
            extracted = extracted.split(next_label)[0]
    return extracted.strip(" .") or None

def extract_about_text(value: str, limit: int = 220) -> str:
    cleaned = clean_text(value)
    description = extract_labeled_field(cleaned, "Description")
    if description: return build_preview_text(description, limit=limit)
    features = extract_labeled_field(cleaned, "Unique Features")
    if features: return build_preview_text(features, limit=limit)
    return build_preview_text(cleaned, limit=limit)

# ==========================================
# 2. DOCUMENTS / RETRIEVAL
# ==========================================
def safe_retriever_invoke(query: str):
    if not retriever: return []
    try: return retriever.invoke(query)
    except Exception: return []

_cached_all_docs = None

def load_all_documents() -> list[dict]:
    global _cached_all_docs
    if _cached_all_docs is not None:
        return _cached_all_docs
    
    if not vectorstore: return []
    
    try:
        # Pinecone does not support .get(), so we fetch all via a broad similarity search
        docs = vectorstore.similarity_search("resort", k=100)
        rows = []
        seen = set()
        for doc in docs:
            name = doc.metadata.get("name")
            if name and name not in seen:
                seen.add(name)
                rows.append({
                    "page_content": clean_text(doc.page_content),
                    "metadata": {k: clean_text(v) if isinstance(v, str) else v for k, v in doc.metadata.items()},
                })
        _cached_all_docs = rows
        return rows
    except Exception as e:
        print(f"Failed to load documents from Pinecone: {e}")
        return []

# ==========================================
# 3. QUERY PARSING & INTENT
# ==========================================
def extract_query_terms(text: str) -> list[str]:
    stopwords = {"the", "a", "an", "i", "am", "is", "are", "for", "to", "of", "in", "on", "at", "me", "my", "we", "our", "and", "or", "with", "want", "need", "show", "suggest", "suggestion", "suggestions", "what", "which", "would", "could", "please", "trip", "stay", "resort", "resorts", "dandeli"}
    return [term for term in re.findall(r"\b[a-z0-9]+\b", normalize_text(text)) if len(term) > 2 and term not in stopwords]

class SearchFilters(BaseModel):
    min_rating: Optional[float] = Field(description="Minimum rating required by the user")
    max_budget: Optional[int] = Field(description="Maximum total budget in INR")
    guest_count: Optional[int] = Field(description="Number of guests traveling")
    family_friendly: Optional[bool] = Field(description="Whether the user explicitly wants family friendly options")

def extract_filters(query: str) -> tuple[dict, str]:
    normalized = normalize_text(query)
    filters = {}
    try:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0).with_structured_output(SearchFilters)
        parsed = llm.invoke(f"Extract search filters from the following query:\n\n{query}")
        
        if parsed.min_rating is not None:
            filters["rating"] = ("gte", parsed.min_rating)
        
        if parsed.max_budget is not None and parsed.guest_count is not None and parsed.guest_count > 0:
            filters["price"] = ("lte", max(1, parsed.max_budget // parsed.guest_count))
            filters["total_budget"] = parsed.max_budget
            filters["guest_count"] = parsed.guest_count
        elif parsed.max_budget is not None:
            filters["price"] = ("lte", parsed.max_budget)
        elif parsed.guest_count is not None and parsed.guest_count > 0:
            filters["guest_count"] = parsed.guest_count
            
        if parsed.family_friendly:
            filters["family_friendly"] = True
            
        return filters, normalized
    except Exception as e:
        print(f"LLM Structured Extraction Failed: {e}")
        return filters, normalized

def is_decision_query(normalized_query: str) -> bool:
    return any(marker in normalized_query for marker in ["which one should i choose", "which resort should", "which should we choose", "what should we choose", "best one", "best resort", "recommend one", "which one is best", "second-best", "backup"])

def wants_best_first_sort(normalized_query: str) -> bool:
    return any(marker in normalized_query for marker in ["sorted from best to worst", "sort from best to worst", "best to worst", "best ones first", "show best first", "top rated first", "highest rated first"])

def is_recommendation_query(normalized_query: str) -> bool:
    markers = ["suggest the best options", "best options", "what do you suggest", "what would you suggest", "what do you recommend", "what would you recommend", "any suggestions", "what are my options", "show me options", "what do you think", "what would be good", "expensive", "luxury", "premium", "high-end", "rich"]
    return any(marker in normalized_query for marker in markers) or is_decision_query(normalized_query)

def infer_trip_context(query: str) -> dict[str, bool]:
    normalized_query = normalize_text(query)
    return {"family": any(marker in normalized_query for marker in ["family", "kids", "children"]), "couple": any(marker in normalized_query for marker in ["couple", "2 people", "two people", "we're 2", "we are 2"]), "solo": any(marker in normalized_query for marker in ["solo", "coming alone", "single", "i'm alone", "i am alone"]), "birdwatching": "bird watching" in normalized_query or "birdwatching" in normalized_query, "nature": any(marker in normalized_query for marker in ["nature", "peaceful", "calm"]), "rafting": "rafting" in normalized_query, "adventure": "adventure" in normalized_query}

# ==========================================
# 4. FILTERING & SCORING
# ==========================================
def passes_numeric_filter(value, operator: str, expected: float) -> bool:
    if value is None: return False
    if operator == "gt": return value > expected
    if operator == "gte": return value >= expected
    if operator == "lt": return value < expected
    if operator == "lte": return value <= expected
    return True

def matches_filters(doc, filters: dict) -> bool:
    meta, content = doc["metadata"], clean_text(doc["page_content"]).lower()
    if "rating" in filters and not passes_numeric_filter(meta.get("rating"), *filters["rating"]): return False
    if "price" in filters and not passes_numeric_filter(meta.get("price"), *filters["price"]): return False
    if filters.get("family_friendly") and "family friendly: yes" not in content: return False
    return True

def score_document_for_query(doc: dict, query: str) -> int:
    normalized_query = normalize_text(query)
    haystack = " ".join([str(doc["metadata"].get("name", "")), str(doc["metadata"].get("location", "")), doc["page_content"]]).lower()
    terms = [term for term in re.findall(r"\b[a-z0-9]+\b", normalized_query) if len(term) > 2]
    score = sum(haystack.count(term) for term in terms)
    if "rafting" in normalized_query:
        score += 12 if "water activities: rafting" in haystack else 0
        score += 10 if "nearby activities: rafting" in haystack or "nearby activities: river rafting" in haystack else 0
        score += 4 if "kali river" in haystack or "ganeshgudi" in haystack else 0
    if "adventure" in normalized_query:
        score += 10 if "category: adventure" in haystack or "category: adventure camp" in haystack else 0
        score += 6 if "adventure desk" in haystack else 0
        score += 4 if "zipline" in haystack or "kayaking" in haystack else 0
    if any(marker in normalized_query for marker in ["luxury", "premium", "expensive", "high-end", "rich"]):
        score += int((doc["metadata"].get("price", 0) or 0) / 60)
        score += 12 if "luxury" in haystack or "riverside" in haystack else 0
        score += int((doc["metadata"].get("rating", 0) or 0) * 6)
    rating = doc["metadata"].get("rating", 0) or 0
    if "good rating" in normalized_query or "best rated" in normalized_query:
        score += int(rating * 25)
    elif is_decision_query(normalized_query):
        score += int(rating * 18) - (40 if rating < 4.2 else 0)
    elif any(marker in normalized_query for marker in ["what do you suggest", "what would you suggest", "what do you recommend", "what would you recommend", "any suggestions"]):
        score += int(rating * 12)
    if any(marker in normalized_query for marker in ["peaceful", "calm", "low-crowd"]) and any(marker in haystack for marker in ["peaceful", "eco resort", "nature resort", "forest"]):
        score += 10
    return score

def sort_documents_for_query(docs: list[dict], query: str, filters: dict = None) -> list[dict]:
    filters = filters or {}
    def sort_key(d):
        score = score_document_for_query(d, query)
        rating = d["metadata"].get("rating", 0) or 0
        price = d["metadata"].get("price", 10**9) or 10**9
        if "price" in filters:
            return (score, rating, price)
        return (score, rating, -price)
    return sorted(docs, key=sort_key, reverse=True)

def sort_documents_by_best_to_worst(docs: list[dict]) -> list[dict]:
    return sorted(docs, key=lambda d: (-(d["metadata"].get("rating", 0) or 0), d["metadata"].get("price", 10**9) or 10**9, d["metadata"].get("name", "")))

def dedupe_documents(docs: list[dict]) -> list[dict]:
    seen, unique_docs = set(), []
    for doc in docs:
        name = doc["metadata"].get("name")
        if name not in seen:
            seen.add(name)
            unique_docs.append(doc)
    return unique_docs

def keyword_rank_documents(docs: list[dict], query: str) -> list[dict]:
    terms = extract_query_terms(query)
    if not terms: return docs[:]
    ranked = []
    for doc in docs:
        haystack = " ".join([str(doc["metadata"].get("name", "")), str(doc["metadata"].get("category", "")), str(doc["metadata"].get("location", "")), doc["page_content"]]).lower()
        score = 0
        for term in terms:
            score += haystack.count(term) * 3
            score += 4 if term in str(doc["metadata"].get("name", "")).lower() else 0
            score += 2 if term in str(doc["metadata"].get("category", "")).lower() else 0
        if score > 0: ranked.append((score, doc))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in ranked]

def hybrid_retrieve_documents(query: str, all_docs: list[dict]) -> list[dict]:
    dense_docs = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in safe_retriever_invoke(query)]
    combined, seen = [], set()
    for doc in dense_docs + keyword_rank_documents(all_docs, query):
        name = doc["metadata"].get("name")
        if name not in seen:
            seen.add(name)
            combined.append(doc)
    return combined

# ==========================================
# 5. SPECIFIC FIELD QUERIES & FORMATTERS
# ==========================================
FIELD_MAPPINGS = [
    ("website", "Website", ["website", "website link", "site", "site link", "web link", "url", "homepage", "official site", "official website", "resort website", "link"]),
    ("phone", "Phone", ["phone", "phone number", "contact number", "contact no", "contact", "mobile", "mobile number", "call number", "telephone", "telephone number", "number"]),
    ("email", "Email", ["email", "email address", "mail", "mail id", "gmail", "contact email", "email id", "mail address"]),
    ("location", "Location", ["location", "address", "where is", "where located", "where is it", "place", "area", "spot", "located", "situated"]),
    ("price", "Price", ["price", "cost", "rate", "tariff", "charges", "fee", "pricing", "how much", "amount", "per day price"]),
    ("rating", "Rating", ["rating", "review", "reviews", "score", "stars", "star rating", "rank", "feedback rating"]),
    ("category", "Category", ["category", "type", "resort type", "kind", "style", "segment", "class"]),
    ("description", "Description", ["description", "about", "details", "tell me more", "more info", "information", "summary", "overview", "what about", "more about"]),
    ("unique_features", "Unique Features", ["unique features", "features", "highlights", "special features", "specialities", "amenities", "facilities", "what is special", "what's special", "special"]),
]

def extract_requested_fields(normalized_query: str) -> list[tuple[str, str]]:
    requested, seen = [], set()
    for key, label, aliases in FIELD_MAPPINGS:
        if any(alias in normalized_query for alias in aliases) and key not in seen:
            requested.append((key, label))
            seen.add(key)
    return requested

def get_field_value(doc: dict, key: str):
    if key == "description": return extract_labeled_field(doc["page_content"], "Description") or extract_about_text(doc["page_content"])
    if key == "unique_features": return extract_labeled_field(doc["page_content"], "Unique Features")
    return doc["metadata"].get(key)

def format_requested_fields(doc: dict, requested_fields: list[tuple[str, str]]) -> str | None:
    if not requested_fields: return None
    name = clean_text(str(doc["metadata"].get("name", "Unknown")))
    lines = []
    for key, label in requested_fields:
        value = get_field_value(doc, key)
        if value in (None, "", "N/A"): lines.append(f"{label} for {name} is not available.")
        elif key == "price": lines.append(f"Price for {name}: {value} INR per day per person")
        elif key == "rating": lines.append(f"Rating for {name}: {value}")
        else: lines.append(f"{label} for {name}: {clean_text(str(value))}")
    return "\n".join(lines)

def format_single_resort_field_response(doc: dict, normalized_query: str) -> str | None:
    return format_requested_fields(doc, extract_requested_fields(normalized_query))

def find_named_resort(query: str, docs: list[dict]) -> dict | None:
    normalized_query, best_doc, best_score = normalize_text(query), None, 0
    for doc in docs:
        resort_name = normalize_text(str(doc["metadata"].get("name", "")))
        if resort_name in normalized_query and len(resort_name.split()) > best_score:
            best_doc, best_score = doc, len(resort_name.split())
    return best_doc

def find_all_named_resorts(query: str, docs: list[dict]) -> list[dict]:
    normalized_query = normalize_text(query)
    found, seen = [], set()
    for doc in docs:
        resort_name = normalize_text(str(doc["metadata"].get("name", "")))
        if resort_name and len(resort_name) > 3 and resort_name in normalized_query and resort_name not in seen:
            found.append(doc)
            seen.add(resort_name)
    return sorted(found, key=lambda d: -len(str(d["metadata"].get("name", ""))))

def is_comparison_query(normalized_query: str) -> bool:
    return any(marker in normalized_query for marker in ["compare", "difference between", "vs", "versus", "torn between", "which one", "better choice"])

def is_single_resort_followup_query(normalized_query: str) -> bool:
    return any(marker in normalized_query for marker in ["tell me more", "more about", "details about", "about this", "about "])

def is_single_resort_field_query(normalized_query: str) -> bool:
    return any(alias in normalized_query for _, _, aliases in FIELD_MAPPINGS for alias in aliases)

def is_compound_best_detail_query(normalized_query: str) -> bool:
    has_list = any(marker in normalized_query for marker in ["list resorts", "show resorts", "list ", "show me resorts"])
    has_best = any(marker in normalized_query for marker in ["best one", "best resort", "tell me more", "details"])
    return has_list and has_best and is_single_resort_field_query(normalized_query)

def build_fit_reason(doc: dict, query: str, guest_count: int | None = None) -> str:
    meta, content, reasons, context = doc["metadata"], doc["page_content"].lower(), [], infer_trip_context(query)
    if context["family"] and "family friendly: yes" in content: reasons.append("family-friendly stay")
    if context["couple"]: reasons.append("easy fit for a 2-person trip")
    if context["solo"]: reasons.append("good for a quiet solo stay")
    if context["rafting"] and "rafting" in content: reasons.append("rafting access nearby")
    if context["birdwatching"] and "bird watching" in content: reasons.append("good for bird watching")
    if context["adventure"] and "adventure" in content: reasons.append("adventure-oriented stay")
    if context["nature"] and any(marker in content for marker in ["peaceful", "forest", "eco resort", "nature resort"]): reasons.append("peaceful nature setting")
    if guest_count and meta.get("price") is not None: reasons.append(f"estimated total {meta.get('price') * guest_count} INR per night for {guest_count} guests")
    if meta.get("rating") is not None: reasons.append(f"rating {meta.get('rating')}")
    return ", ".join((reasons or ["good overall match for your request"])[:4])

def build_tradeoff(doc: dict, guest_count: int | None = None, total_budget: int | None = None) -> str:
    price, rating = doc["metadata"].get("price"), doc["metadata"].get("rating")
    if guest_count and price is not None and total_budget is not None and price * guest_count > total_budget: return "Tradeoff: total nightly cost may feel high for a group budget."
    if price is not None and price < 1000: return "Tradeoff: lower price may mean a simpler stay experience."
    if rating is not None and rating < 4.3: return "Tradeoff: rating is decent but not among the top-rated options."
    return "Tradeoff: availability and exact activity arrangements should still be confirmed before booking."

def format_results(docs: list[dict], guest_count: int | None = None, include_contacts: bool = False) -> str:
    results = []
    for index, doc in enumerate(docs, start=1):
        meta, price = doc["metadata"], doc["metadata"].get("price")
        lines = [f"{index}. {clean_text(str(meta.get('name', 'Unknown')))}", f"Location: {clean_text(str(meta.get('location', 'N/A')))}", f"Price: {price} INR per day per person"]
        if guest_count and price is not None: lines.append(f"Estimated total: {price * guest_count} INR per night for {guest_count} guests")
        lines.extend([f"Rating: {meta.get('rating')}", f"About: {extract_about_text(doc['page_content'])}"])
        if include_contacts: lines.extend([f"Phone: {clean_text(str(meta.get('phone', 'N/A')))}", f"Email: {clean_text(str(meta.get('email', 'N/A')))}", f"Website: {clean_text(str(meta.get('website', 'N/A')))}"])
        results.append("\n".join(lines))
    return "\n\n".join(results)

def format_single_resort_detail(doc: dict, guest_count: int | None = None) -> str:
    meta, price = doc["metadata"], doc["metadata"].get("price")
    lines = [clean_text(str(meta.get("name", "Unknown"))), f"Category: {clean_text(str(meta.get('category', 'N/A')))}", f"Location: {clean_text(str(meta.get('location', 'N/A')))}", f"Price: {price} INR per day per person"]
    if guest_count and price is not None: lines.append(f"Estimated total: {price * guest_count} INR per night for {guest_count} guests")
    lines.extend([f"Rating: {meta.get('rating')}", f"Description: {extract_labeled_field(doc['page_content'], 'Description') or extract_about_text(doc['page_content'])}"])
    features = extract_labeled_field(doc["page_content"], "Unique Features")
    if features: lines.append(f"Unique Features: {features}")
    return "\n".join(lines)

def format_recommendation_summary(docs: list[dict], query: str, guest_count: int | None = None, total_budget: int | None = None) -> str:
    best = docs[0]
    response = ["Best match for your request:", f"{best['metadata'].get('name')}", f"Why it fits: {build_fit_reason(best, query, guest_count=guest_count)}.", build_tradeoff(best, guest_count=guest_count, total_budget=total_budget), "", "Quick details:", "", format_single_resort_detail(best, guest_count=guest_count)]
    if len(docs) > 1:
        response.extend(["", "Backup option:", docs[1]["metadata"].get("name")])
    return "\n".join(response)

def format_compound_best_detail_response(docs: list[dict], query: str, guest_count: int | None = None, total_budget: int | None = None) -> str:
    best = docs[0]
    response = ["Best match for your request:", f"{best['metadata'].get('name')}", f"Why it fits: {build_fit_reason(best, query, guest_count=guest_count)}.", build_tradeoff(best, guest_count=guest_count, total_budget=total_budget), "", "Matching resorts:", "", format_results(docs[:5], guest_count=guest_count), "", f"Requested details for {best['metadata'].get('name')}:", format_single_resort_detail(best, guest_count=guest_count)]
    field_block = format_requested_fields(best, extract_requested_fields(normalize_text(query)))
    if field_block: response.extend(["", field_block])
    return "\n".join(response)

def format_comparison_response(docs: list[dict], query: str) -> str | None:
    if len(docs) < 2: return None
    a_name = clean_text(str(docs[0]["metadata"].get("name", "Resort A")))
    b_name = clean_text(str(docs[1]["metadata"].get("name", "Resort B")))
    lines = [f"Comparing {a_name} vs {b_name}:", ""]
    lines.append(f"Price: {a_name} is {docs[0]['metadata'].get('price')} INR/day. {b_name} is {docs[1]['metadata'].get('price')} INR/day.")
    lines.append(f"Rating: {a_name} is rated {docs[0]['metadata'].get('rating')}. {b_name} is rated {docs[1]['metadata'].get('rating')}.")
    lines.append("")
    lines.append(f"**{a_name} Highlights:**\n{extract_about_text(docs[0]['page_content'])}")
    lines.append(f"\n**{b_name} Highlights:**\n{extract_about_text(docs[1]['page_content'])}")
    lines.append("\nConclusion:")
    a_score, b_score = score_document_for_query(docs[0], query), score_document_for_query(docs[1], query)
    if a_score > b_score + 5: lines.append(f"Based on your specific needs, **{a_name}** seems like a better fit.")
    elif b_score > a_score + 5: lines.append(f"Based on your specific needs, **{b_name}** seems like a better fit.")
    else: lines.append(f"Both are excellent choices. Choose **{a_name}** if you prefer {docs[0]['metadata'].get('category')}, or **{b_name}** for {docs[1]['metadata'].get('category')}.")
    return "\n".join(lines)
