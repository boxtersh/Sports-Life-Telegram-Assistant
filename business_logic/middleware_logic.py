from aiogram.types import Message, CallbackQuery
from services import middleware_bd
from result_wrapper import Result


def validate_event(event) -> Result[tuple[int, str] | tuple[None, None]]:
    user_id = None
    message_text = None
    if isinstance(event, Message) and event.from_user.id:
        if event.text:
            user_id = event.from_user.id
            message_text = event.text
    elif isinstance(event, CallbackQuery) and event.from_user.id:
        user_id = event.from_user.id
        message_text = event.data
    return Result.success((user_id, message_text))


async def validate_pass_handler_special(dict_attribute) -> None:
    result = await middleware_bd.validate_special_crud(dict_attribute)
    if result.success:
        is_login, is_author = result.value
        if not is_login:
            dict_attribute['data']['no_reg'] = dict_attribute['object_info_user'].NOT_REGISTER
        elif not is_author:
            dict_attribute['data']['no_auth'] = dict_attribute['object_info_user'].NOT_AUTHORIZED
    return None


async def validate_pass_handler_crud(dict_attribute) -> str:
    result = await middleware_bd.validate_special_crud(dict_attribute)
    if result.success:
        is_login, is_author = result.value
        if is_author:
            activation_time = await middleware_bd.less_6_hours(dict_attribute)
            if activation_time.success:
                if isinstance(activation_time.value, dict):
                    return dict_attribute['object_info_user'].ACTIVE
                elif activation_time.value is None:
                    res = await middleware_bd.deactivation(dict_attribute)
                    if res is None:
                        return dict_attribute['object_info_user'].DEACTIVATIONS
                    else:
                        return dict_attribute['object_info_user'].ERRORS
                else:
                    return dict_attribute['object_info_user'].ERRORS

    return dict_attribute['object_info_user'].INACTIVES
