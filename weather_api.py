# weather_api.py

import requests
from config import OPENWEATHER_API_KEY

def get_weather(city="Madrid"):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if response.status_code != 200:
            print("Error API:", data)
            return None, None

        temp = data["main"]["temp"]
        humedad = data["main"]["humidity"]
        return temp, humedad

    except Exception as e:
        print("Error al obtener datos del clima:", e)
        return None, None
