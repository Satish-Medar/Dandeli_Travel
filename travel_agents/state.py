import operator
from typing import Annotated, Literal, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str


class RouteResponse(BaseModel):
    next: Literal["SmallTalk", "Researcher", "Planner", "Booker", "OutOfScope", "FINISH"]
