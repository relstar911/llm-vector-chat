from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.query import QueryRequest, QueryResult, ChatHistoryItem
from typing import Optional
from app.services.embedding import embedding_service
from app.services.vector_db import query_vector_db
from app.services.db import SessionLocal, ChatHistory

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/query", response_model=QueryResult)
def query(request: QueryRequest, db: Session = Depends(get_db)):
    embedding = embedding_service.embed(request.query)
    score_threshold = getattr(request, 'score_threshold', 0.5) if hasattr(request, 'score_threshold') else 0.5
    results = query_vector_db(embedding, n_results=request.n_results, score_threshold=score_threshold)
    items = []
    for doc, meta, score in zip(results.get('documents', [[]])[0], results.get('metadatas', [[]])[0], results.get('scores', [[]])[0]):
        chat_db = db.query(ChatHistory).filter_by(id=meta.get('id')).first()
        items.append(ChatHistoryItem(
            id=meta.get('id'),
            prompt=doc,
            response=chat_db.response if chat_db else '',
            timestamp=meta.get('timestamp'),
            metadata=meta,
            score=score
        ))
    return QueryResult(results=items)
