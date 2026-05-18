# Tracks conversational booking state and context for the travel assistant.
# File: travel_agents/state.py


import operator
from typing import Annotated, Literal, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str


class RouteResponse(BaseModel):
    next: Literal["SmallTalk", "Researcher", "Planner", "Booker", "OutOfScope", "FINISH"]