# agent/agent.py
from datetime import datetime
import logging
import uuid
from services.llm_service import agent_decision, summarize_memory
from agent.tools.registry import execute_tool
from agent.memory import get_memory, update_memory

def run_agent(user_input: str, session_id: str):

    request_id = str(uuid.uuid4())
    trace = []

    memory = get_memory(session_id)
    agent_state = memory["messages"].copy()
    summary = memory["summary"]

    logging.info(f"[{request_id}] Loaded Memory: {agent_state}, Summary: {summary}")

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

            # ---------------- LLM DECISION ----------------
            try:
                decision = agent_decision(context)
            except Exception as e:
                logging.error(f"[{request_id}] LLM failure: {e}")

                return build_response(
                    "I'm having trouble understanding your request right now.",
                    session_id,
                    steps_taken,
                    used_tools,
                    trace,
                    {
                        "type": ErrorType.LLM_FAILURE,
                        "message": str(e)
                    }
                )

            logging.info(f"[{request_id}] Step {step} Decision: {decision}")

            action = decision.get("action")

            step_trace = {
                "step": steps_taken,
                "action": action
            }

            # ---------------- RESPOND ----------------
            if action == "respond":
                step_trace["message"] = decision.get("message")
                trace.append(step_trace)

                agent_state.append(f"Assistant: {decision.get('message')}")

                new_summary = summarize_memory(summary, agent_state)

                try:
                    update_memory(session_id, agent_state, new_summary)
                except Exception as e:
                    logging.error(f"[{request_id}] Memory failure: {e}")

                return build_response(
                    decision.get("message"),
                    session_id,
                    steps_taken,
                    used_tools,
                    trace,
                    None
                )

            # ---------------- TOOL CALL ----------------
            elif action == "call_tool":
                tool_name = decision.get("tool_name")
                step_trace["tool"] = tool_name

                # Prevent duplicate tool calls
                if tool_name in used_tools:
                    logging.warning(f"[{request_id}] Tool '{tool_name}' already used. Skipping.")

                    trace.append(step_trace)

                    return build_response(
                        "I already fetched that information. Let me respond with what I have.",
                        session_id,
                        steps_taken,
                        used_tools,
                        trace,
                        None
                    )

                used_tools.add(tool_name)

                try:
                    tool_result = execute_tool(decision, user_input)
                except Exception as e:
                    logging.error(f"[{request_id}] Tool failure: {e}")

                    trace.append(step_trace)

                    return build_response(
                        "I couldn't fetch the required data.",
                        session_id,
                        steps_taken,
                        used_tools,
                        trace,
                        {
                            "type": ErrorType.TOOL_FAILURE,
                            "message": str(e)
                        }
                    )

                step_trace["tool_result"] = str(tool_result)[:200]
                trace.append(step_trace)

                agent_state.append(f"{tool_name} result: {tool_result}")

                try:
                    update_memory(session_id, agent_state, summary)
                except Exception as e:
                    logging.error(f"[{request_id}] Memory failure: {e}")

            # ---------------- UNKNOWN ----------------
            else:
                logging.error(f"[{request_id}] Unknown action")

                trace.append(step_trace)

                new_summary = summarize_memory(summary, agent_state)

                try:
                    update_memory(session_id, agent_state, new_summary)
                except Exception as e:
                    logging.error(f"[{request_id}] Memory failure: {e}")

                return build_response(
                    "Something went wrong.",
                    session_id,
                    steps_taken,
                    used_tools,
                    trace,
                    {
                        "type": ErrorType.UNKNOWN,
                        "message": "Unknown action from LLM"
                    }
                )

        # ---------------- LOOP EXIT ----------------
        return build_response(
            "I couldn't fully process that, but here's what I found so far.",
            session_id,
            steps_taken,
            used_tools,
            trace,
            None
        )

    except Exception as e:
        logging.error(f"[{request_id}] Agent failed: {e}")

        return build_response(
            "Something went wrong. Falling back.",
            session_id,
            steps_taken,
            used_tools,
            trace,
            {
                "type": ErrorType.UNKNOWN,
                "message": str(e)
            }
        )


def format_agent_state(agent_state: list) -> str:
    return "\n".join(agent_state)


def build_response(message, session_id, steps, tools, trace, error=None):
    return {
        "success": error is None,
        "response": message,
        "metadata": {
            "session_id": session_id,
            "steps": steps,
            "tools_used": list(tools)
        },
        "trace": trace,
        "error": error,
        "timestamp": datetime.utcnow().isoformat()
    }


class ErrorType:
    LLM_FAILURE = "LLM_FAILURE"
    TOOL_FAILURE = "TOOL_FAILURE"
    MEMORY_FAILURE = "MEMORY_FAILURE"
    UNKNOWN = "UNKNOWN"