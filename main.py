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
        ["Стандарт — 50 000₽ ⭐ Рекомендуем"],
        ["Под ключ — 70 000₽"]
    ],
    resize_keyboard=True
)

action_menu = ReplyKeyboardMarkup(
    [
        ["Результат", "Задать вопрос"]
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
    context.job_queue.run_once(remind_6h, 21600, chat_id=chat_id)
    context.job_queue.run_once(remind_24h, 86400, chat_id=chat_id)
    context.job_queue.run_once(remind_48h, 172800, chat_id=chat_id)

    context.chat_data["reminders_started"] = True


def stop_reminders(context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["reminders_started"] = False


# ---------------- START (ТВОЁ СООБЩЕНИЕ НЕ ТРОГАЮ) ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()

    await update.message.reply_text(
        "Привет 👋\n"
        "Я помогаю бизнесу не терять клиентов и превращать обращения в продажи.\n\n"
        "Выберите вариант:",
        reply_markup=tariff_menu
    )

    # стартуем с квалификации
    context.user_data["step"] = "business"


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
            "Даже если клиент пишет ночью — система продолжает диалог и доводит до заявки"
        )

    elif tariff == "Под ключ":
        msg = (
            "Результат:\n\n"
            "Полная автоматизация общения — клиенты приходят уже прогретыми"
        )

    else:
        msg = "Сначала выберите тариф."

    await update.message.reply_text(msg)


# ---------------- ОСНОВНАЯ ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    step = context.user_data.get("step")

    # -------- РЕЗУЛЬТАТ --------
    if text == "Результат":
        await send_result(update, context)
        return

    # -------- ВОПРОС --------
    if text == "Задать вопрос":
        context.user_data["step"] = "question"

        await update.message.reply_text(
            "Напишите ваш вопрос — я передам специалисту 👇"
        )
        return

    if step == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Вопрос от клиента:\n\n{update.message.text}"
        )

        await update.message.reply_text("С Вами скоро свяжутся 👍")
        context.user_data["step"] = None
        return

    # -------- ШАГ 1: БИЗНЕС --------
    if step == "business":
        context.user_data["business"] = text
        context.user_data["step"] = "pain"

        await update.message.reply_text(
            "Понял 👍\n\n"
            "Скажите честно:\n"
            "Вы сейчас теряете клиентов из-за того, что не успеваете быстро отвечать?"
        )
        return

    # -------- ШАГ 2: БОЛЬ --------
    if step == "pain":
        context.user_data["step"] = "result_intro"

        await update.message.reply_text(
            "Это самая частая проблема бизнеса 👇\n\n"
            "Пока вы заняты или не отвечаете сразу — клиент уходит к конкурентам.\n\n"
            "Я покажу, как это решается 👇",
            reply_markup=action_menu
        )
        return

    # -------- ПЕРЕХОД К ТАРИФАМ ПОСЛЕ РЕЗУЛЬТАТА --------
    if step == "result_intro":
        context.user_data["step"] = "tariffs"

        await update.message.reply_text(
            "Теперь подберём решение под ваш бизнес 👇",
            reply_markup=tariff_menu
        )
        return

    # -------- ТАРИФЫ --------
    if text in [
        "Базовый — 30 000₽",
        "Стандарт — 50 000₽ ⭐ Рекомендуем",
        "Под ключ — 70 000₽"
    ]:
        if "Базовый" in text:
            context.user_data["tariff"] = "Базовый"
            msg = "Базовый вариант — быстрый приём заявок и фильтрация клиентов"

        elif "Стандарт" in text:
            context.user_data["tariff"] = "Стандарт"
            msg = "Стандарт — оптимальное решение для большинства бизнесов"

        else:
            context.user_data["tariff"] = "Под ключ"
            msg = "Под ключ — полная система автоматизации общения"

        await update.message.reply_text(
            msg +
            f"\n\n👉 Оплатить: {PAYMENT_LINK}\n\n"
            "После оплаты нажмите «Я оплатил» 👍",
            reply_markup=action_menu
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Клиент выбрал тариф: {context.user_data['tariff']}"
        )

        if not context.chat_data.get("reminders_started"):
            start_reminders(context, update.effective_chat.id)

        return

    # -------- ОПЛАТА --------
    if text == "Я оплатил":
        context.user_data["step"] = "paid"
        context.chat_data["paid"] = True

        stop_reminders(context)

        await update.message.reply_text(
            "Принято 👍 Начинаем работу."
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="💰 Клиент сообщил об оплате"
        )
        return


# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
