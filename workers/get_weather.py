from scint.core.worker import Worker
from datetime import datetime

import aiohttp

from scint.core.config import OPENWEATHER_API_KEY
from scint.core.memory import Message
from scint.services.logger import log

get_weather = Worker(
    name="get_weather",
    purpose="You are a weather retrieval function for Scint, an intelligent assistant.",
    description="Use this function to get weather data for the specified city.",
    params={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city name.",
            },
        },
    },
    req=["city"],
)


async def format_weather_message(response):
    main_data = response.get("main", {})
    wind_data = response.get("wind", {})
    clouds_data = response.get("clouds", {})
    sys_data = response.get("sys", {})
    sunrise = datetime.utcfromtimestamp(sys_data.get("sunrise", 0)).strftime("%H:%M:%S")
    sunset = datetime.utcfromtimestamp(sys_data.get("sunset", 0)).strftime("%H:%M:%S")

    parsed_data = (
        f"Current Temp: {main_data.get('temp')}°C\n"
        f"High: {main_data.get('temp_max')}°C\n"
        f"Low: {main_data.get('temp_min')}°C\n"
        f"Feels Like: {main_data.get('feels_like')}°C\n"
        f"Pressure: {main_data.get('pressure')} hPa\n"
        f"Humidity: {main_data.get('humidity')}%\n"
        f"Wind Speed: {wind_data.get('speed')} m/s\n"
        f"Cloud Coverage: {clouds_data.get('all')}%\n"
        f"Sunrise: {sunrise}\n"
        f"Sunset: {sunset}"
    )

    return Message(role="system", content=parsed_data, name="get_weather")


async def get_weather(city):
    log.info(f"Calling OpenWeather API.")
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            data = await response.json()

            if response.status == 200:
                reply = await format_weather_message(data)
                return reply

            else:
                log.error(f"Error fetching weather.")
                return
