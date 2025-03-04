dict_active = {
    "Аэробика":420,
    "Аквааэробика":240,
    "Бодифлекс":260,
    "Гимнастика":480,
    "Скакалка":750
    }


async def get_activity_value(activity_name):
    activity_name_lower = activity_name.lower()
    dict_active_lower = {key.lower(): value for key, value in dict_active.items()}

    if activity_name_lower in dict_active_lower:
        return dict_active_lower[activity_name_lower]

    else:
        activities_list = "\n".join(dict_active.keys())
        raise ValueError(
            f"Активность '{activity_name}' не найдена в списке активностей.\n"
            f"Доступные активности:\n{activities_list}\n\n"
            f"Введите одну из доступных активностей"
        )