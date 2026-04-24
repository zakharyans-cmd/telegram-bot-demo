import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 509239406

PAYMENT_LINK = "https://your-payment-link.ru"


# ---------------- МЕНЮ ----------------
menu = ReplyKeyboardMarkup(
    [
        ["🥉 Старт", "🥈 Рост"],
        ["🥇 Под ключ"]
    ],
    resize_keyboard=True
)


# ---------------- ДОЖИМ ----------------
async def remind_6h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=(
            "👋 Напомню.\n\n"
            "Большинство заявок теряются просто потому, что бизнес не отвечает быстро.\n"
            "Бот решает это автоматически.\n\n"
            "Если актуально — можем подключить."
        )
    )


async def remind_24h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=(
            "⏳ Факт из практики:\n\n"
            "до 70% клиентов уходят к конкурентам, если им не ответили в первые минуты.\n\n"
            "Бот закрывает эту проблему.\n\n"
            "Если интересно — продолжим."
        )
    )


async def remind_48h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=(
            "📌 Закрываю диалог.\n\n"
            "Если задача по заявкам снова станет актуальной — просто напишите «старт»."
        )
    )


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()

    await update.message.reply_text(
        "Я настраиваю чат-ботов, которые берут переписку с клиентами на себя.\n\n"
        "Проблема большинства бизнесов — заявки теряются из-за медленного ответа.\n\n"
        "Выберите формат:",
        reply_markup=menu
    )


# ---------------- ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ТАРИФ
    if text in ["🥉 Старт", "🥈 Рост", "🥇 Под ключ"]:
        context.user_data["tariff"] = text
        context.user_data["step"] = "business"

        await update.message.reply_text(
            "Чем вы занимаетесь?",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # НИША
    if context.user_data.get("step") == "business":
        context.user_data["business"] = text
        context.user_data["step"] = "flow"

        await update.message.reply_text(
            "Как сейчас обрабатываете заявки?\n\n"
            "1 — вручную\n"
            "2 — есть CRM/бот"
        )
        return

    # ДИАГНОСТИКА + БОЛЬ + ПРОДАЖА
    if context.user_data.get("step") == "flow":
        context.user_data["flow"] = text
        business = context.user_data.get("business", "")

        await update.message.reply_text(
            f"Понял.\n\n"
            f"В нише «{business}» обычно главная проблема — скорость ответа.\n\n"
            "Если клиент не получает ответ в первые минуты — он уходит к конкуренту."
        )

        await update.message.reply_text(
            "📉 Из-за этого бизнесы теряют до 30–70% заявок без даже увеличения рекламы.\n\n"
            "Бот решает это так:"
            "\n— отвечает сразу"
            "\n— задаёт вопросы"
            "\n— доводит до заявки"
        )

        # КЕЙС С ЦИФРАМИ
        await update.message.reply_text(
            "📊 Пример:\n\n"
            "В похожем проекте после внедрения:\n"
            "— потеря заявок снизилась на ~40%\n"
            "— конверсия выросла на ~25%\n"
            "— обработка стала 24/7 без менеджера"
        )

        # КАК ПРОХОДИТ
        await update.message.reply_text(
            "Как проходит запуск:\n\n"
            "— собираю логику под ваш бизнес\n"
            "— настраиваю сценарий\n"
            "— подключаю и тестирую\n\n"
            "Обычно 1–2 дня."
        )

        # ОФФЕР
        await update.message.reply_text(
            f"👉 Можно запустить здесь:\n{PAYMENT_LINK}\n\n"
            "Или задать вопрос перед оплатой:",
            reply_markup=ReplyKeyboardMarkup(
                [["💰 Оплатить", "❓ Задать вопрос"]],
                resize_keyboard=True
            )
        )

        # АДМИН
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🔥 ЛИД\n\n"
                f"Тариф: {context.user_data['tariff']}\n"
                f"Ниша: {context.user_data['business']}\n"
                f"Процесс: {context.user_data['flow']}"
            )
        )

        # ДОЖИМ (защита от дублей)
        if not context.chat_data.get("reminders_set"):
            context.job_queue.run_once(remind_6h, 21600, chat_id=update.effective_chat.id)
            context.job_queue.run_once(remind_24h, 86400, chat_id=update.effective_chat.id)
            context.job_queue.run_once(remind_48h, 172800, chat_id=update.effective_chat.id)

            context.chat_data["reminders_set"] = True

        context.user_data["step"] = "decision"
        return

    # ВОПРОС
    if text == "❓ Задать вопрос":
        context.user_data["step"] = "question"

        await update.message.reply_text("Напишите вопрос, отвечу лично.")
        return

    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"❓ ВОПРОС:\n\n{text}"
        )

        await update.message.reply_text("Ответил вам в ближайшее время 👍")
        return

    # ОПЛАТА
    if text == "💰 Оплатить":
        await update.message.reply_text(
            f"Ссылка для оплаты:\n{PAYMENT_LINK}\n\n"
            "После оплаты нажмите «Я оплатил»",
            reply_markup=ReplyKeyboardMarkup(
                [["💰 Я оплатил"]],
                resize_keyboard=True
            )
        )
        return

    if text == "💰 Я оплатил":
        context.chat_data["paid"] = True

        await update.message.reply_text(
            "Принял заявку.\n\n"
            "Проверяю оплату и начинаю работу."
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="💰 ОПЛАТА — ПРОВЕРИТЬ"
        )


# ---------------- RUN ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
