from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    user_id: str | None = None
    user_name: str | None = None
    user_email: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str


class AssistantTurn(BaseModel):
    role: str
    content: str


class AssistantReplyRequest(BaseModel):
    message: str = Field(..., min_length=1)
    messages: list[AssistantTurn] = Field(default_factory=list)


class AssistantReplyResponse(BaseModel):
    reply: str


class SessionCreateRequest(BaseModel):
    user_id: str | None = None
    title: str | None = None
    user_name: str | None = None
    user_email: str | None = None


class SessionSummary(BaseModel):
    session_id: str
    title: str
    preview: str
    updated_at: str


class SessionResponse(BaseModel):
    session_id: str
    message: str
    title: str


class MessageRecord(BaseModel):
    role: str
    content: str
    created_at: str


class SessionDetail(BaseModel):
    session_id: str
    title: str
    updated_at: str
    messages: List[MessageRecord]


class AppConfig(BaseModel):
    clerk_publishable_key: str | None = None
    clerk_enabled: bool
