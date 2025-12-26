import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# === НАСТРОЙКИ ===
DEV_MODE = True  # ❗ пока True — бот закрыт
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в Environment Variables")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    if DEV_MODE:
        await message.answer(
            "🚧 *GockLine*\n\n"
            "Сервис находится в разработке.\n\n"
            "🔒 Регистрация временно закрыта\n"
            "Приложение ещё не доступно для всеобщего использования.",
            parse_mode="Markdown"
        )
        return

    # ⬇️ сюда в будущем включится реальная логика
    await message.answer("Регистрация открыта (в разработке)")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
