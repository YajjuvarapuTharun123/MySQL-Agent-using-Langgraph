import json
import redis
from pymongo import MongoClient
from datetime import datetime
import os


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "sql_mcp_memory")


redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
memory_collection = mongo_db["conversation_history"]


# --- SHORT-TERM MEMORY ---
def get_context():
    data = redis_client.get("conversation_context")
    return json.loads(data) if data else []

def update_context(user_msg, assistant_msg, expire_seconds=300):
    context = get_context()
    context.append({"role": "user", "content": user_msg})
    context.append({"role": "assistant", "content": assistant_msg})
    redis_client.set("conversation_context", json.dumps(context), ex=expire_seconds)

def clear_context():
    redis_client.delete("conversation_context")

# --- RESPONSE CACHE ---
def get_cached_response(query):
    key = f"response_cache:{query.strip().lower()}"
    return redis_client.get(key)

def cache_response(query, response, ttl=300):
    key = f"response_cache:{query.strip().lower()}"
    redis_client.set(key, response, ex=ttl)

# --- LONG-TERM MEMORY (Mongo) ---
def store_long_term(user_query, assistant_reply):
    memory_collection.insert_one({
        "timestamp": datetime.utcnow(),
        "user_query": user_query,
        "assistant_reply": assistant_reply
    })

def get_long_term():
    return list(memory_collection.find({}, {"_id": 0}))
