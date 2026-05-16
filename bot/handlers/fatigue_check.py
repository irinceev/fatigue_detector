from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bot.database.fatigue_repo import save_fatigue_record
from bot.handlers.keyboards import main_menu_keyboard
from bot.ml.fatigue_inference import process_image_and_predict
from bot.database.init_db import is_user_premium, get_total_scan_count
from aiogram.fsm.context import FSMContext  # Не забудь импортировать

router = Router()

# --- Вспомогательная функция для текста рекомендаций ---
def get_recommendation_text(score: float) -> str:
    if score <= 40:
        return (
            "🟢 **Низкий уровень усталости**\n\n"
            "• Сделайте перерыв 5-10 минут: встаньте, разомнитесь.\n"
            "• Выпейте стакан воды и перекусите (фрукт, орехи).\n"
            "• Проветрите помещение, добавьте света.\n"
            "• Дайте отдых глазам: посмотрите вдаль 20-30 секунд."
        )
    elif score <= 70:
        return (
            "🟡 **Средний уровень усталости**\n\n"
            "• Прогуляйтесь на свежем воздухе 20-30 минут.\n"
            "• Сделайте дыхательную практику: вдох на 4 счета, выдох на 6.\n"
            "• Смените задачу на более простую на 15-20 минут.\n"
            "• Откажитесь от кофе в пользу чая или воды.\n"
            "• Оставьте 2-3 главные задачи, остальное перенесите."
        )
    else:
        return (
            "🔴 **Высокий уровень усталости**\n\n"
            "• Сделайте короткий сон (power nap) на 20-30 минут.\n"
            "• Полностью прервите работу на 1-2 часа, смените обстановку.\n"
            "• Примите тёплый душ, чтобы расслабить мышцы.\n"
            "• Постарайтесь лечь спать сегодня пораньше (7-9 часов сна)."
        )


# --- Состояния ---
class FatigueStates(StatesGroup):
    waiting_for_photo = State()

# === кнопка меню ===
@router.message(F.text == "🧠 Проверить усталость")
async def start_fatigue_check(message: Message, state: FSMContext):
    await message.answer(
        "📸 Как использовать?\n"
        "Сделайте фото вашего лица (фронтальный ракурс, хорошее освещение).\n"
        "Отправьте фотографию боту.\n"
        "Дождитесь результата анализа.\n"
        "👇 Отправляйте фото в этот диалог в любое время и получите результат! 👇",
        reply_markup=main_menu_keyboard()
    )


# === обработка фото В ЛЮБОЙ МОМЕНТ ===
from bot.handlers.error_report import user_waiting_complaint 

@router.message(F.photo)
async def photo_handler(message: Message):
    user_id = message.from_user.id
    
    # === ДОБАВЛЯЕМ ЭТОТ БЛОК ===
    # Если юзер был в режиме жалобы, но скинул фото — убираем его из режима жалобы
    if user_id in user_waiting_complaint:
        user_waiting_complaint.discard(user_id)
    # ===========================

    # 1. ПРОВЕРКА ЛИМИТОВ
    # Если НЕ премиум И количество сканирований >= 5
    if not is_user_premium(user_id) and get_total_scan_count(user_id) >= 5:
        await message.answer(
            "🚫 **Лимит исчерпан!**\n\n"
            "В бесплатной версии доступно всего 5 проверок.\n"
            "Чтобы проверять усталость без ограничений, оформите Premium-подписку.",
            # Тут можно добавить клавиатуру с кнопкой "💎 Купить Premium"
        )
        return  # ВАЖНО: Прерываем функцию, чтобы фото не обрабатывалось

    # 2. Если всё ок — выполняем анализ
    try:
        file_id = message.photo[-1].file_id
        file = await message.bot.get_file(file_id)
        image_stream = await message.bot.download_file(file.file_path)
        image_bytes = image_stream.read()

        # Предсказание уровня усталости
        score = process_image_and_predict(image_bytes)
        
        # Сохраняем в БД
        save_fatigue_record(
            user_id=message.from_user.id,
            score=score
        )

        await message.answer(
            f"🧠 Уровень усталости: {score:.2f}",
            reply_markup=main_menu_keyboard()
        )
        
        recommendation = get_recommendation_text(score)
        await message.answer(recommendation, parse_mode="Markdown")

    except Exception as e:
        await message.answer(
            f"Ошибка обработки изображения: {e}",
            reply_markup=main_menu_keyboard()
        )
