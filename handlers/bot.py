from aiogram import Bot, Dispatcher

from handlers import MemoryStorage

__token_file = open("./token", "r")
__token = __token_file.read()
__token_file.close()

bot = Bot(token=__token)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
