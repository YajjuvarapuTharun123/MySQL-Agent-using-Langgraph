# Rademade MySQL MCP Server

A FastAPI-based MCP (Multi-Server Control Protocol) agent for MySQL, built using **LangChain MCP adapters**, **LangGraph**, and **ChatGroq**.
This agent provides an API to interact with a SQL database and answer queries related to a specific table.
It now supports short-term memory with Redis and long-term memory with MongoDB, making repeated queries faster and preserving context over time.

The project has been **tested using Postman** for API requests.

---

## Features

- Connects to a MySQL database via MCP server.
- Agent only answers questions about the table `tharun111`.
- Returns polite responses if a query references other tables.
- Memory-Enabled:
-- Redis – Short-term memory for quick retrieval of recent queries/responses.
-- MongoDB – Long-term memory for conversation history and analytics.
- REST API Endpoints:
-- `POST /query` – Ask a query to the SQL agent.
-- GET /health – Check server health status.
- Tested with Postman for API requests.

---

## Tech Stack

- FastAPI – REST API framework
- LangChain MCP Adapters – MCP server integration
- LangGraph – Agent orchestration
- ChatGroq – LLM backend
- Redis – Short-term memory store
- MongoDB – Long-term memory store
- Docker – Containerized deployment

---

## Prerequisites

- Python 3.13
- MySQL server
- Docker (for Redis & MongoDB)
- Postman (optional, for testing)

---

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
GROQ_API_KEY=your_groq_api_key
```

---

---

## Docker Setup (Redis + MongoDB)

Spin up Redis & MongoDB containers using Docker:
```commands
# Run Redis
docker run -d --name redis-mem -p 6379:6379 redis:latest

# Run MongoDB
docker run -d --name mongo-mem -p 27017:27017 mongo:latest

# Check the Container  is running or not
docker ps
```
# Running the Server

## Install dependencies
```command
pip install -r requirements.txt
```

## Run FastAPI server
```command
uvicorn app:app --reload
```

---

# Memory Behavior

## Short-term memory (Redis):
Stores recent user queries and responses. Speeds up repeated questions by avoiding unnecessary LLM calls.

## Long-term memory (MongoDB):
Stores complete conversation history, allowing for context-aware responses across sessions.

---

# Testing with Postman

- Import your FastAPI endpoint (http://127.0.0.1:8000/docs) into Postman.
- Send requests to /query and /health.
- Observe that repeated queries are faster due to Redis caching.

---
