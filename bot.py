import os
import sqlite3
import random
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ---------- DATABASE ----------
conn = sqlite3.connect("gock.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER UNIQUE,
    password TEXT,
    expires_at INTEGER
)
""")
conn.commit()

# ---------- KEYBOARDS ----------
get_pass_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("🔐 Получить пароль", callback_data="get_pass")
)

regen_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("🔄 Перегенерировать пароль", callback_data="regen_pass")
)

# ---------- HELPERS ----------
def generate_password():
    return str(random.randint(100000, 999999))

def now():
    return int(time.time())

# ---------- HANDLERS ----------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "🚧 GockLine — регистрация\n\n"
        "Нажми кнопку ниже, чтобы получить одноразовый пароль.\n"
        "⏳ Действует 10 минут",
        reply_markup=get_pass_kb
    )

@dp.callback_query_handler(lambda c: c.data in ["get_pass", "regen_pass"])
async def get_or_regen(callback: types.CallbackQuery):
    tg_id = callback.from_user.id
    password = generate_password()
    expires = now() + 600  # 10 минут

    cur.execute("SELECT id FROM users WHERE tg_id = ?", (tg_id,))
    user = cur.fetchone()

    if user:
        cur.execute(
            "UPDATE users SET password=?, expires_at=? WHERE tg_id=?",
            (password, expires, tg_id)
        )
        user_id = user[0]
    else:
        cur.execute(
            "INSERT INTO users (tg_id, password, expires_at) VALUES (?, ?, ?)",
            (tg_id, password, expires)
        )
        user_id = cur.lastrowid

    conn.commit()

    await callback.message.edit_text(
        f"✅ Регистрация GockLine\n\n"
        f"🆔 ID: {user_id}\n"
        f"🔐 Пароль: `{password}`\n"
        f"⏳ Действует 10 минут\n\n"
        f"Используй его в приложении",
        parse_mode="Markdown",
        reply_markup=regen_kb
    )

# ---------- CLEANER ----------
async def cleanup():
    while True:
        cur.execute("DELETE FROM users WHERE expires_at < ?", (now(),))
        conn.commit()
        await asyncio.sleep(60)

# ---------- START ----------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
