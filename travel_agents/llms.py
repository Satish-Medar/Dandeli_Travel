from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

load_dotenv()


groq_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, max_retries=2)
groq_70b = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, max_retries=0)
gemini_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1, max_retries=2)

def prefer_groq_invoke(groq_runnable, gemini_runnable):
    def invoke_wrapper(in_val):
        try:
            return groq_runnable.invoke(in_val)
        except Exception:
            try:
                # If 70B fails (rate limit), fallback to 8B internally if it's a ChatModel, else just gemini
                pass
            except Exception:
                pass
            return gemini_runnable.invoke(in_val)
    
    async def ainvoke_wrapper(in_val):
        try:
            return await groq_runnable.ainvoke(in_val)
        except Exception:
            return await gemini_runnable.ainvoke(in_val)
            
    return RunnableLambda(invoke_wrapper, afunc=ainvoke_wrapper)

planner_prompt = (
    "You are an enthusiastic, local Dandeli Planner. "
    "Create a simple, grounded itinerary using only the resort and activity information in context. "
    "Do not invent attractions, amenities, or facility details that are not explicitly stated in the verified research. "
    "If you cannot answer accurately from the provided research, say so and ask for more details instead of guessing. "
    "Always recommend at least one specific resort from the provided research when the user asks for a stay. "
    "Keep the plan practical and realistic. "
    "Format the response clearly with Day 1 and Day 2 sections when relevant."
)

planner_agent = prefer_groq_invoke(create_react_agent(groq_llm, tools=[]), create_react_agent(gemini_llm, tools=[]))
