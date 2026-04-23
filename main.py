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

ADMIN_ID = 509239406  # твой Telegram ID

NAME, CONTACT = range(2)

# КНОПКИ ГЛАВНОГО ЭКРАНА
keyboard = [
    ["🥉 Простые заявки"],
    ["🥈 Больше заявок"],
    ["🥇 Максимум клиентов"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# СТАРТ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я помогу вам настроить систему, которая автоматически принимает заявки клиентов в Telegram.\n\n"
        "Без переписок вручную и без потери клиентов.\n\n"
        "👇 Выберите вариант:",
        reply_markup=reply_markup
    )


# ВЫБОР ТАРИФА
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    context.user_data["tariff"] = text

    if text in ["🥉 Простые заявки", "🥈 Больше заявок", "🥇 Максимум клиентов"]:
        await update.message.reply_text(
            "Отлично 👍\n\nСейчас задам 3 коротких вопроса и настрою систему под ваш бизнес.",
            reply_markup=ReplyKeyboardRemove()
        )
        await update.message.reply_text("Как вас зовут или как называется бизнес?")
        return NAME

    return ConversationHandler.END


# ИМЯ
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Чем вы занимаетесь?")
    return CONTACT


# КОНТАКТ
async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text

    data = context.user_data

    text = (
        "🔥 НОВАЯ ЗАЯВКА\n\n"
        f"📌 Тариф: {data['tariff']}\n"
        f"👤 Имя: {data['name']}\n"
        f"💼 Сфера: {data['contact']}"
    )

    # отправка тебе
    await context.bot.send_message(chat_id=ADMIN_ID, text=text)

    # сохранение
    with open("leads.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n\n")

    await update.message.reply_text(
        "Спасибо 👍 Я всё получил и скоро с вами свяжусь.",
        reply_markup=reply_markup
    )

    return ConversationHandler.END


# ОТМЕНА
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отменено",
        reply_markup=reply_markup
    )
    return ConversationHandler.END


# ЗАПУСК
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
