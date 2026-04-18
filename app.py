from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# --- DB file name (project root дээр үүснэ) ---
DB_NAME = "leads.db"

# --- Admin хамгаалалт (MVP-д хурдан) ---
# 1) ЭНДЭЭС key-гээ солиорой (урт, таахад хэцүү болгож өг!)
# Жишээ: "8f2c1d9a-7c2b-4a1d-9b8a-xxxxxx"
ADMIN_KEY = "changeme-admin-key"


# ---------- Database init ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ---------- Routes ----------
@app.route("/")
def home():
    # templates/index.html файл байх ёстой
    return render_template("index.html")  # Flask templates convention [1](https://flask.palletsprojects.com/en/stable/tutorial/templates/)


@app.route("/waitlist", methods=["POST"])
def waitlist():
    email = request.form.get("email", "").strip()

    if email:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO leads (email, created_at) VALUES (?, ?)",
            (email, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()

    return redirect("/thanks")


@app.route("/thanks")
def thanks():
    # templates/thanks.html файл байх ёстой
    return render_template("thanks.html")  # Flask templates convention [1](https://flask.palletsprojects.com/en/stable/tutorial/templates/)


@app.route("/admin")
def admin():
    # URL: /admin?key=YOUR_KEY
    key = request.args.get("key", "")
    if key != ADMIN_KEY:
        return "Unauthorized", 401

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, created_at FROM leads ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    # templates/admin.html файл байх ёстой
    return render_template("admin.html", leads=rows)  # Flask templates convention [1](https://flask.palletsprojects.com/en/stable/tutorial/templates/)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)