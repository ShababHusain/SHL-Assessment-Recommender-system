"""
Pydantic models for API request/response validation.
Enforces strict schema compliance per PRD requirements.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from enum import Enum


class MessageRole(str, Enum):
    """Valid message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """Single message in conversation history."""
    role: MessageRole
    content: str = Field(..., min_length=1, max_length=10000)

    @field_validator("content")
    def validate_content(cls, v: str) -> str:
        """Ensure content is non-empty and reasonable length."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message content cannot be empty or whitespace only")
        return stripped


class ChatRequest(BaseModel):
    """Request schema for POST /chat endpoint."""
    messages: List[Message] = Field(..., min_items=1, max_items=100)

    @field_validator("messages")
    def validate_messages(cls, msgs: List[Message]) -> List[Message]:
        """Ensure last message is from user."""
        if msgs and msgs[-1].role != MessageRole.USER:
            raise ValueError("Last message must be from user")
        return msgs


class Recommendation(BaseModel):
    """Single assessment recommendation."""
    name: str = Field(..., min_length=1, max_length=500)
    url: str = Field(..., min_length=10, max_length=1000)
    test_type: str = Field(..., min_length=1, max_length=200)

    @field_validator("url")
    def validate_url(cls, v: str) -> str:
        """Ensure URL is properly formatted."""
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class ChatResponse(BaseModel):
    """Response schema for POST /chat endpoint."""
    reply: str = Field(..., min_length=1, max_length=5000)
    recommendations: List[Recommendation] = Field(default_factory=list)
    end_of_conversation: bool = Field(default=False)

    @field_validator("recommendations")
    def validate_recommendations(cls, recs: List[Recommendation]) -> List[Recommendation]:
        """Ensure recommendations count is within valid range."""
        if len(recs) > 10:
            raise ValueError("Maximum 10 recommendations per response")
        return recs


class HealthResponse(BaseModel):
    """Response schema for GET /health endpoint."""
    status: Literal["ok"] = "ok"


class AssessmentCatalogItem(BaseModel):
    """Single assessment from SHL catalog."""
    name: str
    description: str
    url: str
    duration_minutes: Optional[int] = None
    category: str
    test_type: str
    embedding_vector: Optional[List[float]] = None  # Populated during indexing

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True
