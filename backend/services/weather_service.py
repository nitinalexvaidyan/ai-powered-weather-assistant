# services/weather_service.py

import requests
import os
import logging
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
logging.info(f"API_KEY: {API_KEY}")

def get_weather(location: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"

    response = requests.get(url) 
    result = response.json()
    logging.info(f"weather: {result}")
    return result