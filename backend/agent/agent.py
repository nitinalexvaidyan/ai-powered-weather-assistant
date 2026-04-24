# agent/agent.py
import logging
import uuid
from services.llm_service import agent_decision
from agent.tools import handle_tool_call
from agent.fallback import fallback_pipeline

def run_agent(user_input: str):

    request_id = str(uuid.uuid4())

    try:
        logging.info(f"[{request_id}] Incoming query: {user_input}")

        decision = agent_decision(user_input)
        logging.info(f"[{request_id}] Agent decision: {decision}")

        action = decision.get("action")

        if action == "respond":
            return {"response": decision.get("message")}

        elif action == "call_tool":
            return handle_tool_call(decision, user_input, request_id)

        else:
            raise ValueError("Invalid action")

    except Exception as e:
        logging.error(f"[{request_id}] Agent failed: {e}")
        return fallback_pipeline(user_input)