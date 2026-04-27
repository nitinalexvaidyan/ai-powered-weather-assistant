# agent/langgraph/memory_store.py

memory_store = {}

MAX_MESSAGES = 6


def get_session_memory(session_id: str):
    return memory_store.get(session_id, {
        "messages": [],
        "trace": []
    })


def update_session_memory(session_id: str, messages: list, trace: list):
    memory_store[session_id] = {
        "messages": messages[-MAX_MESSAGES:],  # sliding window
        "trace": trace[-10:]  # optional limit
    }