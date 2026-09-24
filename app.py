import os
import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "/data/app.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            replica TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.route("/health", methods=["GET"])
def health():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1").fetchone()
        conn.close()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 503

@app.route("/read", methods=["GET"])
def read():
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 20").fetchall()
        conn.close()
        return jsonify({"messages": [{"id": r[0], "content": r[1], "replica": r[2], "created_at": r[3]} for r in rows]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/write", methods=["POST"])
def write():
    try:
        content = os.environ.get("HOSTNAME", "unknown")
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO messages (content, replica) VALUES (?, ?)", (content, os.environ.get("HOSTNAME", "unknown")))
        conn.commit()
        conn.close()
        return jsonify({"status": "written", "replica": os.environ.get("HOSTNAME", "unknown")}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
