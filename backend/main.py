from datetime import datetime
import logging
from fastapi import FastAPI
from agent.agent import run_agent
from agent.langgraph import runner

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
def home():
    return {
        "success": True,
        "response": "Welcome to homepage",
        "error": None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/weather")
def weather(query: str, session_id: str):
    return run_agent(query, session_id)


@app.get("/ask")
def ask(query: str, session_id: str):
    return runner.run_langgraph_agent(query, session_id)