from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from ..db import get_db, Base, engine
from ..models import Document
from ..schemas import IngestResponse, ChunkingStrategy
from ..utils.text_extract import extract_text
from ..utils.chunking import make_chunks
from ..services.embeddings import Embedder
from ..services.vectorstore import ensure_collection, upload_chunks
from ..config import settings

router = APIRouter(prefix="/ingest", tags=["ingestion"])

Base.metadata.create_all(bind=engine)

@router.post("", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkingStrategy = Query("fixed"),
    db: Session = Depends(get_db),
):
    try:
        content = await file.read()
        text, content_type = extract_text(file.filename, content)
        chunks = make_chunks(text, chunking_strategy)
        embedder = Embedder(model_name=settings.EMBED_MODEL)
        vectors = embedder.encode(chunks)
        ensure_collection(dim=len(vectors[0]))
        
        doc = Document(filename=file.filename, content_type=content_type, n_chunks=len(chunks), chunking_strategy=chunking_strategy)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        upload_chunks(chunks, vectors, doc.id)
        return IngestResponse(document_id=doc.id, n_chunks=len(chunks), chunking_strategy=chunking_strategy)
    
    except Exception as e:
        return IngestResponse(document_id=None, n_chunks=0, chunking_strategy=chunking_strategy, error=str(e))