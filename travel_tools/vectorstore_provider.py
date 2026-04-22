from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_classic.chains.query_constructor.base import AttributeInfo
from langchain_classic.retrievers import SelfQueryRetriever
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from .config import CHROMA_DB_PATH

load_dotenv()

embedding_func = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
vectorstore = None
retriever = None

try:
    print("Loading ChromaDB...")
    vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_func)
    metadata_field_info = [
        AttributeInfo(name="price", description="Single simple price in INR for 1 day stay for 1 person", type="integer"),
        AttributeInfo(name="rating", description="Rating (1-5)", type="float"),
        AttributeInfo(name="category", description="Resort category", type="string"),
        AttributeInfo(name="name", description="Resort name", type="string"),
        AttributeInfo(name="email", description="Email address", type="string"),
        AttributeInfo(name="phone", description="Phone number", type="string"),
        AttributeInfo(name="location", description="Location", type="string"),
        AttributeInfo(name="website", description="Website URL", type="string"),
    ]
    from langchain_google_genai import ChatGoogleGenerativeAI
    query_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0, max_retries=0).with_fallbacks([ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0, max_retries=2)])
    retriever = SelfQueryRetriever.from_llm(llm=query_llm, vectorstore=vectorstore, document_contents="Detailed descriptions, activities, and amenities of resorts in Dandeli", metadata_field_info=metadata_field_info, enable_limit=False)
    print("SelfQueryRetriever loaded successfully.")
except Exception as error:
    retriever = None
    vectorstore = None
    print(f"Error loading ChromaDB: {error}")
    with open("uvicorn_error.log", "w") as fw:
        fw.write(str(error))
