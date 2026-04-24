import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 509239406

# 👉 ВСТАВЬ ССЫЛКУ ОПЛАТЫ (ЮKASSA)
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
            "Такие системы обычно окупаются за счёт того, что перестают теряться заявки.\n\n"
            "Если задача ещё актуальна — можно запустить."
        )
    )


async def remind_24h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=(
            "⏳ Частая ситуация:\n"
            "клиент написал → ему не ответили вовремя → он ушёл.\n\n"
            "Бот как раз закрывает этот момент.\n\n"
            "Если хотите — подключу под вас."
        )
    )


async def remind_48h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=(
            "📌 Закрываю диалог, чтобы не отвлекать.\n\n"
            "Если вернётесь — просто напишите «старт»."
        )
    )


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()

    await update.message.reply_text(
        "Я настраиваю чат-ботов, которые берут переписку с клиентами на себя.\n\n"
        "Отвечают сразу и доводят до заявки.\n\n"
        "Выберите формат:",
        reply_markup=menu
    )


# ---------------- ОСНОВНАЯ ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text


    # ВЫБОР ТАРИФА
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


    # ДИАГНОСТИКА
    if context.user_data.get("step") == "flow":
        context.user_data["flow"] = text
        business = context.user_data.get("business", "")

        await update.message.reply_text(
            f"Понял.\n\n"
            f"В «{business}» обычно ключевая проблема — скорость ответа.\n\n"
            "Если клиент не получает ответ быстро — он уходит."
        )

        await update.message.reply_text(
            "Что делаю я:\n\n"
            "— бот отвечает сразу\n"
            "— задаёт нужные вопросы\n"
            "— доводит до заявки\n\n"
            "Вы просто получаете уже тёплых клиентов."
        )

        # КЕЙС
        await update.message.reply_text(
            "Короткий пример:\n\n"
            "в похожей нише после внедрения перестали теряться заявки "
            "и загрузка выросла без увеличения рекламы."
        )

        # КАК ПРОХОДИТ
        await update.message.reply_text(
            "Как проходит запуск:\n\n"
            "— собираю логику под ваш бизнес\n"
            "— настраиваю сценарий\n"
            "— подключаю и тестирую\n\n"
            "Обычно 1–2 дня."
        )

        # ВЫБОР ДЕЙСТВИЯ
        await update.message.reply_text(
            f"👉 Можно сразу запустить:\n{PAYMENT_LINK}\n\n"
            "Или задать вопрос перед оплатой:",
            reply_markup=ReplyKeyboardMarkup(
                [["💰 Оплатить", "❓ Задать вопрос"]],
                resize_keyboard=True
            )
        )

        # УВЕДОМЛЕНИЕ
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🔥 ЛИД\n\n"
                f"Тариф: {context.user_data['tariff']}\n"
                f"Ниша: {context.user_data['business']}\n"
                f"Процесс: {context.user_data['flow']}"
            )
        )

        # ДОЖИМ
        job = context.job_queue
        job.run_once(remind_6h, 21600, chat_id=update.effective_chat.id)
        job.run_once(remind_24h, 86400, chat_id=update.effective_chat.id)
        job.run_once(remind_48h, 172800, chat_id=update.effective_chat.id)

        context.user_data["step"] = "decision"
        return


    # ВОПРОС
    if text == "❓ Задать вопрос":
        context.user_data["step"] = "question"

        await update.message.reply_text(
            "Напишите вопрос, отвечу лично."
        )
        return


    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"❓ ВОПРОС ОТ ЛИДА:\n\n{text}"
        )

        await update.message.reply_text(
            "Ответил вам в ближайшее время 👍"
        )
        return


    # ОПЛАТА
    if text == "💰 Оплатить":
        await update.message.reply_text(
            f"Вот ссылка для оплаты:\n{PAYMENT_LINK}\n\n"
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
            "Принял.\n\n"
            "Проверяю оплату и начинаю работу."
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="💰 ОПЛАТА — ПРОВЕРЬ"
        )


# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
