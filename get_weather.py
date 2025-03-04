import aiohttp
import asyncio
import os

from dotenv import load_dotenv

load_dotenv()
api_weather_key = os.getenv('API_WEATHER_KEY')



async def get_temp(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_weather_key}&units=metric"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                if "main" in data and "temp" in data["main"]:
                    temp = data['main']['temp']
                    return temp
                else:
                    return f"Ошибка: {data.get('message', 'Неизвестная ошибка')}"
    except aiohttp.ClientResponseError as http_err:
        if response.status == 401:
            return "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."
        return f"HTTP ошибка: {http_err}"
    except aiohttp.ClientConnectionError as conn_err:
        return f"Ошибка соединения: {conn_err}"
    except aiohttp.ClientTimeout as timeout_err:
        return f"Ошибка таймаута: {timeout_err}"
    except aiohttp.ClientError as req_err:
        return f"Ошибка запроса: {req_err}"
