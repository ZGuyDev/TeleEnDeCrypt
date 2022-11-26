from aiogram import executor

from handlers import dp
from handlers import (encryption_register, decryption_register,
                      other_register, cancel_register)

cancel_register(dp)
encryption_register(dp)
decryption_register(dp)
other_register(dp)

if __name__ == "__main__":
    async def start(*x) -> None:
        print("Bot started")

    async def shut(*x) -> None:
        print("Bot shutted down")

    executor.start_polling(dispatcher=dp, on_startup=start, on_shutdown=shut)
