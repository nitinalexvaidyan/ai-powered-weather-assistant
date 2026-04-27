# agent/langgraph/state.py --> # AgentState

from typing import TypedDict

class AgentState(TypedDict):
    user_input: str
    decision: dict
    tool_result: str
    final_response: str