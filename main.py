import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 509239406

# меню
keyboard = [
    ["🥉 Старт 30k"],
    ["🥈 Рост 40k"],
    ["🥇 Агентство 60k"]
]

menu = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# старт (ПРОДАЮЩИЙ ЭКРАН)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "🚀 Мы настраиваем для бизнеса систему, которая:\n\n"
        "— принимает заявки 24/7\n"
        "— не теряет клиентов\n"
        "— увеличивает продажи без переписок\n\n"
        "👇 Выберите уровень:",
        reply_markup=menu
    )


# главный обработчик
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # 🥉 30K
    if text == "🥉 Старт 30k":
        context.user_data["tariff"] = "30k"
        context.user_data["level"] = "start"

        await update.message.reply_text(
            "🥉 БАЗОВАЯ СИСТЕМА\n\n"
            "✔ заявки в Telegram\n"
            "✔ быстрая настройка\n"
            "✔ простой запуск\n\n"
            "👉 Подходит для старта бизнеса\n\n"
            "Как вас зовут?",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["step"] = "name"
        return

    # 🥈 40K
    if text == "🥈 Рост 40k":
        context.user_data["tariff"] = "40k"
        context.user_data["level"] = "growth"

        await update.message.reply_text(
            "🥈 СИСТЕМА РОСТА\n\n"
            "✔ заявки + автоответ\n"
            "✔ больше конверсии\n"
            "✔ меньше потерь клиентов\n\n"
            "👉 уже система продаж\n\n"
            "Как вас зовут?",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["step"] = "name"
        return

    # 🥇 60K
    if text == "🥇 Агентство 60k":
        context.user_data["tariff"] = "60k"
        context.user_data["level"] = "agency"

        await update.message.reply_text(
            "🥇 СИСТЕМА АГЕНТСТВА\n\n"
            "✔ контроль заявок\n"
            "✔ структура клиентов (CRM-логика)\n"
            "✔ максимальная конверсия\n"
            "✔ масштабирование бизнеса\n\n"
            "👉 это уже полноценная система продаж\n\n"
            "Как вас зовут?",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["step"] = "name"
        return


    # 👤 ИМЯ
    if context.user_data.get("step") == "name":
        context.user_data["name"] = text
        context.user_data["step"] = "business"

        await update.message.reply_text(
            "Чем вы занимаетесь?\n(ваш бизнес / ниша)"
        )
        return


    # 💼 СФЕРА + ПРОДАЖА + ОПЛАТА
    if context.user_data.get("step") == "business":
        context.user_data["business"] = text
        data = context.user_data

        level = data.get("level")

        # 💡 РАЗНЫЙ ДОЖИМ ПО УРОВНЮ
        if level == "start":
            offer = "Базовая система готова к запуску."
        elif level == "growth":
            offer = "Система роста увеличит конверсию заявок."
        else:
            offer = "Агентская система полностью автоматизирует продажи."

        await update.message.reply_text(
            f"🔥 Отлично, я всё понял\n\n"
            f"{offer}\n\n"
            "💳 Для запуска системы:\n"
            "Перевод или оплата по ссылке:\n\n"
            "👉 https://your-payment-link.ru\n\n"
            "После оплаты нажмите кнопку 👇",
            reply_markup=ReplyKeyboardMarkup([["💰 Я оплатил"]], resize_keyboard=True)
        )

        # отправка тебе
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🔥 НОВЫЙ ЛИД\n\n"
                f"Тариф: {data.get('tariff')}\n"
                f"Уровень: {data.get('level')}\n"
                f"Имя: {data.get('name')}\n"
                f"Бизнес: {data.get('business')}"
            )
        )

        context.user_data["step"] = "done"
        return


    # 💰 ОПЛАТИЛ
    if text == "💰 Я оплатил":
        context.user_data["paid"] = True

        await update.message.reply_text(
            "Отлично 👍\n"
            "Оплата получена.\n"
            "Я начинаю настройку вашей системы."
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="💰 ОПЛАТА ПОДТВЕРЖДЕНА"
        )


# запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
