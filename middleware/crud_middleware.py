from middleware.settings_middleware import SpecialCrudMiddleware

from business_logic import middleware_logic


class CrudMiddleware(SpecialCrudMiddleware):
    async def __call__(self, handler, event, data):
        """
        Проверяем полученный объект из telegram Message или CallbackQuery и дополняем словарь data
        значениями user_id и message_text
        :param handler:
        :param event:
        :param data:
        :return:
        """
        self._key_data_default(data)
        result = middleware_logic.validate_event(event)
        user_id, message_text = result.value
        if user_id is None or message_text is None:
            return
        data['user_id'] = user_id
        data['message_text'] = message_text
        dict_attribute = self._create_dict_attribute(user_id, data)
        status_active = await middleware_logic.validate_pass_handler_crud(dict_attribute)
        if status_active == 'ACTIVE':
            await handler(event, data)
            return
        else:
            await self._send_restriction_message(user_id, status_active)
            return
