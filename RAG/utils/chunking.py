import re
from typing import List

def chunk_fixed(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    try:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = words[i:i+chunk_size]
            chunks.append(' '.join(chunk))
            i += chunk_size - overlap if chunk_size - overlap > 0 else chunk_size
    except Exception as e:
        print(f"Error during fixed chunking: {e}")
        return [text]
    return [c for c in chunks if c.strip()]


def chunk_by_sentence(text: str, chunk_size: int = 10, overlap: int = 1) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    i = 0
    while i < len(sentences):
        chunk = sentences[i:i+chunk_size]
        chunks.append(' '.join(chunk))
        i += chunk_size - overlap if chunk_size - overlap > 0 else chunk_size
    return [c for c in chunks if c.strip()]

def make_chunks(text: str, strategy: str) -> List[str]:
    try:
        if strategy == "fixed":
            return chunk_fixed(text)
        elif strategy == "by_sentence":
            return chunk_by_sentence(text)
        else:
            raise ValueError("Unknown chunking strategy")
    except Exception as e:
        print(f"Error during chunking strategy selection: {e}. Falling back to Fixed chunk.")
        return chunk_fixed(text)