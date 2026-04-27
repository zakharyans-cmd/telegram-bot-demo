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
async def remind_6h(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    if context.application.chat_data.get(chat_id, {}).get("paid"):
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text="Если актуально — могу помочь закрыть вопрос с заявками 👌"
    )


async def remind_24h(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    if context.application.chat_data.get(chat_id, {}).get("paid"):
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text="Обычно такие задачи лучше не откладывать — заявки продолжают теряться."
    )


async def remind_48h(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    if context.application.chat_data.get(chat_id, {}).get("paid"):
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text="Закрываю диалог. Если нужно — напишите, вернёмся к этому 👍"
    )


def start_reminders(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    context.job_queue.run_once(remind_6h, 21600, chat_id=chat_id, data=chat_id)
    context.job_queue.run_once(remind_24h, 86400, chat_id=chat_id, data=chat_id)
    context.job_queue.run_once(remind_48h, 172800, chat_id=chat_id, data=chat_id)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    chat_id = update.effective_chat.id
    context.application.chat_data.setdefault(chat_id, {})
    context.application.chat_data[chat_id]["paid"] = False

    context.user_data["step"] = "start"

    await update.message.reply_text(
        "Привет 👋\n\n"
        "Покажу, почему у бизнеса теряются заявки и как это исправить.",
        reply_markup=main_menu
    )


# ---------------- РЕЗУЛЬТАТ ----------------
async def send_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tariff = context.user_data.get("tariff")

    if tariff == "Базовый":
        msg = "Результат: заявки перестают теряться даже при медленных ответах."
    elif tariff == "Стандарт":
        msg = "Результат: клиент доводится до диалога автоматически."
    elif tariff == "Под ключ":
        msg = "Результат: вы получаете уже тёплые заявки, готовые к покупке."
    else:
        msg = "Сначала выберите вариант."

    await update.message.reply_text(msg)


# ---------------- ОСНОВНАЯ ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    state = context.user_data.get("step")
    paid = context.application.chat_data.get(chat_id, {}).get("paid", False)

    # ---------------- вход ----------------
    if text == "Разобрать ситуацию":
        context.user_data["step"] = "diagnosis"

        await update.message.reply_text(
            "Скажи честно:\n\n"
            "👉 мало заявок\n"
            "👉 или заявки есть, но они пропадают?"
        )
        return

    # ---------------- диагностика ----------------
    if state == "diagnosis":
        context.user_data["step"] = "pain"

        await update.message.reply_text(
            "Понял.\n\n"
            "До 40% клиентов бизнес теряет просто из-за отсутствия быстрого ответа.\n\n"
            "Хочешь покажу, как это решается?"
        )
        return

    # ---------------- усиление ----------------
    if state == "pain":
        if text.lower() in ["да", "хочу", "ок", "покажи"]:
            context.user_data["step"] = "pricing"

            await update.message.reply_text(
                "Решается системой обработки заявок.\n\n"
                "Есть 3 варианта — в зависимости от глубины автоматизации 👇",
                reply_markup=tariff_menu
            )
        return

    # ---------------- тарифы ----------------
    if text in ["Базовый — 30 000₽", "Стандарт — 50 000₽ ⭐", "Под ключ — 70 000₽"]:

        if "Базовый" in text:
            tariff = "Базовый"
        elif "Стандарт" in text:
            tariff = "Стандарт"
        else:
            tariff = "Под ключ"

        context.user_data["tariff"] = tariff

        await update.message.reply_text(
            f"Отлично.\n\n"
            f"👉 Оплата: {PAYMENT_LINK}\n\n"
            "После оплаты нажмите «Я оплатил»",
            reply_markup=after_menu
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Выбран тариф: {tariff}"
        )

        # запуск дожима ТОЛЬКО если не оплатил
        if not paid:
            start_reminders(context, chat_id)

        return

    # ---------------- ОПЛАТА ----------------
    if text == "Я оплатил":

        context.application.chat_data[chat_id]["paid"] = True

        await update.message.reply_text("Принято 👍 начинаем работу")

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 Оплата подтверждена (chat_id: {chat_id})"
        )

        return

    # ---------------- РЕЗУЛЬТАТ ----------------
    if text == "Результат":
        await send_result(update, context)
        return

    # fallback
    await update.message.reply_text("Выберите действие 👇", reply_markup=main_menu)


# ---------------- APP ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
