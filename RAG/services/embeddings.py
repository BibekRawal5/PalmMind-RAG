from sentence_transformers import SentenceTransformer
from .singleton import Singleton

class Embedder(metaclass=Singleton):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()
