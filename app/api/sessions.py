from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.services.db import SessionLocal, ChatSession, ChatMessage

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import func

@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    session_data = db.query(
        ChatSession.id,
        ChatSession.title,
        ChatSession.created_at,
        func.count(ChatMessage.id).label("message_count")
    ).outerjoin(ChatMessage, ChatSession.id == ChatMessage.session_id
    ).group_by(ChatSession.id).order_by(ChatSession.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "message_count": s.message_count
        }
        for s in session_data
    ]

from pydantic import BaseModel

class SessionCreateRequest(BaseModel):
    title: str | None = None

@router.post("/sessions")
def create_session(req: SessionCreateRequest, db: Session = Depends(get_db)):
    session_id = str(uuid4())
    session = ChatSession(id=session_id, title=req.title, created_at=datetime.utcnow())
    db.add(session)
    db.commit()
    return {"id": session_id, "title": req.title, "created_at": session.created_at.isoformat()}

@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str, limit: int = Query(20), offset: int = Query(0), db: Session = Depends(get_db)):
    msgs = (
        db.query(ChatMessage)
        .filter_by(session_id=session_id)
        .order_by(ChatMessage.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    # Rückgabe in chronologischer Reihenfolge (älteste zuerst)
    msgs = list(reversed(msgs))
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "text": m.text,
            "timestamp": m.timestamp.isoformat()
        }
        for m in msgs
    ]

from pydantic import BaseModel

class MessageCreateRequest(BaseModel):
    sender: str
    text: str

@router.post("/sessions/{session_id}/message")
def add_message(session_id: str, req: MessageCreateRequest, db: Session = Depends(get_db)):
    msg_id = str(uuid4())
    msg = ChatMessage(
        id=msg_id,
        session_id=session_id,
        sender=req.sender,
        text=req.text,
        timestamp=datetime.utcnow()
    )
    db.add(msg)
    # Titel der Session auf ersten User-Input setzen
    session = db.query(ChatSession).filter_by(id=session_id).first()
    if req.sender == "user" and (session.title is None or session.title.strip() == ""):
        session.title = req.text[:60]
    db.commit()
    return {"id": msg_id, "sender": req.sender, "text": req.text, "timestamp": msg.timestamp.isoformat()}

from fastapi import Query
from app.services.vector_db import remove_from_vector_db

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, remove_vectors: bool = Query(True), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter_by(id=session_id).first()
    if not session:
        return {"success": False, "error": "Session not found"}
    # Optional: Embeddings aus ChromaDB entfernen
    if remove_vectors:
        for msg in session.messages:
            remove_from_vector_db(msg.id)
    db.delete(session)
    db.commit()
    return {"success": True}
