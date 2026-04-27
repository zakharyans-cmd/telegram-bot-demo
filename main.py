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
        ["Я оплатил", "Результат", "Задать вопрос"]
    ],
    resize_keyboard=True
)


# ---------------- ДОЖИМ ----------------
async def remind_6h(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Если актуально — помогу подобрать подходящий вариант 👌"
    )


async def remind_24h(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Можно спокойно вернуться к этому позже — я на связи 👍"
    )


async def remind_48h(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Закрою диалог, но если понадобится — просто напишите 👍"
    )


def start_reminders(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    jobs = []

    jobs.append(context.job_queue.run_once(remind_6h, 21600, chat_id=chat_id))
    jobs.append(context.job_queue.run_once(remind_24h, 86400, chat_id=chat_id))
    jobs.append(context.job_queue.run_once(remind_48h, 172800, chat_id=chat_id))

    context.chat_data["jobs"] = jobs
    context.chat_data["reminders_started"] = True


def stop_reminders(context: ContextTypes.DEFAULT_TYPE):
    for job in context.chat_data.get("jobs", []):
        job.schedule_removal()

    context.chat_data["jobs"] = []
    context.chat_data["reminders_started"] = False


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()

    await update.message.reply_text(
        "Привет 👋\n"
        "Я помогаю бизнесу не терять клиентов и превращать обращения в продажи.\n\n"
        "Выберите вариант:",
        reply_markup=tariff_menu
    )


# ---------------- РЕЗУЛЬТАТ ----------------
async def send_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tariff = context.user_data.get("tariff")

    if tariff == "Базовый":
        msg = (
            "Результат:\n\n"
            "Система фиксирует каждое сообщение 24/7 и ни один клиент не потеряется"
        )

    elif tariff == "Стандарт":
        msg = (
            "Результат:\n\n"
            "Интерес клиента не падает, даже если он написал ночью — "
            "система продолжает диалог и удерживает внимание до контакта"
        )

    elif tariff == "Под ключ":
        msg = (
            "Результат:\n\n"
            "Общение с клиентами выстроено и контролируется — "
            "к вам приходят уже подготовленные к диалогу люди"
        )

    else:
        msg = "Сначала выберите вариант."

    await update.message.reply_text(msg)


# ---------------- ОСНОВНАЯ ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # результат
    if text == "Результат":
        await send_result(update, context)
        return

    # вопрос
    if text == "Задать вопрос":
        context.user_data["step"] = "question"

        await update.message.reply_text(
            "Напишите ваш вопрос — я передам его специалисту 👇"
        )
        return

    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Вопрос от клиента:\n\n{update.message.text}"
        )

        await update.message.reply_text(
            "С Вами скоро свяжутся 👍"
        )

        context.user_data["step"] = None
        return

    # оплата
    if text == "Я оплатил":
        context.chat_data["paid"] = True

        # стоп напоминаний
        stop_reminders(context)

        await update.message.reply_text(
            "Принято. Начинаем работу 👍"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="💰 Клиент сообщил об оплате"
        )
        return

    # тарифы
    if text == "Базовый — 30 000₽":
        context.user_data["tariff"] = "Базовый"

        msg = (
            "Базовый вариант\n\n"
            "Подходит для простого приема обращений и записи на услугу\n\n"
            "— быстрые ответы\n"
            "— отсев случайных обращений"
        )

    elif text == "Стандарт — 50 000₽ ⭐ Рекомендуем":
        context.user_data["tariff"] = "Стандарт"

        msg = (
            "Стандарт ⭐\n\n"
            "Оптимальное решение для большинства бизнесов\n"
            "Система помогает быстро отвечать, удерживать клиента и его интерес\n\n"
            "— настройка логики под ваш бизнес\n"
            "— настройка сценария"
        )

    elif text == "Под ключ — 70 000₽":
        context.user_data["tariff"] = "Под ключ"

        msg = (
            "Под ключ\n\n"
            "Полноценная система обработки заявок, прогревает клиента и доводит до готового запроса\n\n"
            "— не участвуете в рутине — нет лишней нагрузки\n"
            "— передача вам тёплых клиентов"
        )

    else:
        return

    # сообщение + оплата
    await update.message.reply_text(
        msg +
        "\n\nГотовы начать?\n\n"
        f"👉 Оплатить: {PAYMENT_LINK}\n\n"
        "После оплаты нажмите «Я оплатил»",
        reply_markup=action_menu
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Клиент выбрал тариф: {context.user_data.get('tariff', '')}"
    )

    # запуск дожима (только 1 раз)
    if not context.chat_data.get("reminders_started"):
        start_reminders(context, update.effective_chat.id)


# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
