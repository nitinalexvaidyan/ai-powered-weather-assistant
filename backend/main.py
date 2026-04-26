import logging
from fastapi import FastAPI
from agent.agent import run_agent

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
def home():
    return {"success": True, "message": "Welcome to homepage"}

@app.get("/weather")
def weather(query: str, session_id: str):
    return run_agent(query, session_id)