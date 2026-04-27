import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "509239406"))

# ---------------- ССЫЛКИ ОПЛАТЫ ----------------
PAY_LINKS = {
    "Базовый": "https://your-payment-link.ru/basic",
    "Стандарт": "https://your-payment-link.ru/standard",
    "Под ключ": "https://your-payment-link.ru/full"
}

# ---------------- КНОПКИ (ШАГ 1) ----------------
tariff_menu = ReplyKeyboardMarkup(
    [
        ["Стандарт ⭐ Рекомендуем"],
        ["Базовый"],
        ["Под ключ"]
    ],
    resize_keyboard=True
)

# ---------------- КНОПКИ ДЕЙСТВИЙ ----------------
action_menu = ReplyKeyboardMarkup(
    [
        ["Результат", "Задать вопрос", "Оплатить"]
    ],
    resize_keyboard=True
)

# ---------------- КНОПКИ ОПЛАТЫ ----------------
pay_menu = ReplyKeyboardMarkup(
    [
        ["Стандарт — 50 000₽ ⭐ Рекомендуем"],
        ["Базовый — 30 000₽"],
        ["Под ключ — 70 000₽"]
    ],
    resize_keyboard=True
)


# ---------------- ДОЖИМ ----------------
async def remind_6h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Если актуально — помогу подобрать подходящий вариант 👌"
    )


async def remind_24h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Можно
