**Telegram-бот для оценки уровня усталости по фото лица.**  
Пользователь отправляет селфи — бот анализирует лицо с помощью нейросети и возвращает числовую оценку усталости (0–100) с персональными рекомендациями.

---

## 🎯 Как это работает

```
Пользователь → фото → InsightFace (детекция + ArcFace-эмбеддинг) → FatigueRegressor (512→1) → оценка 0–100 → рекомендации
```

1. Фото принимается ботом через Telegram
2. Лицо детектируется моделью **InsightFace (buffalo_l)**
3. ArcFace извлекает **512-мерный эмбеддинг** лица
4. Линейный регрессор `FatigueRegressor` предсказывает **уровень усталости**
5. Результат сохраняется в базу, строится график динамики

<img width="487" height="588" alt="Screenshot_279" src="https://github.com/user-attachments/assets/76c60f57-d84c-418c-ac69-7fa09f69a258" />
<img width="465" height="610" alt="Screenshot_278" src="https://github.com/user-attachments/assets/b308ba96-6dfd-4ef9-810e-c86f699362a8" />

---

## ✨ Возможности

| Функция | Free | Premium |
|---|---|---|
| Проверка усталости по фото | 5 раз | ∞ |
| Рекомендации по уровню усталости | ✅ | ✅ |
| График динамики усталости за месяц | ✅ | ✅ |
| История сканирований | ✅ | ✅ |
| Отправка обратной связи | ✅ | ✅ |

---

## 🛠 Стек

- **Python 3.10**
- **aiogram 3.x** — Telegram Bot API
- **InsightFace** — детекция лиц + ArcFace-эмбеддинги
- **PyTorch** — модель регрессии усталости
- **OpenCV** — предобработка изображений
- **SQLite** — хранение пользователей, сканирований, подписок
- **Matplotlib** — графики динамики
- **APScheduler** — автоотключение истёкших подписок

---

## 📁 Структура проекта

```
fatigue_detector/
├── bot/
│   ├── config.py                  # Конфигурация (токен, пути, ID админов)
│   ├── main.py                    # Точка входа, регистрация роутеров
│   ├── handlers/
│   │   ├── menu.py                # Главное меню
│   │   ├── fatigue_check.py       # Приём фото и анализ усталости
│   │   ├── stats.py               # График динамики
│   │   ├── info.py                # Информация о боте
│   │   ├── subscription.py        # Управление подписками
│   │   ├── scheduler.py           # Автоотключение истёкших подписок
│   │   ├── error_report.py        # Обратная связь
│   │   ├── admin.py               # Команды администратора
│   │   └── keyboards.py           # Клавиатуры
│   ├── database/
│   │   ├── init_db.py             # Схема БД и вспомогательные функции
│   │   ├── fatigue_repo.py        # Запись результатов анализа
│   │   ├── feedback_repo.py       # Запись обратной связи
│   │   └── classify.py            # Классификация уровня усталости
│   └── ml/
│       ├── arcface_loader.py      # Загрузка InsightFace и регрессора
│       ├── fatigue_inference.py   # Пайплайн инференса
│       └── model/
│           ├── model.py           # Архитектура FatigueRegressor
│           ├── infer_utils.py     # Утилиты предобработки
│           └── fatigue_model.pth  # Веса модели
├── requirements.txt
├── .env.example                   # Пример переменных окружения
└── .gitignore
```

---

## 🚀 Запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-username/fatigue-detector-bot.git
cd fatigue-detector-bot
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Создать файл `.env`

```bash
cp .env.example .env
```

Заполнить `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321
DB_PATH=bot/database/database.sqlite
```

### 4. Загрузить модели InsightFace

При первом запуске InsightFace автоматически скачает `buffalo_l`.  
Убедитесь, что `bot/ml/model/fatigue_model.pth` присутствует в репозитории.

### 5. Запустить

```bash
python -m bot.main
```

---

## ⚙️ Конфигурация

Все параметры задаются через переменные окружения (файл `.env`):

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен бота из [@BotFather](https://t.me/BotFather) |
| `ADMIN_IDS` | ID администраторов через запятую |
| `DB_PATH` | Путь к SQLite-базе |

---

## 👑 Команды администратора

| Команда | Описание |
|---|---|
| `/give_premium <user_id> [days]` | Выдать Premium на N дней (по умолчанию 30) |
| `/remove_premium <user_id>` | Отозвать Premium |

---

## 🗄 База данных

SQLite с тремя основными таблицами:

- **`users`** — пользователи и флаг премиума
- **`fatigue_records`** — история сканирований с оценками
- **`subscriptions`** — Premium-подписки с датами начала и конца
- **`feedback`** — обратная связь от пользователей

---
