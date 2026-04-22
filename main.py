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

# 👉 сюда впиши свой Telegram ID (я ниже объясню как узнать)
ADMIN_ID = 509239406

# этапы диалога
NAME, PHONE, SERVICE, COMMENT = range(4)

keyboard = [
    ["📩 Оставить заявку"],
    ["ℹ️ Услуги"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Добро пожаловать!\n\n"
        "Я помогу оставить заявку на услугу.\n"
        "Нажмите кнопку ниже 👇",
        reply_markup=reply_markup
    )


# начало заявки
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✍️ Как вас зовут?",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME


# имя
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    await update.message.reply_text("📞 Оставьте ваш номер телефона:")
    return PHONE


# телефон
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    await update.message.reply_text("💼 Какая услуга вас интересует?")
    return SERVICE


# услуга
async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text

    await update.message.reply_text("💬 Дополнительные комментарии (или напишите '-'):")
    return COMMENT


# финал
async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["comment"] = update.message.text

    data = context.user_data

    text = (
        "🔥 НОВАЯ ЗАЯВКА\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"💼 Услуга: {data['service']}\n"
        f"💬 Комментарий: {data['comment']}"
    )

    # отправка тебе в Telegram
    await context.bot.send_message(chat_id=ADMIN_ID, text=text)

    # сохранение в файл
    with open("leads.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n\n")

    await update.message.reply_text(
        "✅ Спасибо! Ваша заявка отправлена.\nМы скоро с вами свяжемся 🙌",
        reply_markup=reply_markup
    )

    return ConversationHandler.END


# отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Заявка отменена",
        reply_markup=reply_markup
    )
    return ConversationHandler.END


# обработка кнопок
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📩 Оставить заявку":
        return await start_order(update, context)

    elif text == "ℹ️ Услуги":
        await update.message.reply_text(
            "💼 Мы предлагаем:\n"
            "• Создание Telegram-ботов\n"
            "• Автоматизацию заявок\n"
            "• CRM-решения\n"
        )


app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, text_router)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_service)],
        COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_comment)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)

app.run_polling()
