import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "509239406"))

PAYMENT_LINK = "https://your-payment-link.ru"


# ---------------- КНОПКИ (ШАГ 1) ----------------
tariff_menu = ReplyKeyboardMarkup(
    [
        ["Стандарт"],
        ["Базовый"],
        ["Под ключ"]
    ],
    resize_keyboard=True
)

# ---------------- КНОПКИ ПОСЛЕ ВЫБОРА ----------------
action_menu = ReplyKeyboardMarkup(
    [
        ["Результат", "Задать вопрос", "Оплатить"]
    ],
    resize_keyboard=True
)

# ---------------- КНОПКИ ОПЛАТЫ (ШАГ 2) ----------------
pay_menu = ReplyKeyboardMarkup(
    [
        ["Стандарт — 50 000₽ ⭐ Рекомендуем"],
        ["Базовый — 30 000₽"],
        ["Под ключ — 70 000₽"],
        ["Назад"]
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
        text="Можно спокойно вернуться к этому позже — я на связи 👍"
    )


async def remind_48h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Закрою диалог, но если понадобится — просто напишите 👍"
    )


def start_reminders(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    stop_reminders(context)

    context.chat_data["jobs"] = []

    context.chat_data["jobs"].append(
        context.job_queue.run_once(remind_6h, 21600, chat_id=chat_id)
    )
    context.chat_data["jobs"].append(
        context.job_queue.run_once(remind_24h, 86400, chat_id=chat_id)
    )
    context.chat_data["jobs"].append(
        context.job_queue.run_once(remind_48h, 172800, chat_id=chat_id)
    )

    context.chat_data["reminders_started"] = True


def stop_reminders(context: ContextTypes.DEFAULT_TYPE):
    for job in context.chat_data.get("jobs", []):
        try:
            job.schedule_removal()
        except:
            pass

    context.chat_data["jobs"] = []
    context.chat_data["reminders_started"] = False


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    stop_reminders(context)
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
        msg = "Результат:\n\nСистема фиксирует каждое сообщение 24/7 и ни один клиент не потеряется"

    elif tariff == "Стандарт":
        msg = "Результат:\n\nИнтерес клиента не падает, даже если он написал ночью — система продолжает диалог"

    elif tariff == "Под ключ":
        msg = "Результат:\n\nОбщение с клиентами выстроено и контролируется — приходят уже тёплые заявки"

    else:
        msg = "Сначала выберите вариант."

    await update.message.reply_text(msg)


# ---------------- ОПЛАТА ----------------
async def send_payment(update: Update):
    await update.message.reply_text(
        "Выберите тариф для оплаты:",
        reply_markup=pay_menu
    )


# ---------------- ОСНОВНАЯ ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text

    # результат
    if text == "Результат":
        await send_result(update, context)
        return

    # вопрос
    if text == "Задать вопрос":
        context.user_data["step"] = "question"
        await update.message.reply_text("Напишите ваш вопрос — я передам его специалисту 👇")
        return

    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Вопрос от клиента:\n\n{update.message.text}"
        )
        await update.message.reply_text("С Вами скоро свяжутся 👍")
        context.user_data["step"] = None
        return

    # оплата меню
    if text == "Оплатить":
        await send_payment(update)
        return

    # выбор тарифа (ШАГ 1)
    if text == "Базовый":
        context.user_data["tariff"] = "Базовый"
        msg = (
            "Базовый вариант\n\n"
            "Подходит для простого приема обращений и записи на услугу\n\n"
            "— быстрые ответы\n"
            "— отсев случайных обращений\n\n"
            "Готовы начать?"
        )

    elif text == "Стандарт":
        context.user_data["tariff"] = "Стандарт"
        msg = (
            "Стандарт ⭐\n\n"
            "Оптимальное решение для большинства бизнесов\n"
            "Система помогает быстро отвечать и удерживать клиента\n\n"
            "— настройка логики под ваш бизнес\n"
            "— настройка сценария\n\n"
            "Готовы начать?"
        )

    elif text == "Под ключ":
        context.user_data["tariff"] = "Под ключ"
        msg = (
            "Под ключ\n\n"
            "Полноценная система обработки заявок: прогревает клиента и доводит до готового запроса\n\n"
            "— не тратите время на одни и те же вопросы\n"
            "— получаете тёплые заявки\n\n"
            "Готовы начать?"
        )

    # кнопка оплаты (ШАГ 2)
    elif text in [
        "Стандарт — 50 000₽ ⭐ Рекомендуем",
        "Базовый — 30 000₽",
        "Под ключ — 70 000₽"
    ]:

        links = {
            "Стандарт — 50 000₽ ⭐ Рекомендуем": PAYMENT_LINK,
            "Базовый — 30 000₽": PAYMENT_LINK,
            "Под ключ — 70 000₽": PAYMENT_LINK
        }

        await update.message.reply_text(
            f"Оплата:\n👉 {links[text]}\n\nПосле оплаты нажмите «Оплатил» 👍"
        )

        context.chat_data["paid"] = True
        start_reminders(context, update.effective_chat.id)
        return

    else:
        return

    await update.message.reply_text(msg, reply_markup=action_menu)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Клиент выбрал тариф: {context.user_data.get('tariff', '')}"
    )


# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
