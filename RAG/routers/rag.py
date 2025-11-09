from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..schemas import ChatRequest, ChatResponse, ChatTurn
from ..services.embeddings import Embedder
from ..services.vectorstore import search_similar
from ..services.memory import add_turn, get_memory
from ..utils.rag import rag_answer
from ..config import settings

router = APIRouter(prefix="/api/chat", tags=["conversational-rag"])

@router.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    
    embedder = Embedder(model_name=settings.EMBED_MODEL)
    qvec = embedder.encode([req.question])[0]
    
    results = search_similar(qvec, top_k=req.top_k, use_exact=req.use_exact, metric="cosine")
    context_chunks = [t for t, score in results]
    
    answer = rag_answer(context_chunks, req.question)
    
    add_turn(req.session_id, "user", req.question)
    add_turn(req.session_id, "assistant", answer)
    memory = [ChatTurn(**t) for t in get_memory(req.session_id)]
    
    return ChatResponse(answer=answer, context_chunks=context_chunks, memory=memory)
