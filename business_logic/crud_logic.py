from datetime import datetime, date
from decimal import Decimal

from models.models import Workout, Goal, InfoGoal, ViewGoal


def validate_len_string(name_string: str, limitations) -> bool:
    """
    Проверка длины строки на ограничение name_string < limitations
    :param name_string:
    :param limitations:
    :return:
    """
    return len(name_string) <= limitations


def parse_date(str_date: str) -> bool:
    """
    Проверка корректности даты
    :param str_date:
    :return:
    """
    try:
        datetime.strptime(str_date, '%d.%m.%Y')
        return True
    except ValueError:
        return False


def date_in_date_range(str_date: str, model_info: InfoGoal) -> bool:
    """
    Проверка, что дата str_date лежит между датами цели model_info: start_date и end_date
    :param str_date:
    :param model_info:
    :return:
    """
    my_date = datetime.strptime(str_date, '%d.%m.%Y')
    return model_info.start_date <= my_date.date() <= model_info.end_date


def date_is_less_now(str_date: str) -> bool:
    """
    Проверка, что дата str_date меньше либо равна дате сегодня
    :param str_date:
    :return:
    """
    parsed_date = datetime.strptime(str_date, '%d.%m.%Y')
    return parsed_date.date() <= date.today()


def start_date_more_now(start_date: str) -> bool:
    """
    Проверка, что дата str_date меньше либо равна дате сегодня
    :param start_date:
    :return:
    """
    parsed_date = datetime.strptime(start_date, '%d.%m.%Y')
    return date.today() <= parsed_date.date()


def date_workout_less_end_date(str_date: str, end_date: date) -> bool:
    my_date = datetime.strptime(str_date, '%d.%m.%Y')
    return my_date.date() <= end_date


def date_difference(start_date: str, end_date: str) -> bool:
    """
    Проверка, что дата end_date больше даты start_date
    :param start_date:
    :param end_date:
    :return:
    """
    start_date = datetime.strptime(start_date, '%d.%m.%Y')
    end_date = datetime.strptime(end_date, '%d.%m.%Y')
    return start_date.date() < end_date.date()


def is_number_more_zero(number) -> bool:
    """
    Проверка, что number больше нуля
    :param number:
    :return:
    """
    number = float(number)
    return number > 0


def can_convert_to_number(str_value) -> bool:
    """
    Проверка преобразования строки в число.
    :param str_value:
    :return:
    """
    try:
        float(str_value)
        return True
    except ValueError:
        return False


def workout_model_verification(attribute_model: dict, object_info_user) -> set:
    """
    Проверка входных данных условиям модели Workout
    :param attribute_model: словарь атрибутов модели Workout
    :param object_info_user: Объект констант
    :return:
    """
    error_set = set()
    if not validate_len_string(attribute_model['exercise_type'], object_info_user.MAX_LEN_NAME_WORKOUT):
        error_set.add(object_info_user.INVALID_LEN_NAME_WORKOUT)
    if not (can_convert_to_number(attribute_model['quantity']) and is_number_more_zero(attribute_model['quantity'])):
        error_set.add(object_info_user.INVALID_INDICATOR)
    if not validate_len_string(attribute_model['unit'], object_info_user.MAX_LEN_DIMENSION):
        error_set.add(object_info_user.INVALID_LEN_DIMENSION)
    if attribute_model.get('workout_date') is None:
        attribute_model['workout_date'] = date.today().strftime('%d.%m.%Y')
    if parse_date(attribute_model['workout_date']):
        if not date_is_less_now(attribute_model['workout_date']):
            error_set.add(object_info_user.INVALID_DATE_LESS_NOW)
    else:
        error_set.add(object_info_user.INVALID_DATE_WORKOUT)
    return error_set


def create_workout_model(attribute_model: dict, user_id: int) -> Workout:
    """
    Создание объекта Workout для записи в БД
    :param attribute_model: словарь атрибутов модели Workout
    :param user_id: id телеграмм пользователя
    :return:
    """
    attribute_model['quantity'] = float(attribute_model['quantity'])
    attribute_model['register_user_id'] = user_id
    if attribute_model.get('workout_date') is None:
        attribute_model['workout_date'] = date.today()
    else:
        attribute_model['workout_date'] = datetime.strptime(attribute_model['workout_date'], '%d.%m.%Y').date()
    return Workout(**attribute_model)


def goal_model_verification(attribute_model: dict, object_info_user) -> set:
    error_set = set()
    if attribute_model.get('start_date') is None:
        attribute_model['start_date'] = date.today().strftime('%d.%m.%Y')
    if not parse_date(attribute_model['start_date']):
        error_set.add(object_info_user.INVALID_DATE_START)
        return error_set
    if not start_date_more_now(attribute_model['start_date']):
        error_set.add(object_info_user.INVALID_DATE_START)
    if not parse_date(attribute_model['end_date']):
        error_set.add(object_info_user.INVALID_DATE_END)
        return error_set
    if not date_difference(attribute_model['start_date'], attribute_model['end_date']):
        error_set.add(object_info_user.INVALID_DATE_DIFF)
    if not validate_len_string(attribute_model['target_exercise'], object_info_user.MAX_LEN_NAME_WORKOUT):
        error_set.add(object_info_user.INVALID_LEN_NAME_WORKOUT)
    if not (can_convert_to_number(attribute_model['target_quantity']) and is_number_more_zero(
            attribute_model['target_quantity'])):
        error_set.add(object_info_user.INVALID_INDICATOR)
    if not validate_len_string(attribute_model['unit'], object_info_user.MAX_LEN_NAME_WORKOUT):
        error_set.add(object_info_user.INVALID_LEN_DIMENSION)
    return error_set


def create_goal_model(attribute_model: dict, user_id: int) -> Goal:
    """
    Создание объекта Goal для записи в БД
    :param attribute_model: словарь атрибутов объекта Goal
    :param user_id: id пользователя телеграмм
    :return:
    """
    if attribute_model.get('start_date') is None:
        attribute_model['start_date'] = date.today()
    else:
        attribute_model['start_date'] = datetime.strptime(attribute_model['start_date'], '%d.%m.%Y').date()
    attribute_model['end_date'] = datetime.strptime(attribute_model['end_date'], '%d.%m.%Y').date()
    attribute_model['target_quantity'] = float(attribute_model['target_quantity'])
    attribute_model['register_user_id'] = user_id
    return Goal(**attribute_model)


def get_dict_active_goal(list_info_goal: list[dict]) -> dict:
    """
    Из списка готовит словарь {номер по порядку: id цели}
    :param list_info_goal: список активных целей модели class InfoGoal
    :return:
    """
    dict_number_goals = {}
    for index, dict_attribute in enumerate(list_info_goal, start=1):
        if dict_attribute['first_workout'] is None:
            dict_attribute['first_workout'] = '-'
        if dict_attribute['last_workout'] is None:
            dict_attribute['last_workout'] = '-'
        goal = InfoGoal(**dict_attribute)
        index = str(index)
        dict_number_goals[index] = goal
    return dict_number_goals


def workout_model_for_goal_verification(attribute_model: dict, model_info: InfoGoal, object_info_user):
    error_set = set()
    if not (can_convert_to_number(attribute_model['quantity']) and is_number_more_zero(attribute_model['quantity'])):
        error_set.add(object_info_user.INVALID_INDICATOR)
    if attribute_model.get('workout_date') is None:
        attribute_model['workout_date'] = date.today().strftime('%d.%m.%Y')
    if parse_date(attribute_model['workout_date']):
        if not (date_in_date_range(attribute_model['workout_date'], model_info) and
                date_is_less_now(attribute_model['workout_date'])):
            error_set.add(object_info_user.INVALID_DATE_BETWEEN_WORKOUT)
    else:
        error_set.add(object_info_user.INVALID_DATE_WORKOUT)
    return error_set


def create_workout_model_for_goal(user_id: int, model_info: InfoGoal, attribute_model: dict) -> Workout:
    if attribute_model.get('workout_date') is None:
        attribute_model['workout_date'] = date.today().strftime('%d.%m.%Y')
    else:
        attribute_model['workout_date'] = datetime.strptime(attribute_model['workout_date'], '%d.%m.%Y').date()
    workout = Workout(
        workout_date=attribute_model['workout_date'],
        exercise_type=model_info.target_exercise,
        quantity=float(attribute_model['quantity']),
        unit=model_info.unit,
        goal_id=model_info.id_goal,
        register_user_id=user_id
    )
    return workout


def checking_progress_goal(object_attributes):
    workout = InfoGoal(**object_attributes)
    return workout.progress >= 100, workout


def replace_none_attributes(dict_attributes: dict) -> dict:
    if dict_attributes['workout_sessions_count'] == 0:
        dict_attributes['workout_sessions_count'] = '-'
    if dict_attributes['total_quantity'] == 0:
        dict_attributes['total_quantity'] = '-'
    if dict_attributes['max_quantity_per_session'] == 0:
        dict_attributes['max_quantity_per_session'] = '-'
    if dict_attributes['min_quantity_per_session'] == 0:
        dict_attributes['min_quantity_per_session'] = '-'
    if dict_attributes['avg_quantity_per_session'] == 0:
        dict_attributes['avg_quantity_per_session'] = '-'
    if dict_attributes['first_workout'] is None:
        dict_attributes['first_workout'] = '-'
    if dict_attributes['last_workout'] is None:
        dict_attributes['last_workout'] = '-'
    return dict_attributes


def workout_data_serializable(workouts_data: list):
    for dict_attr in workouts_data:
        if isinstance(dict_attr['workout_date'], date):
            dict_attr['workout_date'] = dict_attr['workout_date'].strftime('%d.%m.%Y')
        if isinstance(dict_attr['quantity'], Decimal):
            dict_attr['quantity'] = str(dict_attr['quantity'])


def goal_data_serializable(goal_data: list):
    for dict_attr in goal_data:
        if isinstance(dict_attr['start_date'], date):
            dict_attr['start_date'] = dict_attr['start_date'].strftime('%d.%m.%Y')
        if isinstance(dict_attr['end_date'], date):
            dict_attr['end_date'] = dict_attr['end_date'].strftime('%d.%m.%Y')
        if isinstance(dict_attr['target_quantity'], Decimal):
            dict_attr['target_quantity'] = str(dict_attr['target_quantity'])


def create_goal_model_id_goal(list_goals: list, info_user):
    numbering_of_goal = {}
    for number, attrib_model in enumerate(list_goals, start=1):
        attrib_model['status'] = info_user.STATUS_MAPPING[attrib_model['status']]
        numbering_of_goal[str(number)] = ViewGoal(**attrib_model)
    str_goals = '\n\n'.join(f'номер цели: {key}\nцель: {goal}' for key, goal in numbering_of_goal.items())
    return str_goals, numbering_of_goal


def create_info_goal_model(attrib_model):
    return InfoGoal(**attrib_model)
