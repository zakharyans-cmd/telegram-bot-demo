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


# ---------------- ДОЖИМ ----------------
async def remind_6h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Если актуально — помогу подобрать оптимальный вариант под вашу задачу 👌"
    )


async def remind_24h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Часто клиенты возвращаются позже, чтобы спокойно всё решить. Я на связи 👍"
    )


async def remind_48h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Закрою диалог, но если понадобится — просто напишите, помогу 👍"
    )


def start_reminders(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    job = context.job_queue
    job.run_once(remind_6h, 21600, chat_id=chat_id)
    job.run_once(remind_24h, 86400, chat_id=chat_id)
    job.run_once(remind_48h, 172800, chat_id=chat_id)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()

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
            "Когда нет постоянного администратора, сообщения приходят в разное время "
            "и часть обращений легко потерять.\n\n"
            "Система фиксирует каждое сообщение, чтобы клиент не исчез."
        )

    elif tariff == "Стандарт":
        msg = (
            "📌 Пример:\n\n"
            "Клиент написал и не получил быстрый ответ — интерес начинает снижаться.\n\n"
            "Система продолжает диалог и удерживает внимание до контакта."
        )

    elif tariff == "Под ключ":
        msg = (
            "📌 Пример:\n\n"
            "Клиенты пишут в разное время и часто не доходят до общения с менеджером.\n\n"
            "Система сама отвечает, уточняет запрос и передаёт уже заинтересованных клиентов."
        )

    else:
        msg = "Сначала выберите вариант."

    await update.message.reply_text(msg)


# ---------------- ОСНОВНАЯ ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # пример
    if text == "Пример":
        await send_example(update, context)
        return

    # вопрос
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

    # оплата
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

    # тарифы
    if text == "Базовый — 30 000₽":
        context.user_data["tariff"] = "Базовый"

        msg = (
            "🟢 Базовый вариант.\n\n"
            "Роль: приём сообщений.\n"
            "Помогает не терять обращения клиентов."
        )

    elif text == "Стандарт — 50 000₽ ⭐ Рекомендуем":
        context.user_data["tariff"] = "Стандарт"

        msg = (
            "🔵 Стандарт ⭐\n\n"
            "Роль: ведение диалога.\n"
            "Помогает удерживать клиента и доводить его до интереса."
        )

    elif text == "Под ключ — 70 000₽":
        context.user_data["tariff"] = "Под ключ"

        msg = (
            "🔴 Под ключ.\n\n"
            "Роль: полный контроль потока.\n"
            "Система обрабатывает обращения и передаёт только заинтересованных клиентов."
        )

    else:
        return

    await update.message.reply_text(
        msg + "\n\n"
        f"Оплата:\n{PAYMENT_LINK}",
        reply_markup=question_menu
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=context.user_data.get("tariff", "")
    )

    # 👉 запускаем дожим
    if not context.chat_data.get("paid"):
        start_reminders(context, update.effective_chat.id)


# ---------------- RUN ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
