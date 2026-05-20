from result_wrapper import Result


def checking_string(login_text: str, object_info_user) -> Result:
    if len(login_text) < 6 or len(login_text) > 19:
        return Result.failure(object_info_user.NOT_LEN_STR)
    if set(login_text[0]) - object_info_user.ALLOWED_CHARS != set():
        return Result.failure(object_info_user.LOGIN_START_WITH_LETTER_ERROR)
    set_login_user = {char_ for char_ in login_text}
    if set_login_user - object_info_user.ALLOWED_CHARS_PLUS != set():
        return Result.failure(object_info_user.LOGIN_INVALID_CHARACTERS)
    return Result.success(None)


async def validate_no_reg_no_auth(str_command, no_reg, no_auth) -> Result:
    if no_reg is not None:
        res = f'{str_command}\n{no_reg}'
    elif no_auth is not None:
        res = f'{str_command}\n{no_auth}'
    else:
        res = f'{str_command}'
    return Result.success(res)


async def validate_auth(str_command, no_reg, no_auth) -> Result:
    if no_reg is not None:
        res = no_reg
    elif no_auth is None:
        res = str_command
    else:
        res = None
    return Result.success(res)