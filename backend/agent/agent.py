# agent/agent.py
import logging
import uuid
from services.llm_service import agent_decision, summarize_memory
from agent.tools import execute_tool
from agent.fallback import fallback_pipeline
from agent.memory import get_memory, update_memory

def run_agent(user_input: str, session_id: str):

    request_id = str(uuid.uuid4())

    memory = get_memory(session_id)
    agent_state = memory["messages"].copy()
    summary = memory["summary"]
    logging.info(f"[{request_id}] Loaded Memory: {agent_state}, Loaded summary: {summary}")
    agent_state.insert(0, f"Summary: {summary}")
    agent_state.append(f"User: {user_input}")

    used_tools = set()
    max_steps = 3

    try:
        for step in range(max_steps):

            context = format_agent_state(agent_state)
            logging.info(f"[{request_id}] Step {step} Context:\n{context}")

            decision = agent_decision(context)
            logging.info(f"[{request_id}] Step {step} Decision: {decision}")

            action = decision.get("action")

            if action == "respond":
                agent_state.append(f"Assistant: {decision.get('message')}")
                new_summary = summarize_memory(summary, agent_state)    # 🔥 Summarize old memory
                update_memory(session_id, agent_state, new_summary)
                return {"response": decision.get("message")}

            elif action == "call_tool":
                tool_name = decision.get("tool_name")

                # 🔐 Prevent repeated tool calls
                if tool_name in used_tools:
                    logging.warning(f"[{request_id}] Tool '{tool_name}' already used. Skipping.")
                    return {"response": "I already fetched that information. Let me respond with what I have."}

                used_tools.add(tool_name)

                tool_result = execute_tool(decision, user_input)

                # Add structured tool info
                agent_state.append(f"{tool_name} result: {tool_result}")
                update_memory(session_id, agent_state, summary)

            else:
                raise ValueError("Invalid action")
            
        new_summary = summarize_memory(summary, agent_state)
        update_memory(session_id, agent_state, new_summary)
        return {"response": "I couldn't fully process that, but here's what I found so far."}   # graceful exit   
       

    except Exception as e:
        logging.error(f"[{request_id}] Agent failed: {e}")
        return fallback_pipeline(user_input)


def format_agent_state(agent_state: list) -> str:
    return "\n".join(agent_state)