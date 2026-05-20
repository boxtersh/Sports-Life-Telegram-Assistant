from mysql.connector import Error
from result_wrapper import Result


async def add_workout(dbase, workout_obj) -> Result:
    try:
        res = await dbase.add_workout(workout_obj)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def get_goals(dbase, user_id, status: str = 'active') -> Result:
    try:
        res = await dbase.get_goals(user_id, status)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def get_progress_by_user_id_id_goal(dbase, user_id, id_goal) -> Result:
    try:
        res = await dbase.get_progress_by_user_id_id_goal(user_id, id_goal)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def add_goal(dbase, goal_model) -> Result:
    try:
        res = await dbase.add_goal(goal_model)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def changing_status_to_expired(dbase) -> Result:
    try:
        res = await dbase.changing_status_to_expired()
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def changing_status_to_achieved(dbase) -> Result:
    try:
        res = await dbase.changing_status_to_achieved()
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def get_all_users_expired_goals(dbase) -> Result:
    try:
        res = await dbase.get_all_users_expired_goals()
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def get_all_users_achieved_goals(dbase) -> Result:
    try:
        res = await dbase.get_all_users_achieved_goals()
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def get_by_user_id_by_status_goals_today(dbase, user_id: int, status: str) -> Result:
    try:
        res = await dbase.get_by_user_id_by_status_goals_today(user_id, status)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def get_date_start_end_target_goal(dbase, user_id, id_goal) -> Result:
    try:
        res = await dbase.get_date_start_end_target_goal(user_id, id_goal)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def changing_status_by_register_user_id_id_goal(dbase, status, user_id, id_goal) -> Result:
    try:
        res = await dbase.changing_status_by_register_user_id_id_goal(status, user_id, id_goal)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def view_workouts_filter(dbase, user_id, target_exercise=None) -> Result:
    try:
        res = await dbase.view_workouts_filter(user_id, target_exercise)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def view_workout_detail(dbase, user_id, target_exercise, goal_id=None) -> Result:
    try:
        res = await dbase.view_workout_detail(user_id, target_exercise, goal_id)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def verification_goal_is_expired(dbase, user_id) -> Result:
    try:
        res = await dbase.verification_goal_is_expired(user_id)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def workouts_no_goal_export_json(dbase, user_id):
    try:
        res = await dbase.workouts_no_goal_export_json(user_id)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def goal_export_json(dbase, user_id):
    try:
        res = await dbase.goal_export_json(user_id)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def workouts_goal_export_json(dbase, user_id):
    try:
        res = await dbase.workouts_goal_export_json(user_id)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def get_all_goals(dbase, user_id: int):
    try:
        res = await dbase.get_all_goals(user_id)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')


async def archived_status(dbase, user_id: int):
    try:
        res = await dbase.archived_status(user_id)
        return Result.success(res)
    except Error as err:
        return Result.failure(f'{err}')
