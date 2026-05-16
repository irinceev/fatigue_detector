from bot.config import DB_PATH
import sqlite3
from .classify import classify_fatigue
from bot.database.init_db import add_user_if_not_exists

def save_fatigue_record(user_id: int, score: float):
    # Гарантируем, что пользователь существует
    add_user_if_not_exists(user_id)
    
    fatigue_class = classify_fatigue(score)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO fatigue_records (user_id, fatigue_score, fatigue_class)
        VALUES (?, ?, ?)
    """, (user_id, score, fatigue_class))
    
    conn.commit()
    conn.close()