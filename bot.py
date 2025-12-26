import time
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 🔥 ЭТО РЕШАЕТ CORS

# ---------- DATABASE ----------
db = sqlite3.connect("gock.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender INTEGER,
    receiver INTEGER,
    text TEXT,
    time INTEGER
)
""")
db.commit()

# ---------- SEND MESSAGE ----------
@app.route("/send", methods=["POST"])
def send():
    data = request.json
    sender = data.get("from")
    receiver = data.get("to")
    text = data.get("text")

    if not sender or not receiver or not text:
        return jsonify(ok=False, error="bad data")

    cur.execute(
        "INSERT INTO messages (sender, receiver, text, time) VALUES (?,?,?,?)",
        (sender, receiver, text, int(time.time()))
    )
    db.commit()

    return jsonify(ok=True)

# ---------- GET MESSAGES ----------
@app.route("/get/<int:user_id>", methods=["GET"])
def get_messages(user_id):
    cur.execute(
        "SELECT sender, text, time FROM messages WHERE receiver=? OR sender=? ORDER BY time",
        (user_id, user_id)
    )
    rows = cur.fetchall()

    messages = []
    for r in rows:
        messages.append({
            "from": r[0],
            "text": r[1],
            "time": r[2]
        })

    return jsonify(messages)

# ---------- START ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
