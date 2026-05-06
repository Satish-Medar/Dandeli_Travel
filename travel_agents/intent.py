from typing import Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from .llms import groq_llm, groq_70b, gemini_llm, prefer_groq_invoke

class IntentClassification(BaseModel):
    next: str = Field(description="Exactly one of: SmallTalk, Researcher, Planner, Booker, OutOfScope")

intent_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert intent classifier for Vana AI, a Dandeli Travel Agent.\n"
               "Determine the user's intent based on the conversation history.\n"
               "Rules:\n"
               "- If the user is asking for resort contact information, phone numbers, emails, or websites, pick 'Researcher'.\n"
               "- If the user is answering a question about a booking (like giving dates, names, or THEIR OWN contact info for booking), modifying a booking (changing numbers or dates), or wants to book a resort, pick 'Booker'.\n"
               "- If the user is asking to plan an itinerary or trip, pick 'Planner'.\n"
               "- If the user is asking for resort prices, comparing resorts, or asking for recommendations, pick 'Researcher'.\n"
               "- If it's a general greeting, thanks, or asking for help, pick 'SmallTalk'.\n"
               "- Otherwise, pick 'OutOfScope'."),
    MessagesPlaceholder(variable_name="messages"),
])

intent_chain = prefer_groq_invoke(
    intent_prompt | groq_70b.with_structured_output(IntentClassification),
    prefer_groq_invoke(
        intent_prompt | groq_llm.with_structured_output(IntentClassification),
        intent_prompt | gemini_llm.with_structured_output(IntentClassification)
    )
)

async def classify_user_intent(messages: str | Sequence[BaseMessage]) -> str:
    if isinstance(messages, str):
        msg_list = [HumanMessage(content=messages)]
    else:
        msg_list = list(messages)
        
    try:
        response = await intent_chain.ainvoke({"messages": msg_list})
        return response.next
    except Exception as e:
        print(f"Intent classification failed: {e}")
        return "OutOfScope"
