import asyncio
import threading
from flask import Flask, jsonify
from flask_cors import CORS

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ===== НАСТРОЙКИ =====
TOKEN = "ТВОЙ_BOT_TOKEN_ОСТАВЬ_КАК_ЕСТЬ"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== FLASK (HTML <-> SERVER) =====
app = Flask(__name__)
CORS(app)  # <<< ЭТО ФИКСИТ CORS

USERS = {
    1: {
        "id": 1,
        "username": "user1",
        "verified": False
    }
}

@app.route("/")
def home():
    return "GOCK server is running"

@app.route("/get/<int:user_id>")
def get_user(user_id):
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify(user)

# ===== TELEGRAM BOT =====
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("GOCK bot online")

# ===== RUN BOTH =====
def run_flask():
    app.run(host="0.0.0.0", port=10000)

async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(run_bot())
