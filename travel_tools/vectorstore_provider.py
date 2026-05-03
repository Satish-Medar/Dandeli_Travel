import os
import threading
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_classic.chains.query_constructor.base import AttributeInfo
from langchain_classic.retrievers import SelfQueryRetriever
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from pinecone import init as pinecone_init

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(BASE_DIR / "chroma_db_v2"))
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "dandeli-travel")
VECTORSTORE_TYPE = os.getenv("VECTORSTORE_TYPE", "AUTO").upper()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

embedding_func = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
vectorstore = None
retriever = None
_store_initialized = False
_store_lock = threading.Lock()

metadata_field_info = [
    AttributeInfo(name="price", description="Single simple price in INR for 1 day stay for 1 person", type="integer"),
    AttributeInfo(name="rating", description="Rating (1-5)", type="float"),
    AttributeInfo(name="category", description="Resort category", type="string"),
    AttributeInfo(name="name", description="Resort name", type="string"),
    AttributeInfo(name="email", description="Email address", type="string"),
    AttributeInfo(name="phone", description="Phone number", type="string"),
    AttributeInfo(name="location", description="Location", type="string"),
    AttributeInfo(name="website", description="Website URL", type="string"),
    AttributeInfo(name="family_friendly", description="Whether the resort is family friendly", type="boolean"),
    AttributeInfo(name="romantic_couples", description="Whether the resort is suited for romantic couples", type="boolean"),
]


def _open_error_log(message: str):
    try:
        with open("uvicorn_error.log", "a", encoding="utf-8") as fw:
            fw.write(f"{message}\n")
    except Exception:
        pass


def _pinecone_env_ready() -> bool:
    if not PINECONE_API_KEY or not PINECONE_ENVIRONMENT:
        print("Pinecone environment variables are not configured. Skipping Pinecone load.")
        return False
    try:
        pinecone_init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        return True
    except Exception as error:
        _open_error_log(f"Pinecone init error: {error}")
        print(f"Pinecone init failed: {error}")
        return False


def _load_pinecone_store(timeout_seconds: int = 12) -> Optional[PineconeVectorStore]:
    if not _pinecone_env_ready():
        return None

    def _target(result: dict):
        try:
            result["store"] = PineconeVectorStore.from_existing_index(index_name=PINECONE_INDEX_NAME, embedding=embedding_func)
        except Exception as error:
            result["error"] = error

    print("Loading Pinecone VectorStore...")
    thread_result = {}
    thread = threading.Thread(target=_target, args=(thread_result,), daemon=True)
    thread.start()
    thread.join(timeout=timeout_seconds)
    if thread.is_alive():
        _open_error_log("Pinecone load timeout")
        print(f"Pinecone load timed out after {timeout_seconds} seconds.")
        return None
    if thread_result.get("error"):
        error = thread_result["error"]
        _open_error_log(f"Pinecone load error: {error}")
        print(f"Failed to load Pinecone: {error}")
        return None
    return thread_result.get("store")


def _load_chroma_store() -> Optional[object]:
    try:
        if not Path(CHROMA_DB_PATH).exists():
            print(f"Chroma persistence path not found: {CHROMA_DB_PATH}")
            return None
        from langchain_community.vectorstores import Chroma

        print("Loading local Chroma VectorStore...")
        return Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_func)
    except Exception as error:
        _open_error_log(f"Chroma load error: {error}")
        print(f"Failed to load Chroma: {error}")
        return None


def _build_retriever(store):
    try:
        query_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0, max_retries=0).with_fallbacks([
            ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0, max_retries=2)
        ])
        return SelfQueryRetriever.from_llm(
            llm=query_llm,
            vectorstore=store,
            document_contents="Detailed descriptions, activities, and amenities of resorts in Dandeli",
            metadata_field_info=metadata_field_info,
            enable_limit=False,
        )
    except Exception as error:
        _open_error_log(f"Retriever creation error: {error}")
        print(f"Failed to create retriever: {error}")
        return None


def initialize_vectorstore() -> None:
    global vectorstore, retriever, _store_initialized
    with _store_lock:
        if _store_initialized:
            return
        _store_initialized = True
        if VECTORSTORE_TYPE in {"PINECONE", "AUTO"}:
            vectorstore = _load_pinecone_store()
            if vectorstore is not None:
                retriever = _build_retriever(vectorstore)

        if vectorstore is None and VECTORSTORE_TYPE in {"CHROMA", "AUTO"}:
            vectorstore = _load_chroma_store()
            if vectorstore is not None:
                retriever = _build_retriever(vectorstore)

        if vectorstore is None:
            print("No vector store loaded. Resort search will use local fallback data.")


def get_vectorstore() -> Optional[object]:
    if not _store_initialized:
        initialize_vectorstore()
    return vectorstore


def get_retriever() -> Optional[object]:
    if not _store_initialized:
        initialize_vectorstore()
    return retriever
