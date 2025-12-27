from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import time

app = Flask(__name__)
CORS(app)

DB_NAME = "database.db"

# ---------- БАЗА ДАННЫХ ----------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT UNIQUE,
        nickname TEXT,
        created_at INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- ВРЕМЕННОЕ ХРАНИЛИЩЕ КОДОВ ----------
# ВРЕМЕННО! Потом объединим с bot.py через БД
codes = {
    # telegram_id: "123456"
}

# ---------- API ----------
@app.route("/")
def home():
    return "GockLine server online"

# 🔐 РЕГИСТРАЦИЯ
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json

    telegram_id = data.get("telegram_id")
    code = data.get("code")
    username = data.get("username")
    nickname = data.get("nickname")

    if not all([telegram_id, code, username]):
        return jsonify({"error": "missing_data"}), 400

    # ❗ ВРЕМЕННАЯ ПРОВЕРКА КОДА
    saved_code = codes.get(telegram_id)
    if saved_code != code:
        return jsonify({"error": "invalid_code"}), 403

    conn = get_db()
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (telegram_id, username, nickname, created_at) VALUES (?, ?, ?, ?)",
            (telegram_id, username, nickname, int(time.time()))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "user_exists"}), 409
    finally:
        conn.close()

    return jsonify({"status": "ok"})

# 👤 ПРОФИЛЬ
@app.route("/api/profile/<int:user_id>")
def profile(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, username, nickname FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "not_found"}), 404

    return jsonify(dict(user))

# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
