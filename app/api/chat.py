from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_client import query_ollama
from app.services.embedding import embedding_service
from app.services.vector_db import add_to_vector_db
from app.services.db import SessionLocal, ChatHistory
from app.core.utils import generate_id, current_timestamp
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    system_prompt = (
        "Antworte immer in der Sprache, in der die Frage gestellt wurde. "
        "Wenn du dir unsicher bist, sage: 'Ich bin mir nicht sicher.' "
        "Antworte niemals mit erfundenen Fakten oder Halluzinationen. "
        "Gib keine Übersetzungen, sondern antworte direkt in der Eingabesprache."
    )
    full_prompt = f"{system_prompt}\n\nUser: {request.prompt}"
    response = await query_ollama(full_prompt, model=request.model)
    embedding = embedding_service.embed(request.prompt)
    chat_id = generate_id()
    timestamp = current_timestamp()
    # Metadaten für beide Systeme vorbereiten
    metadata = {"id": chat_id, "timestamp": timestamp}
    chroma_metadata = {"id": chat_id, "timestamp": timestamp.isoformat()}
    add_to_vector_db(request.prompt, embedding, chroma_metadata)
    chat_entry = ChatHistory(id=chat_id, prompt=request.prompt, response=response, timestamp=timestamp, chat_metadata=json.dumps(metadata, default=str))
    db.add(chat_entry)
    db.commit()
    return ChatResponse(response=response)
