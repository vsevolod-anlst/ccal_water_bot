from get_ccal_for_product import get_food_info
from handlers import load_user_data
from fastapi import HTTPException


async def check_user_data(user_id):
    data = await load_user_data(user_id)

    if data:
        weight = data.get("sex")
        age = data.get("sex")
        sex = data.get("sex")
        sex = data.get("sex")
        sex = data.get("sex")
        sex = data.get("sex")

        return '\n'.join([f"{key}: {value}" for key, value in data.items()])
    else:
        raise HTTPException(status_code=404, detail="User data not found")
    # в роутре 2 дописать что если 404 то показать комадну set профиль и попросить заполнить данные

async def calculation_calorie_without_weather(user_id):
    try:
        data = await check_user_data(user_id)

        calories_without_acvite_and_sex = 10 * data.get("weight") + 6.25 * data.get("age") - 5 * data.get("age")

        if data.get("sex") == "Муж": calories_without_active = calories_without_acvite_and_sex * 1.2
        else: calories_without_active = calories_without_acvite_and_sex

        if data.get("cnt_active_min_for_day") == 0: calories_with_active = calories_without_active
        else: calories_with_active = calories_without_active * data.get("cnt_active_min_for_day") * 300/60 # усредненная активность в вакууме

        if data.get("target") == "Сохранить вес":  calories_with_target = calories_with_active
        elif data.get("target") == "Набрать вес": calories_with_target = calories_with_active * 1.2
        else: calories_with_target = calories_with_active * 0.8

        return calories_with_target
    except HTTPException as e:
        return str(e)


async def calculation_water_without_weather(user_id):
    try:
        data = await check_user_data(user_id)




    user_data = {
        "city": data.get("city"),
    }

