import json
import logging
import re

def safe_parse_json(text: str):
    try:
        return json.loads(text)
    except:
        logging.warning("Raw LLM output not valid JSON")

        # Extract JSON using regex
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                logging.error("Failed to parse extracted JSON")

        return None