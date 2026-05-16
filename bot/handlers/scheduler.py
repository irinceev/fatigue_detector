import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot
from bot.config import DB_PATH
from bot.database.init_db import cancel_subscription

async def check_expired_subscriptions(bot: Bot):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now()
    
    # Ищем подписки, которые:
    # 1. Считаются активными (is_active = 1)
    # 2. Но время уже вышло (end_date < now)
    cursor.execute("""
        SELECT user_id FROM subscriptions
        WHERE is_active = 1 
          AND end_date < ?
    """, (now,))
    
    expired_users = cursor.fetchall()
    
    if not expired_users:
        conn.close()
        return

    print(f"📉 Найдено {len(expired_users)} истекших подписок.")

    for (user_id,) in expired_users:
        # Вызываем нашу функцию отключения
        cancel_subscription(user_id)
        
        # Шлем уведомление юзеру
        try:
            await bot.send_message(user_id, "⚠️ **Ваша подписка истекла!**\nПродлите доступ, чтобы снять лимиты.")
        except:
            pass
            
    conn.close()