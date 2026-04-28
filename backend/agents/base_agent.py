class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    def run(self, query: str, session_id: str):
        raise NotImplementedError