from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ℹ️ Инфо")],
            [KeyboardButton(text="🧠 Проверить усталость")],
            [KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="💎 Подписка"), KeyboardButton(text="⚠️ Обратная связь")] 
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # клавиатура всегда видима
    )
    return kb
