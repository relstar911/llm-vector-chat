from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.db import SessionLocal, ChatHistory
from app.models.query import ChatHistoryItem
from typing import List
import json

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/chats", response_model=List[ChatHistoryItem])
def get_all_chats(db: Session = Depends(get_db)):
    chats = db.query(ChatHistory).order_by(ChatHistory.timestamp.desc()).all()
    return [
        ChatHistoryItem(
            id=chat.id,
            prompt=chat.prompt,
            response=chat.response,
            timestamp=chat.timestamp.isoformat() if chat.timestamp else None,
            metadata=json.loads(chat.chat_metadata) if chat.chat_metadata else {}
        ) for chat in chats
    ]

from app.services.vector_db import remove_from_vector_db

@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: str, db: Session = Depends(get_db)):
    chat = db.query(ChatHistory).filter_by(id=chat_id).first()
    if not chat:
        return {"success": False, "error": "Chat not found"}
    db.delete(chat)
    db.commit()
    remove_from_vector_db(chat_id)
    return {"success": True}

from fastapi import Body
from datetime import datetime

from app.services.embedding import embedding_service
from app.services.vector_db import add_to_vector_db

@router.post("/chats/restore")
def restore_chat(
    id: str = Body(...),
    prompt: str = Body(...),
    response: str = Body(...),
    timestamp: str = Body(...),
    metadata: dict = Body({}),
    db: Session = Depends(get_db)
):
    # Prüfen, ob Chat mit ID schon existiert
    if db.query(ChatHistory).filter_by(id=id).first():
        return {"success": False, "error": "Chat mit dieser ID existiert bereits."}
    # Timestamp als datetime
    ts = datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp
    chat_entry = ChatHistory(
        id=id,
        prompt=prompt,
        response=response,
        timestamp=ts,
        chat_metadata=json.dumps(metadata, default=str)
    )
    db.add(chat_entry)
    db.commit()
    # Embedding für den Prompt erzeugen und in ChromaDB speichern
    embedding = embedding_service.embed(prompt)
    add_to_vector_db(prompt, embedding, {"id": id, "timestamp": timestamp})
    return {"success": True}
