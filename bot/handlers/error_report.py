from aiogram import Router, types
from bot.handlers.keyboards import main_menu_keyboard
from bot.database.feedback_repo import save_feedback

router = Router()
user_waiting_complaint = set()

# Вход в раздел обратной связи
@router.message(lambda m: m.text == "⚠️ Обратная связь")
async def error_report_start(message: types.Message):
    user_waiting_complaint.add(message.from_user.id)

    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await message.answer(
        "⚠️ Напишите, что хотите передать разработчикам (только текстом).",
        reply_markup=kb
    )

# Получение жалобы
@router.message()
async def receive_complaint(message: types.Message):
    # Обработка кнопки "Назад"
    if message.text == "⬅️ Назад":
        user_waiting_complaint.discard(message.from_user.id)
        await message.answer(
            "Главное меню. Выберите действие:",
            reply_markup=main_menu_keyboard()
        )
        return

    # Если пользователь не находится в режиме жалобы — игнорируем
    if message.from_user.id not in user_waiting_complaint:
        return

    # Сохраняем жалобу через репозиторий
    user_waiting_complaint.remove(message.from_user.id)
    save_feedback(user_id=message.from_user.id, text=message.text)

    await message.answer(
        "Спасибо за обращение! Мы обязательно его рассмотрим.",
        reply_markup=main_menu_keyboard()
    )
