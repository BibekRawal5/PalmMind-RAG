from __future__ import annotations
from typing import List, Optional
import google.generativeai as genai
from ..config import settings
import json
import re
import sys
import logging

logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout  
)


genai.configure(api_key=settings.GEMINI_API_KEY)

def build_prompt(
    question: str,
    contexts: List[str],
    chat_history: Optional[List[dict]] = None,
    system: Optional[str] = None,
) -> str:
    
    sys = system or (
        "You are a helpful assistant. Answer using the provided context. "
        "If the answer is not in the context, say you don't have enough information."
    )
    history_text = ""
    if chat_history:
        parts = []
        for turn in chat_history[-10:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            parts.append(f"{role.upper()}: {content}")
        history_text = "\n".join(parts)

    context_block = "\n\n".join([f"- {c}" for c in contexts])

    prompt = f"""{sys}

CHAT HISTORY (most recent last):
{history_text}

CONTEXT:
{context_block}

USER QUESTION:
{question}

INSTRUCTIONS:
- Cite snippets from CONTEXT conversationally (no formal citations needed).
- If insufficient context, say so and ask for clarifying info.
- Be brief and direct.
"""
    return prompt

def generate_answer(
    question: str,
    contexts: List[str],
    chat_history: Optional[List[dict]] = None,
) -> str:
    try:
        prompt = build_prompt(question, contexts, chat_history)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        resp = model.generate_content(prompt)
    except Exception as e:
        logging.error(f"Error generating answer: {e}")
        return f"Sorry, I couldn’t generate a response due to an error. {e}"
    
    if not getattr(resp, "text", None):
        return "Sorry, I couldn’t generate a response."
    return resp.text.strip()


def sanitize_json_string(raw: str) -> str:
    if hasattr(raw, "to_dict"):
        raw = str(raw)  
    
    clean = re.sub(r"^```(json)?\s*|\s*```$", "", raw.strip(), flags=re.IGNORECASE | re.MULTILINE)
    return clean


def get_booking_details(
    question: str, 
    contexts: Optional[List[str]] = None,
    chat_history: Optional[List[dict]] = None,
    system: Optional[str] = None
    ) -> dict:
    
    try:
        sys = system or (
            "You are a concise assistant. Answer using ONLY the provided context. "
            "If the answer is not in the context, say you don't have enough information."
        )
        
        prompt = f""" {sys}
        CRITICAL: You must return ONLY a valid JSON object. Do not include any other text, explanation, or markdown formatting before or after the JSON object.
        
        Based on the user query retreive the following:
        
        name: Name provided for booking
        email: email provided for booking
        date: date provided for booking
        time: time provided for booking
        
        The JSON object must follow this exact structure:
        {{
            "name": "Bibek Rawal",
            "email": "bibek.rawal.589@gmail.com",
            "date": "2025-08-16",
            "time": "13:12"
        }}
        
        USER_QUERY:
        {question}
        """
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        resp = model.generate_content(prompt)
        clean_resp = sanitize_json_string(resp.text)
        logging.info(resp.text)
    
        logging.info(json.dumps(clean_resp))
        return json.loads(clean_resp)
    
    except:
        return {
        "name": "Bibek Rawal",
        "email": "bibek.rawal.589@gmail.com",
        "date": "2025-08-16",
        "time": "13:12"
    }
    
    
    