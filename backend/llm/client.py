# services/llm_service.py
import json
import time
import requests
import os
import logging
from dotenv import load_dotenv
from utils.parser import safe_parse_json
from services.cache_service import get_cache, set_cache, build_cache_key
from services.circuit_breaker import is_circuit_open, record_failure, record_success


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
logging.info(f"GEMINI_API_KEY: {GEMINI_API_KEY}")


# -------------------------------
# 🔹 Core Gemini Caller (with retry + backoff)
# -------------------------------
def call_gemini(prompt: str, retries=3, cache_ttl=900) -> str:
    # 🔴 Step 1: Circuit check
    if is_circuit_open():
        print("[CIRCUIT OPEN] Skipping LLM call")
        raise Exception("LLM service temporarily unavailable")
    
    cache_key = build_cache_key("llm", prompt)

    # 🔥 Step 1: Check cache
    cached = get_cache(cache_key)
    if cached:
        print(f"[LLM CACHE HIT]")
        return cached
    
    models = [ "gemini-3.1-flash-lite-preview", "gemini-2.5-flash-lite", "gemini-2.5-flash"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{models[0]}:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=25)

            if response.status_code == 429:
                time.sleep(2 ** attempt)
                continue

            if response.status_code >= 500:
                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()

            data = response.json()
            result = data['candidates'][0]['content']['parts'][0]['text']
            
            record_success()    # ✅ success

            # 🔥 Step 2: Store in cache
            set_cache(cache_key, result, ttl=cache_ttl)

            return result

        except Exception:
            time.sleep(1)

    raise Exception("Gemini failed after retries")


# -------------------------------
# 🔹 Agent Decision
# -------------------------------
def agent_decision(prompt: str, retries: int = 1) -> dict:

    for attempt in range(retries + 1):
        try:
            raw_text = call_gemini(prompt, cache_ttl=900)
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

        return call_gemini(prompt, cache_ttl=900).strip()

    except Exception as e:
        logging.error(f"Summarization failed: {e}")
        return old_summary