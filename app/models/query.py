from pydantic import BaseModel
from typing import Optional, List

class ChatHistoryItem(BaseModel):
    id: Optional[str]
    prompt: str
    response: str
    timestamp: Optional[str]
    metadata: Optional[dict] = None
    score: Optional[float] = None

class QueryRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5
    score_threshold: Optional[float] = 0.5

class QueryResult(BaseModel):
    results: List[ChatHistoryItem]
