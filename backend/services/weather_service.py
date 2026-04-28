# services/weather_service.py

import requests
import os
import logging
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
logging.info(f"OPENWEATHER_API_KEY: {OPENWEATHER_API_KEY}")

def get_weather(location: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"

    response = requests.get(url) 
    result = response.json()
    logging.info(f"weather: {result}")
    return result

def get_forecast(location: str, date: str):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()

    # 🔥 simple filtering (first version)
    for item in data.get("list", []):
        if date in item["dt_txt"]:
            return item

    return "No forecast available for that date"