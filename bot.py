import random
import time
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

TOKEN = "8261801832:AAEHUDbVv1lnBCjHtao_oeGNT_ODowA6Q8g"

bot = Bot(token=TOKEN)
dp = Dispatcher()

codes = {}  # user_id: (code, expire)

@dp.message(CommandStart())
async def start(msg: Message):
    code = random.randint(100000, 999999)
    expire = time.time() + 600  # 10 минут
    codes[msg.from_user.id] = (code, expire)

    await msg.answer(
        f"🔐 GockLine\n\n"
        f"Ваш код регистрации:\n\n"
        f"👉 <b>{code}</b>\n\n"
        f"⏱ Действует 10 минут",
        parse_mode="HTML"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
