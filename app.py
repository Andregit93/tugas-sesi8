import os
import time
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

def init_db():
    for _ in range(10):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            return
        except mysql.connector.Error:
            time.sleep(2)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "db_host": os.getenv("DB_HOST")}), 200

@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Field 'name' wajib diisi"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name) VALUES (%s)", (data["name"],))
    conn.commit()
    item_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"id": item_id, "name": data["name"]}), 201

@app.route("/items", methods=["GET"])
def list_items():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, created_at FROM items ORDER BY id ASC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(rows), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
