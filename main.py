import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 509239406

# меню
keyboard = [
    ["🥉 30k - заявки"],
    ["🥈 40k - рост заявок"],
    ["🥇 60k - система бизнеса"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 VERSION 2026 TEST ACTIVE"
        "Выберите, какую систему хотите:"
        "\n\n👇",
        reply_markup=reply_markup
    )


# обработка ВСЕХ сообщений
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # 🥉 30K
    if text == "🥉 30k - заявки":
        context.user_data["tariff"] = "30k"

        await update.message.reply_text(
            "🥉 ПРОСТАЯ СИСТЕМА\n\n"
            "✔ заявки в Telegram\n"
            "✔ простая настройка\n\n"
            "Напишите ваше имя:",
            reply_markup=ReplyKeyboardRemove()
        )

        context.user_data["step"] = "30_name"
        return

    # 🥈 40K
    if text == "🥈 40k - рост заявок":
        context.user_data["tariff"] = "40k"

        await update.message.reply_text(
            "🥈 СИСТЕМА РОСТА\n\n"
            "✔ заявки + автоответ\n"
            "✔ больше конверсии\n\n"
            "Напишите ваше имя:",
            reply_markup=ReplyKeyboardRemove()
        )

        context.user_data["step"] = "40_name"
        return

    # 🥇 60K
    if text == "🥇 60k - система бизнеса":
        context.user_data["tariff"] = "60k"

        await update.message.reply_text(
            "🥇 ПОЛНАЯ СИСТЕМА\n\n"
            "✔ контроль заявок\n"
            "✔ мини CRM\n"
            "✔ максимальная конверсия\n\n"
            "Напишите ваше имя:",
            reply_markup=ReplyKeyboardRemove()
        )

        context.user_data["step"] = "60_name"
        return


    # 🔁 СБОР ИМЕНИ
    if context.user_data.get("step") in ["30_name", "40_name", "60_name"]:
        context.user_data["name"] = text

        await update.message.reply_text("Чем вы занимаетесь?")
        context.user_data["step"] += "_contact"
        return


    # 🔁 СФЕРА + ФИНАЛ
    if context.user_data.get("step") in ["30_name_contact", "40_name_contact", "60_name_contact"]:
        context.user_data["contact"] = text

        data = context.user_data

        msg = (
            "🔥 НОВАЯ ЗАЯВКА\n\n"
            f"📌 Тариф: {data.get('tariff')}\n"
            f"👤 Имя: {data.get('name')}\n"
            f"💼 Сфера: {data.get('contact')}"
        )

        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

        await update.message.reply_text(
            "Спасибо 👍 Заявка отправлена.",
            reply_markup=reply_markup
        )

        context.user_data.clear()
        return


# запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
