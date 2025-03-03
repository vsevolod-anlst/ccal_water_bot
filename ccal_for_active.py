dict_active = {
    "Аэробика":420,
    "Аквааэробика":240,
    "Бодифлекс":260,
    "Гимнастика":480,
    "Скакалка":750
    }


def get_activity_value(activity_name):
    return dict_active.get(activity_name)