from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from fsm_storage import FormStates

from business_logic import special_logic
from services import special_bd
from keyboards.keyboards import btn_yes_no

router = Router()


@router.message(Command('start'))
async def start_(message: types.Message, object_info_user, no_reg: str, no_auth: str):
    result = await special_logic.validate_no_reg_no_auth(object_info_user.START, no_reg, no_auth)
    await message.answer(result.value, reply_markup=btn_yes_no(), one_time_keyboard=True)


@router.message(Command('cancel'))
async def cancel(message: types.Message, object_info_user, state: FSMContext):
    await message.answer(object_info_user.CANCEL)
    await state.clear()
    return


@router.message(Command('help'))
async def help_(message: types.Message, object_info_user, no_reg: str, no_auth: str):
    result = await special_logic.validate_no_reg_no_auth(object_info_user.HELP, no_reg, no_auth)
    await message.answer(result.value)


@router.message(Command('register'))
async def register(message: types.Message, object_info_user, no_reg: str, state: FSMContext, f_state: FormStates):
    if no_reg is None:
        await message.answer(object_info_user.REGISTRATION_IS_NOT_REQUIRED)
        return
    await state.set_state(f_state.register_login)
    await message.answer(object_info_user.INPUT_LOGIN)


@router.message(F.text, FormStates.register_login)
async def login_user(message: types.Message, object_info_user, state: FSMContext, dbase, f_state: FormStates):
    login_text = message.text.strip().lower()
    result = special_logic.checking_string(login_text, object_info_user)
    if not result.success:
        return await message.reply(result.error)
    result = await special_bd.get_login(dbase, login_text)
    if isinstance(result.value, dict):
        await message.answer(object_info_user.LOGIN_IS_BUSY)
        return
    elif isinstance(result.error, str):
        await message.answer(f'{object_info_user.ERROR_DATABASE}, {result.error}')
        return
    await state.update_data(login_text=login_text)
    await message.answer(object_info_user.INPUT_PASSWORD)
    await state.set_state(f_state.register_password)


@router.message(F.text, FormStates.register_password)
async def password_user(message: types.Message, user_id, object_info_user, state: FSMContext, dbase,
                        f_state: FormStates):
    user_id = user_id
    password_text = message.text.strip().lower()
    result = special_logic.checking_string(password_text, object_info_user)
    if not result.success:
        await message.reply(result.error)
        return
    data_ = await state.get_data()
    login_text = data_.get('login_text')
    result = await special_bd.get_login(dbase, login_text)
    if isinstance(result.value, dict):
        await message.answer(object_info_user.LOGIN_IS_BUSY)
        await state.clear()
        await state.set_state(f_state.register_login)
        return
    elif isinstance(result.error, str):
        await message.answer(f'{object_info_user.ERROR_DATABASE}, {result.error}')
        await state.clear()
        return
    is_success = await special_bd.register_user(dbase, user_id, login_text, password_text)
    if is_success.success:
        await message.answer(object_info_user.REGISTRATION_SUCCESS_MESSAGE)
        await state.clear()
        return
    else:
        await message.answer(object_info_user.ERROR_DATABASE)
        await state.clear()


@router.message(Command('login'))
async def login(message: types.Message, object_info_user, no_reg: str, no_auth: str, state: FSMContext,
                f_state: FormStates):
    result = await special_logic.validate_auth(object_info_user.AUTHORIZATION_IS_NOT_REQUIRED, no_reg, no_auth)
    if result.value is not None:
        await message.answer(result.value)
        return
    await state.set_state(f_state.login_login)
    await message.answer(object_info_user.LOGIN_PROMPT)


@router.message(F.text, FormStates.login_login)
async def login_user(message: types.Message, user_id, object_info_user, state: FSMContext, dbase, f_state: FormStates):
    login_text = message.text.strip().lower()
    result = special_logic.checking_string(login_text, object_info_user)
    if not result.success:
        return await message.reply(result.error)
    result = await special_bd.is_login_exists_by_id(dbase, user_id, login_text)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        await state.clear()
        return
    if result.value is None:
        await message.answer(object_info_user.LOGIN_NOT_EXIST)
        return
    await state.update_data(login_text=login_text)
    await state.set_state(f_state.login_password)
    await message.answer(object_info_user.PASSWORD_PROMPT)


@router.message(F.text, FormStates.login_password)
async def login_user(message: types.Message, user_id, object_info_user, state: FSMContext, dbase, f_state: FormStates):
    password_text = message.text
    data_ = await state.get_data()
    login_text = data_.get('login_text')
    result = await special_bd.get_stored(dbase, user_id, login_text)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        await state.clear()
        return
    if result.value is None:
        await message.answer(object_info_user.PASSWORD_NOT_FOUND)
        await state.clear()
        return
    stored_from_db = result.value['password']
    is_verify = special_bd.verify_password(password_text, stored_from_db)
    if not is_verify.success:
        await message.answer(f'{object_info_user.ERROR}, {is_verify.error}')
        await state.clear()
        return
    if is_verify.success and not is_verify.value:
        await message.answer(object_info_user.INVALID_PASSWORD)
        await state.clear()
        return
    result = await special_bd.authorization(dbase, login_text)
    if not result.success:
        await message.answer(object_info_user.ERROR_DATABASE, result.error)
        await state.clear()
        return
    await message.answer(object_info_user.AUTHORIZATION_SUCCESS_MESSAGE)
    await state.clear()