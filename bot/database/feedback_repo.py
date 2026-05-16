from bot.config import DB_PATH
import sqlite3
from .init_db import add_user_if_not_exists  # чтобы гарантировать существование пользователя

def save_feedback(user_id: int, text: str):
    # Гарантируем, что пользователь есть в таблице users
    add_user_if_not_exists(user_id)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback (user_id, text)
        VALUES (?, ?)
    """, (user_id, text))

    conn.commit()
    conn.close()
