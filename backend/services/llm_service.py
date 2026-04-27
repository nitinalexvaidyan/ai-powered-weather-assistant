# services/llm_service.py
import json
import time
import requests
import os
import logging
from dotenv import load_dotenv
from utils.parser import safe_parse_json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
logging.info(f"GEMINI_API_KEY: {GEMINI_API_KEY}")


# -------------------------------
# 🔹 Core Gemini Caller (with retry + backoff)
# -------------------------------
def call_gemini(prompt: str, retries=4) -> str:
    models = [ "gemini-3.1-flash-lite-preview", "gemini-2.5-flash-lite", "gemini-2.5-flash"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{models[1]}:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    for attempt in range(retries):
        try:
            timeout = 20 + attempt * 2  # 🔥 increase timeout

            response = requests.post(url, json=payload, timeout=timeout)

            # 🔥 Handle rate limit
            if response.status_code == 429:
                wait = 2 ** attempt
                logging.warning(f"429 Rate limit. Retry in {wait}s")
                time.sleep(wait)
                continue

            # 🔥 Handle server issues
            if response.status_code >= 500:
                wait = 2 ** attempt
                logging.warning(f"{response.status_code} Server error. Retry in {wait}s")
                time.sleep(wait)
                continue

            response.raise_for_status()

            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']

        except requests.exceptions.Timeout:
            wait = 2 ** attempt
            logging.warning(f"Timeout. Retry in {wait}s")
            time.sleep(wait)

        except Exception as e:
            logging.error(f"Gemini failed (attempt {attempt}): {e}")
            time.sleep(1)

    raise Exception("Gemini failed after retries")


# -------------------------------
# 🔹 Agent Decision
# -------------------------------
def agent_decision(context: str, retries: int = 1) -> dict:
    prompt = build_agent_prompt(context)

    for attempt in range(retries + 1):
        try:
            raw_text = call_gemini(prompt)
            logging.info(f"[LLM RAW] {raw_text}")

            cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = safe_parse_json(cleaned_text)

            if not parsed:
                raise ValueError("Invalid JSON from LLM")

            logging.info(f"[LLM PARSED] {parsed}")
            return parsed

        except Exception as e:
            logging.warning(f"LLM decision attempt {attempt} failed: {e}")

    raise Exception("LLM decision failed after retries")


# -------------------------------
# 🔹 Final Response Generator
# -------------------------------
def generate_final_response(user_input: str, weather_data: str) -> str:
    try:
        prompt = build_final_response_prompt(user_input, weather_data)
        raw_text = call_gemini(prompt)
        return raw_text.strip()

    except Exception as e:
        logging.error(f"Final response generation failed: {e}")
        return "I couldn't process the advice properly, but weather data is available."


# -------------------------------
# 🔹 Prompt Builders
# -------------------------------
def build_agent_prompt(context: str) -> str:
    return f"""
        You are an AI assistant that decides whether to call a tool or respond directly for weather related queries.

        You must ALWAYS return valid JSON.
        Do NOT return text outside JSON.
        You are supposed to respond to only weather related questions.

        Available Tools:

        1. get_weather
        Description: Get weather for a city
        Arguments:
        - location (string)

        2. weather_advice
        Description: Provide advice based on weather data and user query
        Arguments:
        - weather_data (string)
        - user_query (string)

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
        - Always return valid JSON
        - Use get_weather when weather data is needed
        - Use weather_advice when user asks for suggestions
        - If weather data is already available, DO NOT call get_weather again
        - Do NOT call the same tool repeatedly
        - Prefer responding if sufficient information is available
        - If required info is missing → ask user

        Conversation so far:
        {context}

        Decide the next action.
    """


def build_final_response_prompt(user_input: str, weather_data: str) -> str:
    return f"""
        User asked:
        "{user_input}"

        Weather data:
        {weather_data}

        Provide clear, short advice.
    """


def summarize_memory(old_summary: str, new_messages: list) -> str:
    try:
        prompt = f"""
            Existing summary:
            {old_summary}

            New conversation:
            {chr(10).join(new_messages)}

            Update the summary concisely.
            Keep important details like location, user intent, and context.
        """

        return call_gemini(prompt).strip()

    except Exception as e:
        logging.error(f"Summarization failed: {e}")
        return old_summary