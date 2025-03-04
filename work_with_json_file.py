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
            print(f"Данные пользователя {user_id} успешно сохранены.")
            return True
    except (OSError, IOError) as e:
        print(f"Ошибка при работе с файлом {file_path}: {e}")
        return False


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
        target = user_data.get("target")


        return sex, name, age, weight, height, city, target
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
        target = user_data.get("target")
        calculation_calorie = user_data.get("calculation_calorie")
        calculation_water_without_weather = user_data.get("calculation_water_without_weather")

        return sex, name, age, weight, height, city, target, calculation_calorie, calculation_water_without_weather
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
            "remaining_water": required_water,
            "high_temp_detected": False,
            "intake_log": [],
            "food_log": [],
            "total_calories": 0
        }
    else:
        if "high_temp_detected" not in user_data["log"][current_date]:
            user_data["log"][current_date]["high_temp_detected"] = False
        if "required_water" not in user_data["log"][current_date]:
            user_data["log"][current_date]["required_water"] = user_data.get("calculation_water_without_weather", 3300.0)
        if "remaining_water" not in user_data["log"][current_date]:
            user_data["log"][current_date]["remaining_water"] = user_data["log"][current_date]["required_water"]
        if "intake_log" not in user_data["log"][current_date]:
            user_data["log"][current_date]["intake_log"] = []

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


async def log_food(user_id, product_name, food_weight, food_ccal_per_100g):

    user_data = await get_user_data(user_id)
    print("Полученные данные пользователя:", user_data)
    if not isinstance(user_data, dict):
        return user_data

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")

    if "log" not in user_data:
        user_data["log"] = {}

    if current_date not in user_data["log"]:
        user_data["log"][current_date] = {
            "food_log": [],
            "total_calories": 0
        }
    else:
        # Если лог за текущую дату есть, проверяем наличие food_log
        if "food_log" not in user_data["log"][current_date]:
            user_data["log"][current_date]["food_log"] = []
        # Также проверяем наличие total_calories
        if "total_calories" not in user_data["log"][current_date]:
            user_data["log"][current_date]["total_calories"] = 0

    calories = (food_ccal_per_100g / 100) * food_weight

    user_data["log"][current_date]["food_log"].append({
        "time": current_time,
        "name": product_name,
        "weight": food_weight,
        "calories": calories
    })

    user_data["log"][current_date]["total_calories"] += calories

    await save_user_data(user_id, user_data)
    print(f"Данные о поедании пищи для пользователя {user_id} успешно сохранены.")
    return f"Данные о поедании пищи для пользователя {user_id} успешно сохранены."



async def log_activity(user_id, activity_name, burned_calories, minutes):
    user_data = await get_user_data(user_id)
    print("Полученные данные пользователя:", user_data)

    if not isinstance(user_data, dict):
        return None, user_data

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")

    if "log" not in user_data:
        user_data["log"] = {}

    if current_date not in user_data["log"]:
        user_data["log"][current_date] = {
            "activity_log": [],
            "total_burned_calories": 0,
            "required_water": user_data.get("calculation_water_without_weather", 0)  # Устанавливаем из user_data
        }
    else:
        if "required_water" not in user_data["log"][current_date]:
            user_data["log"][current_date]["required_water"] = user_data.get("calculation_water_without_weather", 0)

    user_data["log"][current_date]["activity_log"].append({
        "time": current_time,
        "name": activity_name,
        "minutes": minutes,
        "burned_calories": burned_calories
    })

    user_data["log"][current_date]["total_burned_calories"] += burned_calories

    additional_water = (200 * minutes) / 30  # Рассчитываем добавляемую воду
    user_data["log"][current_date]["required_water"] += additional_water

    await save_user_data(user_id, user_data)

    print(f"Данные об активности для пользователя {user_id} успешно сохранены.")
    return f"Данные об активности для пользователя {user_id} успешно сохранены."


async def get_daily_progress(user_id):
    user_data = await get_user_data(user_id)
    print("Полученные данные пользователя:", user_data)

    if not isinstance(user_data, dict):
        return user_data

    current_date = datetime.now().strftime("%Y-%m-%d")

    daily_log = user_data.get("log", {}).get(current_date, {})
    if not daily_log:
        return None, "Данные за текущий день отсутствуют."

    total_burned_calories = daily_log.get("total_burned_calories", 0)
    total_calories = daily_log.get("total_calories", 0)
    calculation_calorie = user_data.get("calculation_calorie", 0)
    calculation_calorie = round(calculation_calorie, 1)
    required_water = daily_log.get("required_water", 0)
    remaining_water = daily_log.get("remaining_water", 0)

    calories_to_eat = calculation_calorie + total_burned_calories - total_calories
    water_drinked = required_water - remaining_water

    progress_data = {
        "total_burned_calories": total_burned_calories,
        "total_calories": total_calories,
        "calories_to_eat": calories_to_eat,
        "remaining_water": remaining_water,
        "water_drinked": water_drinked,
        "calculation_calorie": calculation_calorie
    }

    return progress_data, None