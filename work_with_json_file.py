import json
import os
import aiofiles
from datetime import datetime


from get_weather import get_temp


file_path='user_data.json'


if not os.path.exists(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump({}, file, ensure_ascii=False, indent=4)


async def save_user_data(user_id, user_data, file_path='user_data.json'):
    data = {}
    try:
        if os.path.exists(file_path):
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                try:
                    file_content = await file.read()
                    data = json.loads(file_content)
                except json.JSONDecodeError:
                    data = {}

        data[user_id] = user_data

        async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
            await file.write(json.dumps(data, ensure_ascii=False, indent=4))
    except (OSError, IOError) as e:
        print(f"Ошибка при работе с файлом {file_path}: {e}")


async def get_user_data(user_id, file_path='user_data.json'):
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            file_content = await file.read()
            data = json.loads(file_content)

            if user_id in data:
                return data[user_id]
            else:
                return f"Пользователь с ID {user_id} не найден."
    except FileNotFoundError:
        return "Файл с данными не найден."
    except json.JSONDecodeError:
        return "Файл поврежден или пуст."



async def load_user_data_details(user_id):
    user_data = await get_user_data(user_id)

    if isinstance(user_data, dict):
        sex = user_data.get("sex")
        name = user_data.get("name")
        age = user_data.get("age")
        weight = user_data.get("weight")
        height = user_data.get("height")
        city = user_data.get("city")
        cnt_active_min_for_day = user_data.get("cnt_active_min_for_day")
        target = user_data.get("target")


        return sex, name, age, weight, height, city, cnt_active_min_for_day, target
    else:
        return user_data


async def load_user_data_ccal_and_water(user_id):
    user_data = await get_user_data(user_id)

    if isinstance(user_data, dict):
        sex = user_data.get("sex")
        name = user_data.get("name")
        age = user_data.get("age")
        weight = user_data.get("weight")
        height = user_data.get("height")
        city = user_data.get("city")
        cnt_active_min_for_day = user_data.get("cnt_active_min_for_day")
        target = user_data.get("target")
        calculation_calorie = user_data.get("calculation_calorie")
        calculation_water_without_weather = user_data.get("calculation_water_without_weather")

        return sex, name, age, weight, height, city, cnt_active_min_for_day, target, calculation_calorie, calculation_water_without_weather
    else:
        return user_data


async def delete_user_data(user_id, file_path='user_data.json'):
    if not os.path.exists(file_path):
        print("Файл не найден!")
        return "Файл с данными не найден."

    try:
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
            file_content = await file.read()
            print("Содержимое файла:", file_content)
            data = json.loads(file_content)
            print("Загруженные данные:", data)

        if str(user_id) in data:
            del data[str(user_id)]

            async with aiofiles.open(file_path, mode='w', encoding='utf-8') as file:
                await file.write(json.dumps(data, ensure_ascii=False, indent=4))

            return "Ваши данные удалены!"
        else:
            print(f"Пользователь {user_id} не найден в данных.")
            return f"Пользователь с ID {user_id} не найден."
    except json.JSONDecodeError:
        print("Ошибка чтения JSON!")
        return "Файл поврежден или имеет неверный формат."


async def log_water(user_id, amount):

    user_data = await get_user_data(user_id)
    print("Полученные данные пользователя:", user_data)
    if not isinstance(user_data, dict):
        return user_data

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")

    if "log" not in user_data:
        user_data["log"] = {}

    if current_date not in user_data["log"]:
        required_water = user_data.get("calculation_water_without_weather", 3300.0)
        user_data["log"][current_date] = {
            "required_water": required_water,
            "intake_log": [],
            "remaining_water": required_water,
            "high_temp_detected": False  # Признак жаркого дня
        }

    city_name = user_data.get("city")
    if city_name and not user_data["log"][current_date]["high_temp_detected"]:
        temp = await get_temp(city_name)
        if isinstance(temp, (int, float)) and temp > 25:
            user_data["log"][current_date]["required_water"] += 500.0
            user_data["log"][current_date]["remaining_water"] += 500.0
            user_data["log"][current_date]["high_temp_detected"] = True

    user_data["log"][current_date]["intake_log"].append({
        "time": current_time,
        "amount": amount
    })

    user_data["log"][current_date]["remaining_water"] -= amount
    if user_data["log"][current_date]["remaining_water"] < 0:
        user_data["log"][current_date]["remaining_water"] = 0

    await save_user_data(user_id, user_data)
    print(f"Данные о воде для пользователя {user_id} успешно сохранены.")
    return f"Данные о воде для пользователя {user_id} успешно сохранены."