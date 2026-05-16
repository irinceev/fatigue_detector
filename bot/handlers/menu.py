from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.handlers.keyboards import main_menu_keyboard
from bot.handlers import info, fatigue_check, stats, error_report, subscription, admin  # твои модули
from bot.database.init_db import add_user_if_not_exists  # функция добавления пользователя в БД

router = Router()


# Команда /start
@router.message(lambda m: m.text == "/start")
async def start_cmd(message: types.Message):
    # Добавляем пользователя в БД, если его там ещё нет
    add_user_if_not_exists(message.from_user.id)

    await message.answer(
        "Главное меню. Выберите действие:",
        reply_markup=main_menu_keyboard()
    )

# Обработка кнопок меню
@router.message(lambda m: m.text in ["ℹ️ Инфо", "🧠 Проверить усталость", "📊 Статистика", "⚠️ Обратная связь", "💎 Подписка"])
async def handle_menu_actions(message: types.Message, state: FSMContext):
    if message.text == "ℹ️ Инфо":
        await info.info_handler(message)
    elif message.text == "🧠 Проверить усталость":
        # Передаём state в обработчик усталости
        await fatigue_check.start_fatigue_check(message, state)
    elif message.text == "📊 Статистика":
        await stats.stats_handler(message)
    elif message.text == "⚠️ Обратная связь":
        await error_report.error_report_start(message)
    elif message.text == "💎 Подписка":
        await subscription.subscription_handler(message)
