from pydantic import BaseModel
from typing import Literal

ChunkingStrategy = Literal["fixed", "by_heading"]

class IngestResponse(BaseModel):
    document_id: int
    n_chunks: int
    chunking_strategy: ChunkingStrategy

class ChatRequest(BaseModel):
    session_id: str
    question: str
    top_k: int = 4
    use_exact: bool = False  
    rerank: bool = False

class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatResponse(BaseModel):
    answer: str
    context_chunks: list[str]
    memory: list[ChatTurn]

class BookingRequest(BaseModel):
    name: str
    email: str
    date: str  
    time: str  

class BookingResponse(BaseModel):
    id: int
    message: str
