import binascii
import hashlib
import os

from mysql.connector import Error

from result_wrapper import Result


def _create_hash(password: str) -> str:
    """
    Возвращает строку вида salt_hex$sha256_hex(salt + password).
    Простая и наглядная — удобно показать студентам.
    """
    salt = os.urandom(8)
    salt_hex = binascii.hexlify(salt).decode()
    digest = hashlib.sha256(salt + password.encode("utf-8")).hexdigest()
    return f"{salt_hex}${digest}"


def verify_password(password: str, stored: str) -> Result:
    """
    Проверяет пароль по сохранённому формату salt_hex$hash.
    """
    try:
        salt_hex, stored_digest = stored.split("$", 1)
        salt = binascii.unhexlify(salt_hex)
    except Exception as err:
        return Result.failure(f'{err}')
    digest = hashlib.sha256(salt + password.encode("utf-8")).hexdigest()
    return Result.success(digest == stored_digest)


async def register_user(dbase, user_id: int, login: str, password: str) -> Result:
    """Регистрирует пользователя, возвращает id.
    Выкидывает ValueError, если такой пользователь уже есть.
    """
    try:
        stored = _create_hash(password)
        await dbase.add_user(user_id, login, stored)
        res = Result.success(True)
    except Error as err:
        res = Result.failure(f'{err}')
    return res


async def get_login(dbase, login_text) -> Result:
    try:
        result = await dbase.login_exists(login_text)
        res = Result.success(result)
    except Error as err:
        res = Result.failure(f'{err}')
    return res


async def get_stored(dbase, user_id, login_text) -> Result:
    try:
        response = await dbase.get_stored(user_id, login_text)
        res = Result.success(response)
    except Error as err:
        res = Result.failure(f'{err}')
    return res


async def authorization(dbase, login_text) -> Result:
    try:
        await dbase.authorization(login_text)
        return Result.success(None)
    except Error as err:
        return Result.failure(f'{err}')


async def is_login_exists_by_id(dbase, user_id, login_text) -> Result:
    try:
        response = await dbase.is_login_exists_by_id(user_id, login_text)
        return Result.success(response)
    except Error as err:
        return Result.failure(f'{err}')
