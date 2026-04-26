# agent/memory.py

memory_store = {}
MAX_MEMORY_LENGTH = 10

def get_memory(session_id: str):
    return memory_store.get(session_id, [])


def update_memory(session_id: str, agent_state: list):
    trimmed_state = agent_state[-MAX_MEMORY_LENGTH:]    # Keep only last N messages
    memory_store[session_id] = trimmed_state