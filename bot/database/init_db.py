from bot.config import DB_PATH
import sqlite3
from datetime import datetime, timedelta
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # === 1. Создаем таблицу пользователей (если нет) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            is_premium INTEGER DEFAULT 0,  -- 0 = обычный, 1 = премиум
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # === 2. МИГРАЦИЯ: Если таблица уже была, добавляем колонку is_premium ===
    try:
        # Пытаемся добавить колонку. Если она уже есть, sqlite вернет ошибку, которую мы игнорируем
        cursor.execute("ALTER TABLE users ADD COLUMN is_premium INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Колонка уже существует

    # === 3. Таблица записей усталости ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fatigue_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fatigue_score REAL,
            fatigue_class TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # === 4. Таблица обратной связи ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
        # === 5. Таблица подписок (НОВАЯ) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# === Функция добавления пользователя (обновленная) ===
def add_user_if_not_exists(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Добавляем пользователя, is_premium встанет в 0 по умолчанию
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id)
        VALUES (?)
    """, (user_id,))
    conn.commit()
    conn.close()


# === Новая функция: Проверка премиума ===
def is_user_premium(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT is_premium FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    # Если result есть и в нем 1 (True), возвращаем True
    return result and result[0] == 1


# # === Новая функция: Выдать премиум ===
# def set_user_premium(user_id, status=True):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     val = 1 if status else 0
#     cursor.execute("UPDATE users SET is_premium = ? WHERE user_id = ?", (val, user_id))
#     conn.commit()
#     conn.close()

def set_user_premium(user_id, status=True):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    val = 1 if status else 0
    
    # 1. ОБНОВЛЯЕМ (UPDATE)
    cursor.execute("UPDATE users SET is_premium = ? WHERE user_id = ?", (val, user_id))
    
    # 2. ВАЖНО: Если обновлять некого (пользователя нет в базе), ничего не произойдет.
    # Поэтому проверим, обновилась ли строка:
    if cursor.rowcount == 0:
        # Если пользователя нет, добавляем его сразу с премиумом
        cursor.execute("INSERT INTO users (user_id, is_premium) VALUES (?, ?)", (user_id, val))
    
    conn.commit()  # <--- ОБЯЗАТЕЛЬНО! Без этого изменения не сохранятся
    conn.close()

# === Функция подсчета ВСЕХ сканирований пользователя ===
def get_total_scan_count(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Считаем количество записей в таблице fatigue_records для конкретного user_id
    cursor.execute("SELECT COUNT(*) FROM fatigue_records WHERE user_id = ?", (user_id,))
    
    count = cursor.fetchone()[0] # fetchone вернет кортеж (5,), берем [0]
    conn.close()
    
    return count

def create_subscription(user_id, days=30):
    """
    Создает новую подписку, ЕСЛИ нет активной.
    Также обновляет флаг is_premium в таблице users (для совместимости).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now()
    
    # 1. Проверяем, есть ли УЖЕ активная подписка (которая еще не истекла)
    cursor.execute("""
        SELECT id FROM subscriptions 
        WHERE user_id = ? AND is_active = 1 AND end_date > ?
    """, (user_id, now))
    
    if cursor.fetchone():
        conn.close()
        return False # Ошибка: у человека уже есть подписка
    
    # 2. Создаем новую запись (Старые со статусом 0 просто лежат в истории)
    end_date = now + timedelta(days=days)
    cursor.execute("""
        INSERT INTO subscriptions (user_id, start_date, end_date, is_active)
        VALUES (?, ?, ?, 1)
    """, (user_id, now, end_date))
    
    # 3. Синхронизируем со старой системой (ставим галочку в users)
    cursor.execute("UPDATE users SET is_premium = 1 WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()
    return True


def cancel_subscription(user_id):
    """
    Вызывается шедулером, когда время вышло.
    Переводит подписку в статус 0 и снимает флаг в users.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Все активные подписки этого юзера помечаем как "архивные" (0)
    cursor.execute("UPDATE subscriptions SET is_active = 0 WHERE user_id = ?", (user_id,))
    
    # 2. Снимаем галочку в users (чтобы бот запретил доступ)
    cursor.execute("UPDATE users SET is_premium = 0 WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()