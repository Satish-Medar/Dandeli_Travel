from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, START, StateGraph

from .content import extract_content
from .intent import classify_user_intent
from .llms import gemini_llm, groq_llm, prefer_groq_invoke
from .nodes import booker_node, out_of_scope_node, planner_node, researcher_node, smalltalk_node
from .state import AgentState, RouteResponse

supervisor_prompt = ChatPromptTemplate.from_messages([("system", "You are a Supervisor coordinating experts for Dandeli Tourism.\nIf the last message is from the user, route to SmallTalk, Researcher, Planner, Booker, or OutOfScope.\nIf the last message is from an expert, route to FINISH."), MessagesPlaceholder(variable_name="messages"), ("system", "Who should act next? Select one: SmallTalk, Researcher, Planner, Booker, OutOfScope, or FINISH.")])
supervisor_chain = prefer_groq_invoke(supervisor_prompt | groq_llm.with_structured_output(RouteResponse), supervisor_prompt | gemini_llm.with_structured_output(RouteResponse))


async def supervisor_node(state: AgentState):
    if state["messages"]:
        last_msg = state["messages"][-1]
        if getattr(last_msg, "name", "") in ["SmallTalk", "Researcher", "Planner", "Booker", "OutOfScope"]:
            return {"next": "FINISH"}
        if hasattr(last_msg, "content"):
            intent = await classify_user_intent(state["messages"])
            return {"next": intent}
    response = await supervisor_chain.ainvoke({"messages": state["messages"]})
    return {"next": response.next}


builder = StateGraph(AgentState)
for name, node in [("SmallTalk", smalltalk_node), ("Researcher", researcher_node), ("Planner", planner_node), ("Booker", booker_node), ("OutOfScope", out_of_scope_node), ("Supervisor", supervisor_node)]:
    builder.add_node(name, node)
builder.add_edge(START, "Supervisor")
for name in ["SmallTalk", "Researcher", "Planner", "Booker", "OutOfScope"]:
    builder.add_edge(name, "Supervisor")
builder.add_conditional_edges("Supervisor", lambda state: state["next"], {"SmallTalk": "SmallTalk", "Researcher": "Researcher", "Planner": "Planner", "Booker": "Booker", "OutOfScope": "OutOfScope", "FINISH": END})
graph = builder.compile()
