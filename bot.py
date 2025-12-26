import os
from aiogram import Bot, Dispatcher, executor, types

DEV_MODE = True
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if DEV_MODE:
        await message.answer(
            "🚧 GockLine\n\n"
            "Сервис находится в разработке.\n\n"
            "🔒 Регистрация временно закрыта"
        )
    else:
        await message.answer("Регистрация открыта")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
