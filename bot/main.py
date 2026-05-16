import asyncio
import logging
import sqlite3
from bot.database.init_db import init_db
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties

from bot.config import TOKEN
from bot.handlers import menu, fatigue_check, info, stats, error_report
from bot.config import DB_PATH

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.handlers.scheduler import check_expired_subscriptions

# === Настройка логов ===
logging.basicConfig(level=logging.INFO)

# === Экземпляры ===
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

from bot.handlers import admin
dp.include_router(admin.router)

# === Подключение роутеров ===
dp.include_routers(
    menu.router,
    fatigue_check.router,
    info.router,
    stats.router,
    error_report.router
)

# === Главная функция ===
async def main():
    logging.info("🤖 Инициализация базы данных...")
    init_db()

    logging.info("🤖 Бот запущен...")
    
        # === ЗАПУСК ПЛАНИРОВЩИКА (до start_polling) ===
    scheduler = AsyncIOScheduler()
    # Запускаем проверку раз в час
    from bot.handlers.subscription import router as subscription_router
    dp.include_router(subscription_router)
    
    scheduler.add_job(check_expired_subscriptions, "interval", hours=1, args=[bot])
    scheduler.start()
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
