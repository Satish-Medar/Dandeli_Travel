from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

load_dotenv()


def prefer_groq_invoke(groq_runnable, gemini_runnable):
    def invoke_wrapper(in_val):
        try:
            return groq_runnable.invoke(in_val)
        except Exception:
            return gemini_runnable.invoke(in_val)
    return RunnableLambda(invoke_wrapper)


groq_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, max_retries=0)
gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, max_retries=2)

planner_prompt = (
    "You are an enthusiastic, local Dandeli Planner. "
    "Create a simple, grounded itinerary using only the resort and activity information in context. "
    "Do not invent attractions or facilities. "
    "Always recommend at least one specific resort from the provided research when the user asks for a stay. "
    "Keep the plan practical and realistic. "
    "Format the response clearly with Day 1 and Day 2 sections when relevant."
)

planner_agent = prefer_groq_invoke(create_react_agent(groq_llm, tools=[]), create_react_agent(gemini_llm, tools=[]))
