# agent/langgraph/state.py --> # AgentState

from typing import Dict, TypedDict, List

class AgentState(TypedDict):
    user_input: str
    messages: List[str]        # 🔥 conversation memory
    decision: dict
    tool_result: str
    final_response: str
    trace: List[Dict]   # 🔥 NEW