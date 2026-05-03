import os
import json
import time
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import init as pinecone_init
from pathlib import Path

# Load environment variables
load_dotenv()

# Path to the data
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = str(BASE_DIR / "data" / "json_files" / "resorts.json")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "dandeli-travel")

def load_data():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        return []

    with open(DATA_PATH, "r", encoding="utf-8-sig") as f:
        resorts = json.load(f)

    docs = []
    for resort in resorts:
        normalized_price = resort.get("price")

        # Create a rich text representation for embedding to capture all context
        content = (
            f"Resort Name: {resort.get('name')}\n"
            f"Category: {resort.get('category')}\n"
            f"Location: {resort.get('location')}, {resort.get('city')}\n"
            f"Description: {resort.get('description')}\n"
            f"Unique Features: {resort.get('unique_features')}\n"
            f"Rooms: {', '.join(resort.get('rooms', []))}\n"
            f"Amenities: {', '.join(resort.get('amenities', []))}\n"
            f"On-site Activities: {', '.join(resort.get('activities_onsite', []))}\n"
            f"Nearby Activities: {', '.join(resort.get('activities_nearby', []))}\n"
            f"Water Activities: {', '.join(resort.get('water_activities', []))}\n"
            f"Food Options: {', '.join(resort.get('food_options', []))}\n"
            f"Price: {normalized_price} INR per day per person\n"
            f"Rating: {resort.get('rating')} based on {resort.get('review_count')} reviews\n"
            f"Family Friendly: {'Yes' if resort.get('family_friendly') else 'No'}\n"
        )

        def clean_val(v):
            if isinstance(v, str):
                return " ".join(v.split())
            return v
            
        metadata = {
            "id": resort.get("id"),
            "name": clean_val(resort.get("name")),
            "category": clean_val(resort.get("category")),
            "city": clean_val(resort.get("city")) or "Dandeli",
            "price": normalized_price,
            "rating": resort.get("rating"),
            "family_friendly": resort.get("family_friendly", False),
            "romantic_couples": resort.get("romantic_couples", False),
            "email": clean_val(resort.get("email")) or "Not Available",
            "phone": clean_val(resort.get("phone")) or "Not Available",
            "website": clean_val(resort.get("website")) or "Not Available",
            "location": clean_val(resort.get("location")) or "Not Available",
            "check_in": clean_val(resort.get("check_in")) or "N/A",
            "check_out": clean_val(resort.get("check_out")) or "N/A"
        }

        # Filter out None values from metadata
        metadata = {k: v for k, v in metadata.items() if v is not None}

        docs.append(Document(page_content=content, metadata=metadata))

    return docs

def create_pinecone_store(docs, embeddings):
    print("Connecting to Pinecone...")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
    if not pinecone_api_key or not pinecone_env:
        raise RuntimeError("PINECONE_API_KEY and PINECONE_ENVIRONMENT must be set to ingest data.")
    pinecone_init(api_key=pinecone_api_key, environment=pinecone_env)

    print(f"Creating/updating Pinecone index: {PINECONE_INDEX_NAME}...")
    vectorstore = PineconeVectorStore.from_documents(
        documents=docs,
        embedding=embeddings,
        index_name=PINECONE_INDEX_NAME
    )
    print(f"Success! Pinecone index updated.")

if __name__ == "__main__":
    docs = load_data()
    if docs:
        print("Initializing Google Generative AI Embeddings...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")

        create_pinecone_store(docs, embeddings)
    else:
        print("No documents loaded out of JSON. Aborting.")
