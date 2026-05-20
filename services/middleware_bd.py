from mysql.connector import Error
from result_wrapper import Result


async def validate_special_crud(dict_attribute) -> Result:
    try:
        is_author = None
        user_id = await dict_attribute['dbase'].user_id_exists(dict_attribute['user_id'])
        auth_status = await dict_attribute['dbase'].get_auth_status_user_id(dict_attribute['user_id'])
        is_user_id = user_id is not None
        if auth_status is not None:
            is_author = auth_status.get('auth_status', False) == 1
        res = Result.success((is_user_id, is_author))
    except Error as err:
        res = Result.failure(f'{err}')
    return res


async def less_6_hours(dict_attribute) -> Result:
    try:
        res = Result.success(await dict_attribute['dbase'].less_6_hours(dict_attribute['user_id']))
    except Error as err:
        res = Result.failure(f'{dict_attribute['object_info_user'].ERROR_DATABASE}, {err}')
    return res


async def deactivation(dict_attribute) -> None | str:
    try:
        await dict_attribute['dbase'].deactivation(dict_attribute['user_id'])
    except Error as err:
        return f'{dict_attribute['object_info_user'].ERROR_DATABASE}\n{err}'