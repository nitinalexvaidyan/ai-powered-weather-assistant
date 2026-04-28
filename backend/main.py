from datetime import datetime
import logging
from fastapi import FastAPI
from agents.router.router_agent import RouterAgent

router = RouterAgent()

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


@app.get("/ask")
def ask(query: str, session_id: str):
    return router.route(query, session_id)