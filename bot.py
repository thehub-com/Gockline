import asyncio
import random
import time
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# ================= НАСТРОЙКИ =================
TOKEN = "8261801832:AAEHUDbVv1lnBCjHtao_oeGNT_ODowA6Q8g"
CODE_LIFETIME = 600  # 10 минут

# ================= ХРАНИЛИЩЕ КОДОВ =================
# telegram_id: (code, expire_time)
codes = {}

# ================= БОТ =================
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================= КНОПКИ =================
def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Получить код", callback_data="get_code")],
        [InlineKeyboardButton(text="♻️ Новый код", callback_data="regen_code")],
    ])

# ================= /START =================
@dp.message(Command("start"))
async def start(message: Message):
    text = (
        "👋 <b>Добро пожаловать в GockLine</b>\n\n"
        "Это регистрационный бот.\n\n"
        "🔐 Нажмите кнопку ниже, чтобы получить\n"
        "<b>одноразовый 6-значный код</b> для входа.\n\n"
        "⏱ Код действует 10 минут."
    )
    await message.answer(text, reply_markup=main_keyboard(), parse_mode="HTML")

# ================= ГЕНЕРАЦИЯ КОДА =================
def generate_code():
    return str(random.randint(100000, 999999))

async def send_code(user_id: int, chat_id: int):
    code = generate_code()
    expire = int(time.time()) + CODE_LIFETIME
    codes[user_id] = (code, expire)

    text = (
        "✅ <b>Ваш код готов</b>\n\n"
        f"🔑 <code>{code}</code>\n\n"
        "⏱ Действует 10 минут.\n"
        "⚠️ Никому не передавайте."
    )
    await bot.send_message(chat_id, text, parse_mode="HTML")

# ================= КНОПКИ =================
@dp.callback_query(F.data == "get_code")
async def get_code(call):
    await send_code(call.from_user.id, call.message.chat.id)
    await call.answer()

@dp.callback_query(F.data == "regen_code")
async def regen_code(call):
    await send_code(call.from_user.id, call.message.chat.id)
    await call.answer("Код обновлён")

# ================= ПРОВЕРКА КОДА (ДЛЯ SERVER.PY) =================
def verify_code(telegram_id: int, code: str) -> bool:
    if telegram_id not in codes:
        return False

    saved_code, expire = codes[telegram_id]
    if time.time() > expire:
        del codes[telegram_id]
        return False

    if saved_code == code:
        del codes[telegram_id]
        return True

    return False

# ================= ЗАПУСК =================
async def main():
    print("🤖 GockLine bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
