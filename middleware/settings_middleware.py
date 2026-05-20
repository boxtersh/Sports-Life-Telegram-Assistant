from aiogram.dispatcher.middlewares.base import BaseMiddleware


class SpecialCrudMiddleware(BaseMiddleware):
    def __init__(self, dict_attr_middleware):
        super().__init__()
        self.bot = dict_attr_middleware['bot']
        self.dbase = dict_attr_middleware['dbase']
        self.object_info_user = dict_attr_middleware['object_info_user']
        self.f_state = dict_attr_middleware['f_state']

    def _create_dict_attribute(self, user_id, data):
        """
        Создаем словарь с данными для передачи обработчикам
        :param user_id:
        :param data:
        :return:
        """
        dict_attribute = {
            'dbase': self.dbase,
            'user_id': user_id,
            'data': data,
            'object_info_user': self.object_info_user
        }
        return dict_attribute

    def _key_data_default(self, data):
        """
        Устанавливаем значения по умолчанию для data
        :param data:
        :return:
        """
        data['no_reg'] = None
        data['no_auth'] = None
        data['f_state'] = self.f_state
        data['object_info_user'] = self.object_info_user
        data['dbase'] = self.dbase

    async def _send_restriction_message(self, user_id, status_active):
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=getattr(self.object_info_user, status_active, 'Что то пошло не так 🤔')
            )
        except Exception as err:
            print(f"Не удалось отправить сообщение пользователю {user_id}****{status_active}: {err}")

    async def __call__(self, handler, event, data):
        raise NotImplementedError()