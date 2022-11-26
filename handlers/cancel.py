from handlers import Dispatcher, types
from handlers import bot

from aiogram.dispatcher.filters import Text

from modules.messages import MESSAGES


async def cancel(message: types.Message, state):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await bot.send_message(message.chat.id, MESSAGES["cancel"])


def cancel_register(dp: Dispatcher):
    dp.register_message_handler(cancel, Text(
        equals=["cancel"], ignore_case=True), state="*")
    dp.register_message_handler(
        cancel, commands=["cancel", "отмена"], state="*")
