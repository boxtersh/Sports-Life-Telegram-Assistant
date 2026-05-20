from aiogram import Router, types, F

router = Router()


@router.message(F.text)
async def unknown_command(message: types.Message, object_info_user):
    text = message.text
    await message.answer(object_info_user.UNKNOWN_COMMAND.format(text=text))
    return