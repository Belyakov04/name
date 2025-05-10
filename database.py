import sqlite3
from config import ADMIN_IDS


def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        score INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id: int, username: str):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()


def update_score(user_id: int, points: int):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (points, user_id))
    conn.commit()
    conn.close()
