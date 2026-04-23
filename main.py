import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 509239406


# ---------------- МЕНЮ ----------------
keyboard = [
    ["🥉 Старт 30k"],
    ["🥈 Рост 40k"],
    ["🥇 Агентство 60k"]
]

menu = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ---------------- ДОЖИМ ----------------
async def remind_6h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=(
            "👋 Напомню аккуратно.\n\n"
            "Если актуально — могу запустить систему под ваш бизнес сегодня.\n"
            "Она уже готова к внедрению."
        )
    )


async def remind_24h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=(
            "⏳ Всё ещё актуально?\n\n"
            "Система может уже сейчас начать собирать заявки вместо вас."
        )
    )


async def remind_48h(context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=(
            "📌 Не буду больше отвлекать.\n\n"
            "Если решите — просто напишите «старт», я подключу систему."
        )
    )


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()

    await update.message.reply_text(
        "🚀 Я настраиваю для бизнеса систему, которая превращает обращения клиентов в продажи автоматически.\n\n"
        "— без потерь заявок\n"
        "— без ручной переписки\n"
        "— с ростом конверсии\n\n"
        "👇 Выберите уровень:",
        reply_markup=menu
    )


# ---------------- ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text


    # 🥉 30K
    if text == "🥉 Старт 30k":
        context.user_data["tariff"] = "30k"
        await update.message.reply_text(
            "🥉 БАЗОВАЯ СИСТЕМА\n\n"
            "✔ приём заявок в Telegram\n"
            "✔ простая автоматизация\n\n"
            "Как к вам можно обращаться?",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["step"] = "name"
        return


    # 🥈 40K
    if text == "🥈 Рост 40k":
        context.user_data["tariff"] = "40k"
        await update.message.reply_text(
            "🥈 СИСТЕМА РОСТА\n\n"
            "✔ автоматические ответы\n"
            "✔ рост конверсии\n\n"
            "Как к вам можно обращаться?",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["step"] = "name"
        return


    # 🥇 60K
    if text == "🥇 Агентство 60k":
        context.user_data["tariff"] = "60k"
        await update.message.reply_text(
            "🥇 АГЕНТСКАЯ СИСТЕМА\n\n"
            "✔ управление заявками\n"
            "✔ структура продаж\n"
            "✔ масштабирование бизнеса\n\n"
            "Как к вам можно обращаться?",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["step"] = "name"
        return


    # 👤 ИМЯ
    if context.user_data.get("step") == "name":
        context.user_data["name"] = text
        context.user_data["step"] = "business"

        await update.message.reply_text("Чем вы занимаетесь?")
        return


    # 💼 ФИНАЛ + ОПЛАТА
    if context.user_data.get("step") == "business":
        context.user_data["business"] = text

        data = context.user_data

        await update.message.reply_text(
            "Отлично 👍 я всё понял.\n\n"
            "Я могу внедрить систему под ваш бизнес и запустить её.\n\n"
            "💳 Формат:\n"
            "— оплата по ссылке или переводом\n"
            "— после оплаты начинается настройка\n\n"
            "👉 После оплаты нажмите кнопку ниже",
            reply_markup=ReplyKeyboardMarkup([["💰 Я оплатил"]], resize_keyboard=True)
        )

        # уведомление тебе
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🔥 НОВЫЙ ЛИД\n\n"
                f"Тариф: {data['tariff']}\n"
                f"Имя: {data['name']}\n"
                f"Бизнес: {data['business']}"
            )
        )

        # запуск дожима
        job = context.job_queue
        job.run_once(remind_6h, 21600, chat_id=update.effective_chat.id)
        job.run_once(remind_24h, 86400, chat_id=update.effective_chat.id)
        job.run_once(remind_48h, 172800, chat_id=update.effective_chat.id)

        context.user_data["step"] = "done"
        return


    # 💰 ОПЛАТА
    if text == "💰 Я оплатил":
        context.chat_data["paid"] = True

        await update.message.reply_text(
            "Принял 👍\n\n"
            "Я зафиксировал ваш запрос.\n"
            "Сейчас проверю оплату и начну настройку."
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="💰 КЛИЕНТ НАЖАЛ 'Я ОПЛАТИЛ'"
        )


# ---------------- RUN ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
