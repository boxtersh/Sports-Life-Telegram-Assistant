from middleware.settings_middleware import SpecialCrudMiddleware

from business_logic import middleware_logic


class SpecialMiddleware(SpecialCrudMiddleware):
    async def __call__(self, handler, event, data):
        self._key_data_default(data)
        result = middleware_logic.validate_event(event)
        user_id, message_text = result.value
        if user_id is None or message_text is None:
            return
        data['user_id'] = user_id
        data['message_text'] = message_text
        dict_attribute = self._create_dict_attribute(user_id, data)
        await middleware_logic.validate_pass_handler_special(dict_attribute)
        await handler(event, data)
        return
