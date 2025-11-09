from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .routers import ingest, rag, bookings
from .utils.chunking import make_chunks
from .services.embeddings import Embedder
from .services.vectorstore import search_similar
from .services.memory import add_turn, get_memory
from .utils.rag import rag_answer
from .schemas import ChatTurn
from .config import settings

PMRAG = FastAPI(title="RAG Backend", version="1.0.0")
PMRAG.mount("/static", StaticFiles(directory="RAG/static"), name="static")

PMRAG.include_router(ingest.router)
PMRAG.include_router(rag.router)
PMRAG.include_router(bookings.router)

@PMRAG.get("/healthz")
def health():
    return {"status": "ok"}

@PMRAG.get("/ui", response_class=HTMLResponse)
def serve_ui():
    return FileResponse("RAG/static/ui.html")

@PMRAG.post("/ui/rag")
async def ui_rag(request: Request):
    data = await request.json()
    text = data.get("text", "")
    chunking = data.get("chunking", "fixed")
    try:
        chunks = make_chunks(text, chunking)
        return JSONResponse({"chunks": chunks})
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@PMRAG.post("/ui/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        print("/chat received:", data)
        message = data.get("message", "")
        if not message:
            return JSONResponse({"error": "No message provided."}, status_code=400)
        session_id = "ui-session"
        top_k = 4
        use_exact = False
        embedder = Embedder(model_name=settings.EMBED_MODEL)
        qvec = embedder.encode([message])[0]
        results = search_similar(qvec, top_k=top_k, use_exact=use_exact, metric="cosine")
        context_chunks = [t for t, score in results]
        answer = rag_answer(context_chunks, message)
        add_turn(session_id, "user", message)
        add_turn(session_id, "assistant", answer)
        
        raw_memory = get_memory(session_id)
        safe_memory = []
        for t in raw_memory:
            role = t.get("role", "user")
            content = t.get("content")
            if content is None:
                content = ""
            safe_memory.append(ChatTurn(role=role, content=str(content)))
        return JSONResponse({"response": answer, "context": context_chunks, "memory": [t.dict() for t in safe_memory]})
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
