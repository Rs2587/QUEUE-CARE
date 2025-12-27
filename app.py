from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)


DB_NAME = "database.db"
MAX_TOKENS = 50
SLOT_DURATION = 10  # minutes
START_APPOINTMENT_HOUR = 9  # 9:00 AM

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            token INTEGER,
            time_slot TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


def get_today():
    return datetime.now().strftime("%Y-%m-%d")

def get_token_count():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM appointments WHERE date=?",
        (get_today(),)
    )
    count = cur.fetchone()[0]
    conn.close()
    return count

def generate_time_slot(token):
    total_minutes = (token - 1) * SLOT_DURATION
    hour = START_APPOINTMENT_HOUR + total_minutes // 60
    minute = total_minutes % 60
    end_minute = minute + SLOT_DURATION
    return f"{hour:02d}:{minute:02d} - {hour:02d}:{end_minute:02d}"

def already_booked(phone):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM appointments WHERE phone=? AND date=?",
        (phone, get_today())
    )
    exists = cur.fetchone()[0] > 0
    conn.close()
    return exists

def estimated_wait_time(token):
    return (token - 1) * SLOT_DURATION

def reset_if_new_day():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT date FROM appointments")
    rows = cur.fetchall()

    if rows and rows[0][0] != get_today():
        cur.execute("DELETE FROM appointments")
        conn.commit()

    conn.close()

def remaining_slots():
    return MAX_TOKENS - get_token_count()


@app.route("/call", methods=["POST"])
def simulate_call():
    reset_if_new_day()

    data = request.json
    phone = data.get("phone")
    mode = data.get("mode", "success")  

    
    if mode == "wrong_time":
        return jsonify({
            "SMS": "Booking allowed only between 8:00–8:05 AM. Please try tomorrow."
        })

    
    if mode == "full":
        return jsonify({
            "SMS": "Today’s appointments are full. Please try again tomorrow."
        })

    
    if already_booked(phone):
        return jsonify({
            "SMS": "You have already booked today. Please come at your scheduled time."
        })

    
    count = get_token_count()
    if count >= MAX_TOKENS:
        return jsonify({
            "SMS": "Today’s appointments are full. Please try again tomorrow."
        })

    
    token = count + 1
    time_slot = generate_time_slot(token)
    wait_time = estimated_wait_time(token)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO appointments (phone, token, time_slot, date) VALUES (?,?,?,?)",
        (phone, token, time_slot, get_today())
    )
    conn.commit()
    conn.close()

    return jsonify({
        "SMS": f"Your token number is {token}. "
               f"Your appointment time is {time_slot}. "
               f"Estimated waiting time: {wait_time} minutes."
    })


@app.route("/admin", methods=["GET"])
def admin_view():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT phone, token, time_slot FROM appointments WHERE date=?",
        (get_today(),)
    )
    data = cur.fetchall()
    conn.close()
    return jsonify(data)

@app.route("/reset", methods=["POST"])
def admin_reset():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments")
    conn.commit()
    conn.close()
    return jsonify({"status": "All appointments reset successfully"})

@app.route("/slots", methods=["GET"])
def slot_status():
    return jsonify({
        "remaining_slots": remaining_slots(),
        "max_slots": MAX_TOKENS
    })

@app.route("/stats", methods=["GET"])
def stats():
    return jsonify({
        "date": get_today(),
        "total_booked": get_token_count(),
        "max_limit": MAX_TOKENS
    })


if __name__ == "__main__":
    app.run(debug=True)
