import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 509239406
PAYMENT_LINK = "https://your-payment-link.ru"


# ---------------- КНОПКИ ----------------
main_menu = ReplyKeyboardMarkup(
    [["Разобрать ситуацию"]],
    resize_keyboard=True
)

tariff_menu = ReplyKeyboardMarkup(
    [
        ["Базовый — 30 000₽"],
        ["Стандарт — 50 000₽ ⭐"],
        ["Под ключ — 70 000₽"]
    ],
    resize_keyboard=True
)

after_menu = ReplyKeyboardMarkup(
    [["Я оплатил", "Результат"]],
    resize_keyboard=True
)


# ---------------- ДОЖИМ ----------------
async def remind(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data

    chat_data = context.application.chat_data.get(chat_id, {})
    if chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text="Если актуально — могу помочь закрыть вопрос с потерей заявок 👌"
    )


def start_reminders(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    context.job_queue.run_once(remind, 21600, chat_id=chat_id, data=chat_id)
    context.job_queue.run_once(remind, 86400, chat_id=chat_id, data=chat_id)
    context.job_queue.run_once(remind, 172800, chat_id=chat_id, data=chat_id)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    context.user_data.clear()
    context.user_data["step"] = "start"

    context.application.chat_data.setdefault(chat_id, {})
    context.application.chat_data[chat_id]["paid"] = False

    await update.message.reply_text(
        "Привет 👋\n\n"
        "Покажу, почему бизнес теряет заявки и как это исправить.",
        reply_markup=main_menu
    )


# ---------------- РЕЗУЛЬТАТ ----------------
async def send_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tariff = context.user_data.get("tariff")

    if tariff == "Базовый":
        msg = "Результат: заявки перестают теряться даже при медленных ответах."
    elif tariff == "Стандарт":
        msg = "Результат: клиент сам доводится до диалога."
    elif tariff == "Под ключ":
        msg = "Результат: приходят уже тёплые заявки."
    else:
        msg = "Сначала выберите тариф."

    await update.message.reply_text(msg)


# ---------------- ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text or ""
    text = raw_text.strip().lower()

    chat_id = update.effective_chat.id
    step = context.user_data.get("step")

    paid = context.application.chat_data.get(chat_id, {}).get("paid", False)

    # ---------------- вход ----------------
    if text == "разобрать ситуацию":
        context.user_data["step"] = "diagnosis"

        await update.message.reply_text(
            "Что ближе к вашей ситуации?\n\n"
            "👉 мало заявок\n"
            "👉 заявки есть, но они теряются"
        )
        return

    # ---------------- диагностика ----------------
    if step == "diagnosis":
        context.user_data["step"] = "pain"

        await update.message.reply_text(
            "Понял.\n\n"
            "До 40% клиентов теряется из-за отсутствия быстрого ответа.\n\n"
            "Хочешь покажу решение?"
        )
        return

    # ---------------- боль ----------------
    if step == "pain":
        if text in ["да", "хочу", "ок", "покажи"]:
            context.user_data["step"] = "offer"

            await update.message.reply_text(
                "Решается системой обработки заявок.\n\n"
                "Есть 3 уровня 👇",
                reply_markup=tariff_menu
            )
        return

    # ---------------- тарифы ----------------
    if "30 000" in text:
        tariff = "Базовый"
    elif "50 000" in text:
        tariff = "Стандарт"
    elif "70 000" in text:
        tariff = "Под ключ"
    else:
        tariff = None

    if tariff:
        context.user_data["tariff"] = tariff

        await update.message.reply_text(
            f"Отлично 👍\n\n"
            f"👉 Оплата: {PAYMENT_LINK}\n\n"
            "После оплаты нажмите «Я оплатил»",
            reply_markup=after_menu
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Выбран тариф: {tariff}"
        )

        if not paid:
            start_reminders(context, chat_id)

        return

    # ---------------- оплата ----------------
    if text == "я оплатил":
        context.application.chat_data[chat_id]["paid"] = True

        await update.message.reply_text("Принято 👍 начинаем работу")

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 Оплата подтверждена ({chat_id})"
        )
        return

    # ---------------- результат ----------------
    if text == "результат":
        await send_result(update, context)
        return

    # ---------------- fallback ----------------
    await update.message.reply_text(
        "Нажмите кнопку ниже 👇",
        reply_markup=main_menu
    )


# ---------------- APP ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
