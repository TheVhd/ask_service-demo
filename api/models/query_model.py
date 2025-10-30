from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class QueryRequest(BaseModel):
    """
    Query Request Model
    """
    question: str = Field(..., description="User question")
    sessionID: Optional[str] = Field(None, description="Session ID")


class QueryResponse(BaseModel):
    """
    Query Response Model
    """
    answer: str
    session_id: str
    question: str
    service_name: str
    prompt_tokens: int
    completion_tokens: int
