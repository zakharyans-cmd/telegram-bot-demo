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

question_menu = ReplyKeyboardMarkup(
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
        intro = "Привет 👋\nСейчас подберём подходящий вариант под вашу задачу.\n\n"
    elif any(x in text for x in ["как", "что", "расскажи", "интересно"]):
        intro = "Привет 👋\nКоротко объясню, как это работает.\n\n"
    else:
        intro = "Привет 👋\nЯ помогаю бизнесу не терять клиентов и превращать обращения в продажи.\n\n"

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
            "Когда нет постоянного администратора, сообщения приходят в разное время "
            "и на часть из них не успевают ответить.\n\n"
            "Система помогает не терять такие обращения."
        )

    elif tariff == "Стандарт":
        msg = (
            "📌 Пример:\n\n"
            "Клиенты часто пишут и не получают быстрый ответ.\n\n"
            "Система сразу реагирует и продолжает диалог без потери интереса."
        )

    elif tariff == "Под ключ":
        msg = (
            "📌 Пример:\n\n"
            "Клиенты пишут в разное время — утром, вечером, в мессенджеры и соцсети.\n"
            "Не всегда получается ответить сразу, и часть людей просто перестаёт ждать.\n\n"
            "Система сразу отвечает на сообщение, уточняет запрос и помогает не терять заинтересованных клиентов."
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

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="Вопрос"
        )
        return

    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=update.message.text
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
            text="Оплата"
        )
        return

    # ---------------- ТАРИФЫ ----------------
    if text == "Базовый — 30 000₽":
        context.user_data["tariff"] = "Базовый"

        msg = (
            "Базовый вариант.\n\n"
            "Подходит для простого приёма обращений или записи на услугу без сложной логики."
        )

    elif text == "Стандарт — 50 000₽ ⭐ Рекомендуем":
        context.user_data["tariff"] = "Стандарт"

        msg = (
            "Стандарт ⭐\n\n"
            "Оптимальный вариант для большинства бизнесов.\n\n"
            "Помогает быстрее обрабатывать обращения и не терять клиентов."
        )

    elif text == "Под ключ — 70 000₽":
        context.user_data["tariff"] = "Под ключ"

        msg = (
            "Под ключ.\n\n"
            "Подходит, когда нужно полностью закрыть обработку входящих обращений: "
            "от первого сообщения клиента до передачи вам заинтересованного клиента.\n"
            "Система сама отвечает и помогает не терять обращения в потоке сообщений."
        )

    else:
        return

    # ---------------- ОФФЕР ----------------
    await update.message.reply_text(
        msg + "\n\n"
        f"Оплата:\n{PAYMENT_LINK}",
        reply_markup=question_menu
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=context.user_data.get("tariff", "")
    )


# ---------------- RUN ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
