import random
import time
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "8261801832:AAEHUDbVv1lnBCjHtao_oeGNT_ODowA6Q8g"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

codes = {}  # user_id: (code, expire_time)

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
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

@dp.message_handler(commands=['code'])
async def get_code(msg: types.Message):
    data = codes.get(msg.from_user.id)
    if not data:
        await msg.answer("❌ Код не найден. Напишите /start")
        return

    code, expire = data
    if time.time() > expire:
        await msg.answer("⏱ Код истёк. Напишите /start")
        del codes[msg.from_user.id]
        return

    await msg.answer(f"Ваш активный код: {code}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
