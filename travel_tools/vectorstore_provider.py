import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_classic.chains.query_constructor.base import AttributeInfo
from langchain_classic.retrievers import SelfQueryRetriever
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

embedding_func = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
vectorstore = None
retriever = None

try:
    print("Loading Pinecone VectorStore...")
    index_name = os.getenv("PINECONE_INDEX_NAME", "dandeli-travel")
    vectorstore = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding_func)
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
    query_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0, max_retries=0).with_fallbacks([ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0, max_retries=2)])
    retriever = SelfQueryRetriever.from_llm(llm=query_llm, vectorstore=vectorstore, document_contents="Detailed descriptions, activities, and amenities of resorts in Dandeli", metadata_field_info=metadata_field_info, enable_limit=False)
    print("SelfQueryRetriever loaded successfully from Pinecone.")
except Exception as error:
    retriever = None
    vectorstore = None
    print(f"Error loading Pinecone: {error}")
    with open("uvicorn_error.log", "a") as fw:
        fw.write(f"Pinecone load error: {str(error)}\n")
