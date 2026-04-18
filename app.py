from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DB_NAME = "leads.db"
ADMIN_KEY = os.environ.get("ADMIN_KEY", "dev-key")


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


@app.route("/")
def home():
    return render_template("index.html")


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
    return render_template("thanks.html")


@app.route("/admin")
def admin():
    key = request.args.get("key", "")
    if key != ADMIN_KEY:
        return "Unauthorized", 401

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, created_at FROM leads ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    return render_template("admin.html", leads=rows)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)