from typing import List
from fastapi.encoders import jsonable_encoder
from RAG.routers.bookings import create_booking
from ..services.llm_gemini import generate_answer, get_booking_details
from ..schemas import BookingRequest
import logging
from RAG.db import SessionLocal
import sys
import json

logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout  
)

def rag_answer(context_chunks: List[str], question: str) -> str:
    try:
        if detect_booking_intent(question):
            data = get_booking_details(question)
            data = jsonable_encoder(data)
            db = SessionLocal()        
            logging.info("\nHELLO DATA\n")
            logging.info(json.dumps(data))
            booking_response = create_booking(
                BookingRequest(name=data.get("name", ""),
                email=data.get("email", ""),
                date=data.get("date", ""),
                time=data.get("time", ""),),
                db=db
            )
            return booking_response.message
    except Exception as e:
        logging.error(f"Error processing booking intent: {e}")
        
    else:
        return generate_answer(question, context_chunks)

def detect_booking_intent(query: str) -> bool:
    keywords = ["book", "appointment", "reserve", "schedule"]
    return any(k in query.lower() for k in keywords)