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
    session_id: Optional[str] = "default"


class MatchedSchemeSchema(BaseModel):
    id: int
    title: str
    category: str
    description: str
    eligibility: str
    required_documents: str
    deadline: str
    match_reason: str
    benefits: Optional[str] = ""
    application: Optional[str] = ""
    official_link: Optional[str] = ""


class AssistantChatResponse(BaseModel):
    reply: str
    matched_schemes: List[MatchedSchemeSchema] = []
    missing_fields: List[str] = []
    can_create_reminder: bool = True


@router.post("/chat", response_model=AssistantChatResponse)
def assistant_chat(payload: ChatMessageInput, db: Session = Depends(get_db)):
    """
    AI Case Worker RAG endpoint analyzing citizen queries, retrieving SQLite schemes,
    grounding response with Gemini LLM, maintaining conversation memory, and outputting myScheme links.
    """
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message string cannot be empty")

    session_id = payload.session_id or f"citizen_{payload.citizen_id or 'default'}"
    result = ai_case_worker.analyze_and_respond(payload.message, db, session_id=session_id)
    return result
