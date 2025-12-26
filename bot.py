import os, sqlite3, random, time, threading
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("gock.db", check_same_thread=False)
cur = conn.cursor()

# ---------- TABLES ----------
cur.execute("""CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 tg_id INTEGER UNIQUE,
 password TEXT,
 expires_at INTEGER
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS profiles (
 user_id INTEGER PRIMARY KEY,
 nick TEXT,
 username TEXT,
 avatar TEXT
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS messages (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 from_id INTEGER,
 to_id INTEGER,
 text TEXT,
 time INTEGER
)""")

conn.commit()

app = Flask(__name__)

# ---------- HELPERS ----------
def now(): return int(time.time())
def gen_pass(): return str(random.randint(100000, 999999))

# ---------- BOT ----------
@dp.message_handler(commands=["start"])
async def start(m: types.Message):
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔐 Получить пароль", callback_data="get")
    )
    await m.answer("GockLine регистрация", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "get")
async def get_pass(c: types.CallbackQuery):
    tg = c.from_user.id
    p = gen_pass()
    exp = now() + 600

    cur.execute("SELECT id FROM users WHERE tg_id=?", (tg,))
    r = cur.fetchone()
    if r:
        uid = r[0]
        cur.execute("UPDATE users SET password=?, expires_at=? WHERE tg_id=?", (p, exp, tg))
    else:
        cur.execute("INSERT INTO users (tg_id,password,expires_at) VALUES (?,?,?)", (tg,p,exp))
        uid = cur.lastrowid
        cur.execute("INSERT INTO profiles (user_id,nick) VALUES (?,?)", (uid,f"user{uid}"))
    conn.commit()

    await c.message.edit_text(f"ID: {uid}\nПароль: {p}")

# ---------- API LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    d = request.json
    cur.execute("SELECT expires_at FROM users WHERE id=? AND password=?", (d["id"], d["password"]))
    r = cur.fetchone()
    if not r or r[0] < now():
        return jsonify(ok=False)
    return jsonify(ok=True)

# ---------- SEND MESSAGE ----------
@app.route("/message/send", methods=["POST"])
def send():
    d = request.json
    cur.execute(
        "INSERT INTO messages (from_id,to_id,text,time) VALUES (?,?,?,?)",
        (d["from"], d["to"], d["text"], now())
    )
    conn.commit()
    return jsonify(ok=True)

# ---------- GET MESSAGES ----------
@app.route("/message/get", methods=["POST"])
def get():
    d = request.json
    cur.execute(
        "SELECT from_id,text,time FROM messages WHERE to_id=? ORDER BY time",
        (d["me"],)
    )
    rows = cur.fetchall()
    return jsonify(messages=[
        {"from":r[0],"text":r[1],"time":r[2]} for r in rows
    ])

# ---------- START ----------
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000), daemon=True).start()
    executor.start_polling(dp, skip_updates=True)
