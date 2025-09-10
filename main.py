import os
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from memory import (
    get_context, update_context, clear_context,
    get_cached_response, cache_response,
    store_long_term, get_long_term
)

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

app = FastAPI(title="SQL MCP Agent API")
agent = None

SYSTEM_PROMPT = (
    "You are a SQL assistant. Only answer questions related to the table 'tharun111'. "
    "Do not reference any other tables. If the user asks about non-existing tables, "
    "inform them politely that only 'tharun111' is available."
)

class QueryRequest(BaseModel):
    query: str

async def init_agent():
    global agent
    client = MultiServerMCPClient(
        {
            "mysql": {
                "command": "uvx",
                "args": ["--from", "mysql-mcp-server", "mysql_mcp_server"],
                "transport": "stdio",
                "env": {
                    "MYSQL_HOST": MYSQL_HOST,
                    "MYSQL_PORT": MYSQL_PORT,
                    "MYSQL_USER": MYSQL_USER,
                    "MYSQL_PASSWORD": MYSQL_PASSWORD,
                    "MYSQL_DATABASE": MYSQL_DATABASE,
                },
            }
        }
    )
    tools = await client.get_tools()
    model = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct")
    agent = create_react_agent(model, tools)
    print("✅ Agent initialized with MCP + Groq!")

@app.on_event("startup")
async def startup_event():
    await init_agent()


@app.post("/query")
async def query_agent(request: QueryRequest):
    global agent

    # 1. Check Redis cache first
    cached = get_cached_response(request.query)
    if cached:
        return {"response": cached, "cached": True}

    # 2. Build context
    context_messages = get_context()
    user_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + context_messages + [
        {"role": "user", "content": request.query}
    ]

    # 3. Call LLM
    response = await agent.ainvoke({"messages": user_messages})
    reply = response['messages'][-1].content

    # 4. Update memory & cache
    cache_response(request.query, reply)
    update_context(request.query, reply)
    store_long_term(request.query, reply)

    return {"response": reply, "cached": False}

@app.get("/memory") # For Checking long-term memory
async def memory_history():
    return {"history": get_long_term()}

@app.delete("/memory/clear") # For clearing short-term memory
async def clear_memory():
    clear_context()
    return {"message": "Short-term memory cleared."}

@app.get("/health")
def health_check():
    return {"status": "running"}
