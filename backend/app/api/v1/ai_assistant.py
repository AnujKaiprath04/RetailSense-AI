from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from services.ai_assistant import AIRetailAssistantEngine

router = APIRouter(prefix="/ai-assistant", tags=["AI Retail Assistant"])
ai_engine = AIRetailAssistantEngine()

@router.post("/query")
def query_ai_assistant(
    payload: dict = Body(..., example={"query": "Why is tomorrow crowded and how many cashiers should I assign?"}),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query_text = payload.get("query", "Summarize store status")
    store_id = current_user.store_id or 1
    
    result = ai_engine.process_query(query_text, db, store_id=store_id)
    return result
