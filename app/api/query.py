from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.query import QueryRequest, QueryResult, ChatHistoryItem
from typing import Optional
from app.services.embedding import embedding_service
from app.services.vector_db import query_vector_db
from app.services.db import SessionLocal, ChatHistory, ChatSession

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/query", response_model=QueryResult)
def query(request: QueryRequest, db: Session = Depends(get_db)):
    import traceback
    try:
        embedding = embedding_service.embed(request.query)
        score_threshold = getattr(request, 'score_threshold', 0.5) if hasattr(request, 'score_threshold') else 0.5
        results = query_vector_db(embedding, n_results=request.n_results, score_threshold=score_threshold)
        items = []
        # Alle existierenden Session-IDs holen
        session_ids = set(row[0] for row in db.query(ChatSession.id).all())
        for doc, meta, score in zip(results.get('documents', [[]])[0], results.get('metadatas', [[]])[0], results.get('scores', [[]])[0]):
            chat_db = db.query(ChatHistory).filter_by(id=meta.get('id')).first()
            # Session-Filter: Nur anzeigen, wenn Session existiert
            session_id = meta.get('session_id') or (chat_db.session_id if chat_db and hasattr(chat_db, 'session_id') else None)
            if session_id and session_id not in session_ids:
                continue  # Session existiert nicht mehr
            items.append(ChatHistoryItem(
                id=meta.get('id'),
                prompt=doc,
                response=chat_db.response if chat_db else '',
                timestamp=meta.get('timestamp'),
                metadata=meta,
                score=score
            ))
        return QueryResult(results=items)
    except Exception as e:
        print("[Query-ERROR] Exception:", e)
        print(traceback.format_exc())
        return {"success": False, "error": str(e), "trace": traceback.format_exc()}

