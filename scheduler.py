import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from services import crud_db
from models import models


def replace_none_values(dict_attribute: dict) -> dict:
    if dict_attribute['first_workout'] is None:
        dict_attribute['first_workout'] = '-'
    if dict_attribute['last_workout'] is None:
        dict_attribute['last_workout'] = '-'
    return dict_attribute

async def daily_scheduler(bot: Bot, dbase, object_info_user):
    """
    Ежедневно проверя цели:
    changing_status_to_expired - меняет статус если цель просрочена;
    get_all_users_expired_goals - отправляет пользователям статитику просроченных целей
    :param bot:
    :param dbase:
    :param object_info_user:
    :return:
    """
    while True:
        now = datetime.now()
        next_run = now.replace(hour=18, minute=40, second=0, microsecond=0)
        if now >= next_run:
            next_run = next_run + timedelta(days=1)

        wait_seconds = (next_run - now).total_seconds()
        print(f"До следующего запуска: {wait_seconds} секунд ({next_run})")
        await asyncio.sleep(wait_seconds)

        result = await crud_db.changing_status_to_achieved(dbase)
        if not result.success:
            print(object_info_user.ERROR_DATABASE, result.error)
            continue
        result_achieved = await crud_db.get_all_users_achieved_goals(dbase)
        if not result_achieved.success:
            print(object_info_user.ERROR_DATABASE, result_achieved.error)
            continue
        elif result_achieved.value:
            for dict_attribute in result_achieved.value:
                user_id_achieved = dict_attribute['register_user_id']
                replace_none_values(dict_attribute)
                goal_achieved = models.InfoGoal(**dict_attribute)
                try:
                    await bot.send_message(chat_id=user_id_achieved,
                                           text=f'{object_info_user.LIST_GOAL_ACHIEVED}\n'
                                                f'{goal_achieved}\n')
                except Exception as err:
                    print(f"Не удалось отправить сообщение пользователю {user_id_achieved}: {err}")
                await asyncio.sleep(0.3)

        result = await crud_db.changing_status_to_expired(dbase)
        if not result.success:
            print(object_info_user.ERROR_DATABASE, result.error)
            continue
        result_expired = await crud_db.get_all_users_expired_goals(dbase)
        if not result_expired.success:
            print(object_info_user.ERROR_DATABASE, result_expired.error)
        elif result_expired.value:
            for dict_attribute in result_expired.value:
                user_id_expired = dict_attribute['register_user_id']
                replace_none_values(dict_attribute)
                goal_expired = models.InfoGoal(**dict_attribute)
                try:
                    await bot.send_message(chat_id=user_id_expired,
                                           text=f'{object_info_user.LIST_GOAL_EXPIRED}\n'
                                                f'{goal_expired}')
                except Exception as err:
                    print(f"Не удалось отправить сообщение пользователю {user_id_expired}: {err}")
                await asyncio.sleep(0.3)