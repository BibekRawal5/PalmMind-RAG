import redis
import json
from ..config import settings
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def add_turn(session_id: str, role: str, content: str, max_turns: int = 20):
    key = f"chat:{session_id}"
    r.rpush(key, json.dumps({"role": role, "content": content}))
    r.ltrim(key, -max_turns, -1)

def get_memory(session_id: str) -> list[dict]:
    key = f"chat:{session_id}"
    turns = r.lrange(key, 0, -1)
    return [json.loads(t) for t in turns]

def clear_memory(session_id: str):
    r.delete(f"chat:{session_id}")
