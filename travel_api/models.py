# Defines data models used by the travel API and booking system.
# File: travel_api/models.py


from typing import List, Optional
import re
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User message content")
    session_id: Optional[str] = Field(None, min_length=1, max_length=100, description="Session identifier")
    user_id: Optional[str] = Field(None, min_length=1, max_length=100, description="User identifier")
    user_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User display name")
    user_email: Optional[str] = Field(None, description="User email address")

    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v):
        """Sanitize message content to prevent XSS and other attacks."""
        if not v:
            return v

        # Remove potentially dangerous HTML/script tags
        v = re.sub(r'<[^>]+>', '', v)

        # Remove null bytes and other control characters
        v = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', v)

        # Limit consecutive whitespace
        v = re.sub(r'\s{3,}', ' ', v)

        return v.strip()

    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v):
        """Validate session ID format."""
        if v is None:
            return v

        # Allow alphanumeric, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Session ID must contain only letters, numbers, hyphens, and underscores')

        return v

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        """Validate user ID format."""
        if v is None:
            return v

        # Allow alphanumeric, hyphens, underscores, and dots
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError('User ID must contain only letters, numbers, dots, hyphens, and underscores')

        return v

    @field_validator('user_name')
    @classmethod
    def sanitize_user_name(cls, v):
        """Sanitize user name."""
        if v is None:
            return v

        # Remove potentially dangerous characters
        v = re.sub(r'[<>"/\\|?*\x00-\x1f]', '', v)

        # Limit length and strip whitespace
        return v.strip()[:100]

    @field_validator('user_email')
    @classmethod
    def validate_user_email(cls, v):
        """Validate user email format."""
        if v is None:
            return v

        # Basic email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')

        return v.lower().strip()


class ChatResponse(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100)
    reply: str = Field(..., min_length=1, max_length=50000)


class AssistantTurn(BaseModel):
    role: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=50000)
    name: Optional[str] = Field(None, min_length=1, max_length=100)

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        """Validate assistant turn role."""
        allowed_roles = {'user', 'assistant', 'system', 'function'}
        if v.lower() not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v.lower()

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v):
        """Sanitize assistant name."""
        if v is None:
            return v
        # Remove potentially dangerous characters
        return re.sub(r'[<>"/\\|?*\x00-\x1f]', '', v).strip()[:100]


class AssistantReplyRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="Assistant message content")
    messages: List[AssistantTurn] = Field(default_factory=list, max_length=50, description="Conversation history")

    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v):
        """Sanitize message content."""
        if not v:
            return v

        # Remove potentially dangerous HTML/script tags
        v = re.sub(r'<[^>]+>', '', v)

        # Remove null bytes and other control characters
        v = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', v)

        # Limit consecutive whitespace
        v = re.sub(r'\s{3,}', ' ', v)

        return v.strip()


class AssistantReplyResponse(BaseModel):
    reply: str = Field(..., min_length=1, max_length=50000)
    node_name: Optional[str] = Field(None, min_length=1, max_length=100)


class SessionCreateRequest(BaseModel):
    user_id: Optional[str] = Field(None, min_length=1, max_length=100, description="User identifier")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Session title")
    user_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User display name")
    user_email: Optional[str] = Field(None, description="User email address")

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        """Validate user ID format."""
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError('User ID must contain only letters, numbers, dots, hyphens, and underscores')
        return v

    @field_validator('title')
    @classmethod
    def sanitize_title(cls, v):
        """Sanitize session title."""
        if v is None:
            return v
        # Remove potentially dangerous characters and limit length
        v = re.sub(r'[<>"/\\|?*\x00-\x1f]', '', v)
        return v.strip()[:200]

    @field_validator('user_name')
    @classmethod
    def sanitize_user_name(cls, v):
        """Sanitize user name."""
        if v is None:
            return v
        v = re.sub(r'[<>"/\\|?*\x00-\x1f]', '', v)
        return v.strip()[:100]

    @field_validator('user_email')
    @classmethod
    def validate_user_email(cls, v):
        """Validate user email format."""
        if v is None:
            return v

        # Basic email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')

        return v.lower().strip()


class SessionSummary(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    preview: str = Field(default="", max_length=500)
    updated_at: str = Field(..., min_length=1, max_length=50)


class SessionResponse(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=500)
    title: str = Field(..., min_length=1, max_length=200)


class MessageRecord(BaseModel):
    role: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=50000)
    created_at: str = Field(..., min_length=1, max_length=50)


class SessionDetail(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    updated_at: str = Field(..., min_length=1, max_length=50)
    messages: List[MessageRecord] = Field(..., max_length=1000)


class AppConfig(BaseModel):
    clerk_publishable_key: Optional[str] = Field(None, min_length=1, max_length=200)
    clerk_enabled: bool