from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai_service import ai_case_worker

router = APIRouter(prefix="/assistant", tags=["AI Case Worker"])


class ChatMessageInput(BaseModel):
    message: str
    citizen_id: Optional[int] = None


class MatchedSchemeSchema(BaseModel):
    id: int
    title: str
    category: str
    description: str
    eligibility: str
    required_documents: str
    deadline: str
    match_reason: str


class AssistantChatResponse(BaseModel):
    reply: str
    matched_schemes: List[MatchedSchemeSchema] = []
    missing_fields: List[str] = []
    can_create_reminder: bool = True


@router.post("/chat", response_model=AssistantChatResponse)
def assistant_chat(payload: ChatMessageInput, db: Session = Depends(get_db)):
    """
    AI Case Worker endpoint analyzing citizen queries, extracting structured fields,
    matching database schemes, and offering follow-ups or reminder actions.
    """
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message string cannot be empty")

    result = ai_case_worker.analyze_and_respond(payload.message, db)
    return result
