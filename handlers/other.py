from handlers import Dispatcher, types
from handlers import bot

from modules.messages import MESSAGES


async def help_handler(message: types.Message):
    await bot.send_message(message.chat.id, MESSAGES["help"])


async def all_handler(message: types.Message):
    await bot.send_message(message.chat.id, MESSAGES["unknown-cmd"])


def other_register(dp: Dispatcher):
    dp.register_message_handler(help_handler, commands=[
                                "start", "help", "cmds", "команды"])
    dp.register_message_handler(all_handler, content_types=["any"])
