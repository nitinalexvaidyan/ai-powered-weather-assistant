# agent/memory.py

memory_store = {}

def get_memory(session_id: str):
    return memory_store.get(session_id, [])


def update_memory(session_id: str, agent_state: list):
    memory_store[session_id] = agent_state