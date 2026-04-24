import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 509239406

PAYMENT_LINK = "https://your-payment-link.ru"


# ---------------- КНОПКИ ----------------
tariff_menu = ReplyKeyboardMarkup(
    [
        ["Стандарт — 50 000₽ ⭐ Рекомендуем"],
        ["Базовый — 30 000₽"],
        ["Под ключ — 70 000₽"]
    ],
    resize_keyboard=True
)


action_menu = ReplyKeyboardMarkup(
    [
        ["Я оплатил", "Пример", "Задать вопрос"]
    ],
    resize_keyboard=True
)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()

    text = (update.message.text or "").lower()

    if any(x in text for x in ["цена", "стоимость", "сколько"]):
        intro = "Привет 👋\nСейчас быстро подберём подходящий вариант под вашу задачу.\n\n"
    elif any(x in text for x in ["как", "что", "расскажи", "интересно"]):
        intro = "Привет 👋\nКоротко покажу, как это работает и что подойдёт вам.\n\n"
    else:
        intro = "Привет 👋\nЯ помогаю бизнесу не терять клиентов и превращать обращения в заявки.\n\n"

    await update.message.reply_text(
        intro + "Выберите вариант:",
        reply_markup=tariff_menu
    )


# ---------------- ПРИМЕР ----------------
async def send_example(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tariff = context.user_data.get("tariff")

    if tariff == "Базовый":
        msg = (
            "📌 Пример:\n\n"
            "Когда нет постоянного администратора, сообщения приходят в разное время, "
            "и на часть из них просто не успевают ответить.\n\n"
            "Система помогает не терять такие обращения."
        )

    elif tariff == "Стандарт":
        msg = (
            "📌 Пример:\n\n"
            "Часто клиенты пишут и уходят, если не получают быстрый ответ.\n\n"
            "Система сразу реагирует и ведёт диалог дальше без потери интереса."
        )

    elif tariff == "Под ключ":
        msg = (
            "📌 Пример:\n\n"
            "Когда поток обращений большой, менеджеры не успевают обрабатывать всех.\n\n"
            "Система берёт первый контакт на себя и передаёт уже тёплых клиентов."
        )

    else:
        msg = "Сначала выберите вариант."

    await update.message.reply_text(msg)


# ---------------- ОСНОВНАЯ ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ---------------- ПРИМЕР ----------------
    if text == "Пример":
        await send_example(update, context)
        return

    # ---------------- ВОПРОС ----------------
    if text == "Задать вопрос":
        context.user_data["step"] = "question"

        await update.message.reply_text(
            "С Вами скоро свяжутся 👍"
        )

        # уведомление админу (без лишних данных)
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="Клиент написал вопрос"
        )
        return

    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Вопрос:\n\n{text}"
        )

        await update.message.reply_text(
            "С Вами скоро свяжутся 👍"
        )
        return

    # ---------------- ОПЛАТА ----------------
    if text == "Я оплатил":
        context.chat_data["paid"] = True

        await update.message.reply_text(
            "Принято. Начинаем работу 👍"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="Оплата получена"
        )
        return

    # ---------------- ТАРИФЫ ----------------
    if text == "Базовый — 30 000₽":
        context.user_data["tariff"] = "Базовый"

        msg = (
            "Ты выбрал базовый вариант.\n\n"
            "Подходит, если нужно просто не терять входящие обращения."
        )

    elif text == "Стандарт — 50 000₽ ⭐ Рекомендуем":
        context.user_data["tariff"] = "Стандарт"

        msg = (
            "Это оптимальный вариант.\n\n"
            "Он закрывает основную проблему — быстрая реакция и удержание клиента в диалоге."
        )

    elif text == "Под ключ — 70 000₽":
        context.user_data["tariff"] = "Под ключ"

        msg = (
            "Полное решение.\n\n"
            "Если у тебя поток заявок и важно не терять ни одного клиента."
        )

    else:
        return

    # ---------------- ПЕРЕХОД В ДЕЙСТВИЕ ----------------
    await update.message.reply_text(
        msg + "\n\n"
        f"Стоимость: указана в выбранном варианте\n\n"
        f"Оплата:\n{PAYMENT_LINK}",
        reply_markup=action_menu
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text="Клиент выбрал вариант"
    )


# ---------------- RUN ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
