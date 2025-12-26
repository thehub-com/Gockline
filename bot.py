import os
import sqlite3
import random
import time
import threading

from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

# ================== BOT ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ================== DATABASE ==================
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

# ================== FLASK ==================
app = Flask(__name__)

# ================== KEYBOARDS ==================
kb_get = InlineKeyboardMarkup().add(
    InlineKeyboardButton("🔐 Получить пароль", callback_data="get")
)

kb_regen = InlineKeyboardMarkup().add(
    InlineKeyboardButton("🔄 Перегенерировать пароль", callback_data="regen")
)

# ================== HELPERS ==================
def gen_pass():
    return str(random.randint(100000, 999999))

def now():
    return int(time.time())

# ================== BOT HANDLERS ==================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "🚧 GockLine — регистрация\n\n"
        "Нажми кнопку ниже, чтобы получить одноразовый пароль.\n"
        "⏳ Действует 10 минут",
        reply_markup=kb_get
    )

@dp.callback_query_handler(lambda c: c.data in ["get", "regen"])
async def get_pass(callback: types.CallbackQuery):
    tg_id = callback.from_user.id
    password = gen_pass()
    expires = now() + 600

    cur.execute("SELECT id FROM users WHERE tg_id=?", (tg_id,))
    row = cur.fetchone()

    if row:
        user_id = row[0]
        cur.execute(
            "UPDATE users SET password=?, expires_at=? WHERE tg_id=?",
            (password, expires, tg_id)
        )
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
        reply_markup=kb_regen
    )

# ================== API ==================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user_id = data.get("id")
    password = data.get("password")

    cur.execute(
        "SELECT expires_at FROM users WHERE id=? AND password=?",
        (user_id, password)
    )
    row = cur.fetchone()

    if not row:
        return jsonify(ok=False, error="Неверные данные"), 401

    if row[0] < now():
        return jsonify(ok=False, error="Пароль истёк"), 403

    return jsonify(ok=True)

# ================== CLEANER ==================
def cleaner():
    while True:
        cur.execute("DELETE FROM users WHERE expires_at < ?", (now(),))
        conn.commit()
        time.sleep(60)

# ================== START ==================
if __name__ == "__main__":
    threading.Thread(target=cleaner, daemon=True).start()
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=10000),
        daemon=True
    ).start()

    executor.start_polling(dp, skip_updates=True)
