memory_store = {}
MAX_MEMORY_LENGTH = 6  # reduce because we now have summary

def get_memory(session_id: str):
    return memory_store.get(session_id, {
        "messages": [],
        "summary": ""
    })


def update_memory(session_id: str, messages: list, summary: str):
    memory_store[session_id] = {
        "messages": messages[-MAX_MEMORY_LENGTH:],
        "summary": summary
    }