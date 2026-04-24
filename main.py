import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 509239406

PAYMENT_LINK = "https://your-payment-link.ru"


# ---------------- КНОПКИ ----------------
tariff_menu = ReplyKeyboardMarkup(
    [
        ["Базовый — 30 000₽"],
        ["Стандарт — 40 000₽"],
        ["Под ключ — 60 000₽"]
    ],
    resize_keyboard=True
)


# ---------------- ДОЖИМ ----------------
async def remind_6h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Напомню: система может продолжать обрабатывать заявки без участия менеджера."
    )


async def remind_24h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Часто заявки теряются просто из-за задержки ответа. Это можно убрать автоматизацией."
    )


async def remind_48h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Если будет актуально — просто напишите /start, я продолжу."
    )


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()

    await update.message.reply_text(
        "Я помогаю бизнесу не терять заявки и быстрее доводить клиентов до покупки.\n\n"
        "Выберите вариант:",
        reply_markup=tariff_menu
    )


# ---------------- ЛОГИКА ТАРИФОВ ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ---------------- БАЗОВЫЙ ----------------
    if text == "Базовый — 30 000₽":
        context.user_data["tariff"] = "Базовый"
        context.user_data["price"] = "30k"

        await update.message.reply_text(
            "Базовый вариант.\n\n"
            "Подходит, если нужно быстро закрыть обработку заявок:\n"
            "— быстрый ответ клиенту\n"
            "— сбор контакта\n"
            "— передача менеджеру"
        )

    # ---------------- СТАНДАРТ ----------------
    elif text == "Стандарт — 40 000₽":
        context.user_data["tariff"] = "Стандарт"
        context.user_data["price"] = "40k"

        await update.message.reply_text(
            "Стандарт.\n\n"
            "Подходит, если заявки уже есть, но часть теряется.\n\n"
            "Система помогает:\n"
            "— отвечать сразу\n"
            "— уточнять запрос клиента\n"
            "— передавать только тёплые заявки"
        )

    # ---------------- ПОД КЛЮЧ ----------------
    elif text == "Под ключ — 60 000₽":
        context.user_data["tariff"] = "Под ключ"
        context.user_data["price"] = "60k"

        await update.message.reply_text(
            "Под ключ.\n\n"
            "Это уже полноценная система обработки заявок.\n\n"
            "Она снижает потери и помогает менеджерам работать только с тёплыми клиентами."
        )

    else:
        return

    # ---------------- ОФФЕР (МЯГКИЙ) ----------------
    await update.message.reply_text(
        f"Стоимость: {context.user_data['price']}\n\n"
        "Если подходит — можно подключить по ссылке ниже:\n"
        f"{PAYMENT_LINK}\n\n"
        "Если есть вопросы — лучше сначала обсудим 👍",
        reply_markup=ReplyKeyboardMarkup(
            [["Я оплатил", "Задать вопрос"]],
            resize_keyboard=True
        )
    )

    # ---------------- АДМИН ----------------
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "Новый лид\n\n"
            f"Тариф: {context.user_data['tariff']}\n"
            f"Цена: {context.user_data['price']}"
        )
    )

    # ---------------- ДОЖИМ ----------------
    if not context.chat_data.get("reminders_set"):
        context.job_queue.run_once(remind_6h, 21600, chat_id=update.effective_chat.id)
        context.job_queue.run_once(remind_24h, 86400, chat_id=update.effective_chat.id)
        context.job_queue.run_once(remind_48h, 172800, chat_id=update.effective_chat.id)
        context.chat_data["reminders_set"] = True


# ---------------- ВОПРОСЫ ----------------
async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Я оплатил":
        context.chat_data["paid"] = True

        await update.message.reply_text(
            "Принял оплату 👍 Начинаю работу."
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="Оплата — проверь"
        )

    elif text == "Задать вопрос":
        context.user_data["step"] = "question"

        await update.message.reply_text(
            "Хорошо 👍 Напишите вопрос — отвечу вам здесь."
        )

    elif context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Вопрос клиента:\n\n{text}"
        )

        await update.message.reply_text(
            "Спасибо, передал. Ответим вам в ближайшее время 👍"
        )


# ---------------- RUN ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, payment))

app.run_polling()
