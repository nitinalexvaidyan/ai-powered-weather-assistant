# prompts/prompt_builder.py

from datetime import datetime
from tools.registry import TOOL_REGISTRY


def build_tools_prompt() -> str:
    tool_descriptions = []

    for name, meta in TOOL_REGISTRY.items():
        args = ", ".join(meta["args"].keys())
        tool_descriptions.append(
            f"{name}({args}) - {meta['description']}"
        )

    return "\n".join(tool_descriptions)


def build_agent_prompt(context: str, state) -> str:
    # tools = build_tools_prompt()
    tools = state.get("tools", {})

    tool_list = "\n".join([
        f"{name}" for name in tools.keys()
    ])
    return f"""
        You are an AI assistant that decides whether to call a tool or respond directly for weather related queries.
        
        Available Tools:
            {tool_list}

        Output formats:
            1. Tool call:
                {{
                "action": "call_tool",
                "tool_name": "<tool_name>",
                "arguments": {{ ... }}
                }}

            2. Direct response:
                {{
                "action": "respond",
                "message": "<message>"
                }}

        Rules:
        - Only respond to weather related questions.
        - Always return valid JSON and never return text outside JSON.
        - Prefer responding if sufficient information is available instead of fetching the data again.
        - If required info is missing in the user input → ask user
        - Extract date if user asks about future and Pass date in YYYY-MM-DD format
        - Todays date is {datetime.now()}

        Conversation so far:
            {context}

        Decide the next action.
    """