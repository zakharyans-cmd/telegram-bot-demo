import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 509239406
NAME, CONTACT = range(2)

keyboard = [
    ["📩 Оставить заявку"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Добро пожаловать!\n\n"
        "🤖 Я бот для бизнеса, который:\n"
        "• принимает заявки 24/7\n"
        "• отвечает клиентам автоматически\n\n"
        "👇 Попробуйте, как это работает:",
        reply_markup=reply_markup
    )


# запуск заявки
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✍️ Как вас зовут?",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME


# имя
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "📞 Напишите ваш телефон или @username в Telegram:"
    )
    return CONTACT


# контакт
async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text

    data = context.user_data

    text = (
        "🔥 НОВАЯ ЗАЯВКА\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Контакт: {data['contact']}"
    )

    # отправка тебе
    await context.bot.send_message(chat_id=ADMIN_ID, text=text)

    # сохранение
    with open("leads.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n\n")

    await update.message.reply_text(
        "✅ Спасибо! Заявка отправлена.",
        reply_markup=reply_markup
    )

    return ConversationHandler.END


# обработка кнопки
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📩 Оставить заявку":
        return await start_order(update, context)


# отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Отменено",
        reply_markup=reply_markup
    )
    return ConversationHandler.END


app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, router)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)

app.run_polling()
