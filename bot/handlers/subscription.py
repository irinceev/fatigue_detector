# from aiogram import Router, F, types
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from bot.database.init_db import is_user_premium

# router = Router()

# @router.message(F.text == "💎 Подписка")
# async def subscription_handler(message: types.Message):
#     user_id = message.from_user.id

#     # 1. Сначала проверяем, вдруг он уже купил
#     if is_user_premium(user_id):
#         await message.answer(
#             "🌟 **У вас уже активирован Premium!**\n\n"
#             "Вы можете пользоваться ботом без ограничений.\n"
#             "Спасибо за поддержку! 💖",
#             parse_mode="Markdown"
#         )
#         return

#     # 2. Если премиума нет — предлагаем купить
#     text = (
#         "💎 **Premium**\n\n"
#         "В бесплатной версии доступно всего **5 сканирований**.\n"
#         "Оформите подписку, чтобы снять все ограничения!\n\n"
#         "🔥 **Что дает Premium?**\n"
#         "✅ Безлимитное количество проверок\n"
#         "✅ Доступ к расширенной статистике\n"
#         "✅ Приоритетная поддержка\n\n"
#         "💸 **Цена:** 199₽ (ежемесячная)"
#     )

#     # Создаем Инлайн-кнопку под сообщением
#     # Пока нет банка, кнопка ведет либо к тебе в ЛС, либо это заглушка
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [
#             InlineKeyboardButton(text="💳 Оплатить (Картой)", callback_data="pay_stub")
#         ],
#         [
#             # Замени YOUR_USERNAME на свой ник без @
#             InlineKeyboardButton(text="✍️ Написать админу", url="https://t.me/andrewshtop") 
#         ]
#     ])

#     await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


# # === Обработка нажатия на кнопку "Оплатить" (Заглушка) ===
# @router.callback_query(F.data == "pay_stub")
# async def payment_stub_handler(callback: types.CallbackQuery):
#     # Показываем всплывающее уведомление (alert)
#     await callback.answer(
#         "Автоматическая оплата пока подключается.\n"
#         "Пожалуйста, напишите админу для оформления!", 
#         show_alert=True
#     )
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.init_db import is_user_premium, create_subscription

router = Router()

@router.message(F.text == "💎 Подписка")
async def subscription_handler(message: types.Message):
    user_id = message.from_user.id

    # 1. Сначала проверяем, вдруг он уже купил
    if is_user_premium(user_id):
        await message.answer(
            "🌟 **У вас уже активирован Premium!**\n\n"
            "Вы можете пользоваться ботом без ограничений.\n"
            "Спасибо за поддержку! 💖",
            parse_mode="Markdown"
        )
        return

    # 2. Если премиума нет — предлагаем купить
    text = (
        "💎 **Premium**\n\n"
        "В бесплатной версии доступно всего **5 сканирований**.\n"
        "Оформите подписку, чтобы снять все ограничения!\n\n"
        "🔥 **Что дает Premium?**\n"
        "✅ Безлимитное количество проверок\n"
        "✅ Доступ к расширенной статистике\n"
        "✅ Приоритетная поддержка\n\n"
        "💸 **Цена:** 199₽ (ежемесячная)"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Оплатить (Картой)", callback_data="pay_stub")
        ],
        [
            InlineKeyboardButton(text="✍️ Написать админу", url="https://t.me/andrewshtop") 
        ]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

# === ТЕСТОВЫЙ РЕЖИМ: Выдаем Premium при нажатии ===
@router.callback_query(F.data == "pay_stub")
async def payment_test_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    print("🔥 НАЖАЛИ КНОПКУ ОПЛАТЫ!")
    
    # Выдаем пробную подписку на 30 дней
    success = create_subscription(user_id, days=30)
    
    if success:
        # Меняем сообщение на успешное
        await callback.message.edit_text(
            "**🤖 Бот находится в тестовом режиме**\n\n"
            "🎉 **Пробная подписка активирована!**\n\n"
            "✅ **Premium на 30 дней** выдан **бесплатно**\n"
            "✅ Теперь **безлимит** на все функции\n\n"
            "💡 *Спасибо за тестирование!* 🎮",
            parse_mode="Markdown"
        )
    else:
        await callback.answer("⚠️ У вас уже есть активная подписка!", show_alert=True)
    
    # Закрываем callback
    await callback.answer()