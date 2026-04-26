# agent/agent.py
import logging
import uuid
from services.llm_service import agent_decision, summarize_memory
from agent.tools import execute_tool
from agent.fallback import fallback_pipeline
from agent.memory import get_memory, update_memory

def run_agent(user_input: str, session_id: str):

    request_id = str(uuid.uuid4())
    trace = []
    memory = get_memory(session_id)
    agent_state = memory["messages"].copy()
    summary = memory["summary"]
    logging.info(f"[{request_id}] Loaded Memory: {agent_state}, Loaded summary: {summary}")
    agent_state.insert(0, f"Summary: {summary}")
    agent_state.append(f"User: {user_input}")

    steps_taken = 0
    used_tools = set()
    max_steps = 3

    try:
        for step in range(max_steps):
            steps_taken += 1

            context = format_agent_state(agent_state)
            logging.info(f"[{request_id}] Step {step} Context:\n{context}")

            decision = agent_decision(context)
            logging.info(f"[{request_id}] Step {step} Decision: {decision}")

            action = decision.get("action")
            step_trace = {
                "step": steps_taken,
                "action": action
            }


            if action == "respond":
                step_trace["message"] = decision.get("message")
                agent_state.append(f"Assistant: {decision.get('message')}")
                new_summary = summarize_memory(summary, agent_state)    # 🔥 Summarize old memory
                update_memory(session_id, agent_state, new_summary)
                return build_response(
                    decision.get("message"),
                    session_id,
                    steps_taken,
                    used_tools,
                    trace
                )

            elif action == "call_tool":
                tool_name = decision.get("tool_name")
                step_trace["tool"] = tool_name
                trace.append(step_trace)

                # 🔐 Prevent repeated tool calls
                if tool_name in used_tools:
                    logging.warning(f"[{request_id}] Tool '{tool_name}' already used. Skipping.")
                    return build_response(
                        "I already fetched that information. Let me respond with what I have.",
                        session_id,
                        steps_taken,
                        used_tools,
                        trace
                    )

                used_tools.add(tool_name)

                tool_result = execute_tool(decision, user_input)
                step_trace["tool_result"] = str(tool_result)[:200]

                # Add structured tool info
                agent_state.append(f"{tool_name} result: {tool_result}")
                update_memory(session_id, agent_state, summary)

            else:
                raise ValueError("Invalid action")
            
        new_summary = summarize_memory(summary, agent_state)
        update_memory(session_id, agent_state, new_summary)
        return build_response(
            "I couldn't fully process that, but here's what I found so far.",
            session_id,
            steps_taken,
            used_tools,
            trace
        )   # graceful exit   
            

    except Exception as e:
        logging.error(f"[{request_id}] Agent failed: {e}")
        return build_response(
            "Something went wrong. Falling back.",
            session_id,
            steps_taken,
            used_tools,
            trace
        )


def format_agent_state(agent_state: list) -> str:
    return "\n".join(agent_state)


def build_response(message, session_id, steps, tools, trace):
    return {
        "response": message,
        "metadata": {
            "session_id": session_id,
            "steps": steps,
            "tools_used": list(tools)
        },
        "trace": trace
    }