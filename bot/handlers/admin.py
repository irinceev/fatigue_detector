from aiogram import Router, types
from aiogram.filters import CommandObject, Command
# Импортируем НОВЫЕ функции (вместо set_user_premium)
from bot.database.init_db import create_subscription, cancel_subscription
from bot.config import ADMIN_IDS

router = Router()

@router.message(Command("give_premium"))
async def give_premium_command(message: types.Message, command: CommandObject):
    # Логирование для отладки
    print(f"👤 Кто пишет: {message.from_user.id}")
    print(f"👑 Админы: {ADMIN_IDS}")
    
    # 1. Проверка на админа
    if message.from_user.id not in ADMIN_IDS:
        print("❌ Отказ: не админ")
        return
    
    print("✅ Доступ разрешен")

    # 2. Проверка аргументов
    if command.args is None:
        await message.answer("Ошибка: введите ID пользователя.\nПример: `/give_premium 123456789` (на 30 дней)\nИли: `/give_premium 123456789 60`")
        return

    try:
        # Разбиваем аргументы (ID и дни)
        args = command.args.split()
        user_id = int(args[0])
        
        # Если вторым числом указали дни, берем их. Иначе - 30.
        days = int(args[1]) if len(args) > 1 else 30
        
        # 3. Выдаем подписку через НОВУЮ функцию
        # Она добавит запись в subscriptions и поставит галочку в users
        success = create_subscription(user_id, days=days)
        
        if success:
            await message.answer(f"✅ Пользователю `{user_id}` выдан Premium на {days} дней!")
            
            # Уведомление юзеру
            try:
                await message.bot.send_message(user_id, f"🎉 Вам выдан Premium-статус на {days} дней! Лимиты сняты.")
            except:
                pass
        else:
            await message.answer(f"⚠️ У пользователя `{user_id}` уже есть активная подписка. Сначала отмените её или дождитесь окончания.")

    except ValueError:
        await message.answer("Ошибка: ID и количество дней должны быть числами.")


@router.message(Command("remove_premium"))
async def remove_premium_command(message: types.Message, command: CommandObject):
    # 1. Проверка на админа
    if message.from_user.id not in ADMIN_IDS:
        return

    # 2. Проверка аргументов
    if command.args is None:
        await message.answer("Ошибка: введите ID пользователя.\nПример: /remove_premium 123456789")
        return

    try:
        user_id = int(command.args)
        
        # 3. ЗАБИРАЕМ ПРЕМИУМ через НОВУЮ функцию
        # Она закроет подписку в базе и снимет галочку в users
        cancel_subscription(user_id)
        
        await message.answer(f"❌ Premium и подписка у пользователя `{user_id}` отключены.")
        
        # Уведомление юзеру
        try:
            await message.bot.send_message(user_id, "⚠️ Ваш Premium-статус отключен администратором.")
        except:
            pass

    except ValueError:
        await message.answer("Ошибка: ID должен быть числом.")
