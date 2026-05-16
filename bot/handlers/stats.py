import io
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from aiogram import Router, F, types
from aiogram.types import BufferedInputFile
from bot.database.init_db import DB_PATH
from bot.handlers.keyboards import main_menu_keyboard

router = Router()

# === 1. Получаем сырые данные из БД ===
def get_raw_stats(user_id: int, days: int = 30):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    
    # Берем ВСЕ записи за месяц
    cursor.execute("""
        SELECT fatigue_score, created_at 
        FROM fatigue_records 
        WHERE user_id = ? AND created_at >= ?
        ORDER BY created_at ASC
    """, (user_id, start_date))
    
    data = cursor.fetchall()
    conn.close()
    return data

# === 2. Обрабатываем данные: считаем среднее за день ===
def get_daily_averages(raw_data):
    # Словарь: { "2023-10-12": [45, 50, 55], ... }
    grouped_by_date = defaultdict(list)
    
    for score, timestamp_str in raw_data:
        # Превращаем строку времени в дату (без часов и минут)
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        date_key = dt.date() # только дата (год-месяц-день)
        grouped_by_date[date_key].append(score)
    
    # Считаем среднее для каждой даты
    # Результат: список кортежей [(date_obj, avg_score), ...]
    daily_stats = []
    for date_obj, scores in grouped_by_date.items():
        avg_score = sum(scores) / len(scores)
        daily_stats.append((date_obj, avg_score))
    
    # Сортируем по дате
    daily_stats.sort(key=lambda x: x[0])
    return daily_stats

# === 3. Строим график по средним значениям ===
def create_fatigue_chart(daily_data):
    if not daily_data:
        return None

    # Разделяем данные
    dates = [row[0] for row in daily_data]
    scores = [row[1] for row in daily_data]

    plt.figure(figsize=(10, 6))
    ax = plt.gca()

    # Строим график
    # Увеличил толщину линии и размер точек для красоты на белом фоне
    plt.plot(dates, scores, marker='o', linestyle='-', color='#007AFF', linewidth=3, markersize=8)
    
    plt.title("Динамика усталости (среднее за день)")
    plt.ylabel("Баллы (0-100)")
    
    # === НАСТРОЙКА ОСИ X (ДАТЫ) ===
    # Устанавливаем формат даты "День.Месяц"
    date_fmt = mdates.DateFormatter('%d.%m')
    ax.xaxis.set_major_formatter(date_fmt)

    # Если данных не очень много (меньше 15 дней), 
    # заставляем matplotlib подписать КАЖДУЮ дату, где есть точка
    if len(dates) <= 15:
        plt.xticks(dates) 
    else:
        # Если данных много, ставим подписи автоматом, чтобы текст не слипся
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    # Поворачиваем даты, чтобы влезали
    plt.gcf().autofmt_xdate()

    # === УБИРАЕМ ЛИШНЕЕ ===
    # Убираем сетку (клетки)
    # plt.grid(False) — по умолчанию выключена, но можно явно не писать
    
    # Убираем рамки сверху и справа (так стильнее без сетки)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Ограничиваем ось Y
    plt.ylim(0, 105)

    # Зоны усталости (оставляем фоновые цвета, они полезны)
    plt.axhspan(0, 40, color='#4CD964', alpha=0.1, label='Низкая')   # Приятный зеленый
    plt.axhspan(40, 70, color='#FFCC00', alpha=0.1, label='Средняя') # Мягкий желтый
    plt.axhspan(70, 100, color='#FF3B30', alpha=0.1, label='Высокая') # Мягкий красный
    
    # plt.legend(loc='upper left', frameon=False) # Легенда без рамки

    # Сохраняем
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()
    return buf

# === Хендлер ===
@router.message(F.text == "📊 Статистика")
async def stats_handler(message: types.Message):
    user_id = message.from_user.id
    
    # 1. Получаем сырые данные
    raw_data = get_raw_stats(user_id, days=30)
    
    if not raw_data:
        await message.answer("📊 Нет данных за последний месяц.", reply_markup=main_menu_keyboard())
        return

    # 2. Превращаем их в средние за день
    daily_data = get_daily_averages(raw_data)

    # 3. Формируем текст (последние 10 дней)
    text_lines = [
        "📊 **Средняя усталость по дням:**",
        "(🟢 — низкая, 🟡 — средняя, 🔴 — высокая)\n"
    ]
    
    # Берем последние 10 дней и разворачиваем (сначала новые)
    last_days = daily_data[-10:][::-1]
    
    for date_obj, avg_score in last_days:
        formatted_date = date_obj.strftime("%d.%m.%Y")
        icon = "🟢" if avg_score <= 33 else "🟡" if avg_score <= 66 else "🔴"
        text_lines.append(f"{icon} `{formatted_date}` — **{avg_score:.1f}**")
    
    # Общая средняя за весь месяц
    total_avg = sum([x[1] for x in daily_data]) / len(daily_data)
    text_lines.append(f"\n📈 **В среднем за месяц:** {total_avg:.1f}")

    response_text = "\n".join(text_lines)

    # 4. График
    chart_buf = create_fatigue_chart(daily_data)
    
    if chart_buf:
        photo = BufferedInputFile(chart_buf.read(), filename="chart_daily.png")
        await message.answer_photo(
            photo=photo,
            caption=response_text,
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    else:
        await message.answer(response_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
