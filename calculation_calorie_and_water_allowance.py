from get_ccal_for_product import get_food_info
from fastapi import HTTPException

from work_with_json_file import load_user_data_details



async def calculation_calorie_without_weather(user_id):
    user_id = str(user_id)
    result = await load_user_data_details(user_id)

    if isinstance(result, tuple):
        sex, name, age, weight, height, city, target = await load_user_data_details(user_id)

        calories_without_acvite_and_sex = 10 * weight + 6.25 * height - 5 * age

        if sex == "Муж": calories_without_active = calories_without_acvite_and_sex * 1.2
        else: calories_without_active = calories_without_acvite_and_sex


        if target == "Сохранить вес":  calories_with_target = calories_without_active
        elif target == "Набрать вес": calories_with_target = calories_without_active * 1.2
        else: calories_with_target = calories_without_active * 0.8

        return calories_with_target



async def calculation_water_without_weather(user_id):
    user_id = str(user_id)
    result = await load_user_data_details(user_id)

    if isinstance(result, tuple):
        sex, name, age, weight, height, city, target = await load_user_data_details(user_id)

        water_without_weather_and_target = 30 * weight + 500

        if target == "Сохранить вес": water_without_weather = water_without_weather_and_target
        else: water_without_weather = water_without_weather_and_target * 1.2

        return water_without_weather


