from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)

# ---- ВРЕМЕННОЕ ХРАНИЛИЩЕ (потом БД) ----
users = {}        # user_id -> profile
codes = {}        # code -> time
messages = {}     # chat_id -> messages

# ---- ПРОСТОЙ ГЕНЕРАТОР ID ----
def next_user_id():
    return len(users) + 1

# ---- ПРОВЕРКА КОДА ОТ БОТА ----
@app.route("/verify", methods=["POST"])
def verify_code():
    data = request.json
    code = data.get("code")

    if not code:
        return jsonify({"error": "NO_CODE"}), 400

    if code not in codes:
        return jsonify({"error": "INVALID_CODE"}), 403

    # код живёт 10 минут
    if time.time() - codes[code] > 600:
        del codes[code]
        return jsonify({"error": "CODE_EXPIRED"}), 403

    user_id = next_user_id()
    users[user_id] = {
        "id": user_id,
        "username": None,
        "avatar": None,
        "bio": "",
        "gip": 0
    }

    del codes[code]

    return jsonify({
        "status": "ok",
        "user_id": user_id
    })


# ---- СОХРАНЕНИЕ ПРОФИЛЯ ----
@app.route("/profile/save", methods=["POST"])
def save_profile():
    data = request.json
    user_id = data.get("user_id")

    if user_id not in users:
        return jsonify({"error": "USER_NOT_FOUND"}), 404

    users[user_id]["username"] = data.get("username")
    users[user_id]["bio"] = data.get("bio", "")

    return jsonify({"status": "saved"})


# ---- ПОЛУЧИТЬ ПРОФИЛЬ ----
@app.route("/profile/<int:user_id>")
def get_profile(user_id):
    if user_id not in users:
        return jsonify({"error": "USER_NOT_FOUND"}), 404
    return jsonify(users[user_id])


# ---- ОТПРАВКА СООБЩЕНИЯ ----
@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    chat_id = data.get("chat_id")
    text = data.get("text")
    from_id = data.get("from_id")

    if not chat_id or not text:
        return jsonify({"error": "BAD_DATA"}), 400

    messages.setdefault(chat_id, []).append({
        "from": from_id,
        "text": text,
        "time": int(time.time())
    })

    return jsonify({"status": "sent"})


# ---- ПОЛУЧИТЬ СООБЩЕНИЯ ----
@app.route("/messages/<chat_id>")
def get_messages(chat_id):
    return jsonify(messages.get(chat_id, []))


# ---- ТЕСТОВЫЙ РОУТ ----
@app.route("/")
def index():
    return "GockLine server is running"


# ---- ВАЖНО ДЛЯ RENDER ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
