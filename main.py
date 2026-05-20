import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from middleware.special_middleware import SpecialMiddleware
from middleware.crud_middleware import CrudMiddleware
from handlers import special, crud, unknown_command
from fsm_storage import FormStates
from repo import Repo
from constants import DatabaseQueries, InfoForUser
from config import settings
from scheduler import daily_scheduler


async def main():
    object_queries = DatabaseQueries()
    object_info_user = InfoForUser()
    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher(bot=bot, storage=MemoryStorage())
    dbase = Repo(object_queries)
    f_state = FormStates
    await dbase.open()
    await dbase.create_table_in_db()
    asyncio.create_task(daily_scheduler(bot, dbase, object_info_user))
    dict_attr_middleware = {'bot': bot,
                            'dbase': dbase,
                            'object_info_user': object_info_user,
                            'f_state': f_state}
    special.router.message.middleware(SpecialMiddleware(dict_attr_middleware))
    unknown_command.router.message.middleware(SpecialMiddleware(dict_attr_middleware))
    crud.router.message.middleware(CrudMiddleware(dict_attr_middleware))
    crud.router.callback_query.middleware(CrudMiddleware(dict_attr_middleware))

    dp.include_routers(
        special.router,
        crud.router,
        unknown_command.router
    )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await dbase.close()


if __name__ == '__main__':
    print('Запускаю бота')
    asyncio.run(main())