import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# кнопки
keyboard = [
    ["📩 Оставить заявку"],
    ["ℹ️ Услуги"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Добро пожаловать!\n\n"
        "🤖 Я бот для бизнеса, который:\n"
        "• принимает заявки 24/7\n"
        "• отвечает клиентам автоматически\n"
        "• упрощает запись на услуги\n\n"
        "👇 Попробуйте, как это работает:",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши /start")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))

app.run_polling()
