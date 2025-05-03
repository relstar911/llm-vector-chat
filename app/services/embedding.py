from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"

class EmbeddingService:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list:
        embedding = self.model.encode([text])[0]
        return embedding.tolist() if isinstance(embedding, np.ndarray) else embedding

embedding_service = EmbeddingService()
