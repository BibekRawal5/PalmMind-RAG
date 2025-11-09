import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List, Tuple
from ..config import settings
import numpy as np
import logging
import sys

logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout  
)

client = QdrantClient(url=settings.QDRANT_URL, 
                      api_key= settings.QDRANT_API)

def ensure_collection(dim: int):
    collections = [c.name for c in client.get_collections().collections]
    if settings.COLLECTION_NAME not in collections:
        client.recreate_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
        )


def upload_chunks(chunks: List[str], vectors: List[List[float]], doc_id: int):
    points = [
        PointStruct(
            id=str(uuid.uuid4()),  
            vector=vec,
            payload={
                "text": chunk,
                "doc_id": doc_id,
                "chunk_id": i
            }
        )
        for i, (chunk, vec) in enumerate(zip(chunks, vectors))
    ]

    client.upsert(
        collection_name=settings.COLLECTION_NAME,
        points=points
    )

def cosine_similarity(vec1, vec2):
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)

def euclidean_distance(vec1, vec2):
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.linalg.norm(v1 - v2)

def search_similar(query_vec: List[float], top_k: int = 4, use_exact: bool = False, 
                   metric: str = "cosine") -> List[Tuple[str, float]]:
    try:
        res = client.scroll(
            collection_name=settings.COLLECTION_NAME,
            with_vectors=True
        )[0]
        
        results = []
        for point in res:
            vec = point.vector
            if metric == "cosine":
                score = cosine_similarity(query_vec, vec)
            elif metric == "euclidean":
                score = -euclidean_distance(query_vec, vec)
            results.append((point.payload.get("text", ""), float(score)))

        results = sorted(results, key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    except Exception as e:
        logging.error(f"Error occurred while searching similar: {e}")
        return []