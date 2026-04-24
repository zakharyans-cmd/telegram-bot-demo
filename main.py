import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 509239406

PAYMENT_LINK = "https://your-payment-link.ru"


# ---------------- КНОПКИ ----------------
tariff_menu = ReplyKeyboardMarkup(
    [
        ["Стандарт — 50 000₽ ⭐ Рекомендуем"],
        ["Базовый — 30 000₽"],
        ["Под ключ — 70 000₽"]
    ],
    resize_keyboard=True
)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()

    text = (update.message.text or "").lower()

    if any(x in text for x in ["цена", "стоимость", "сколько"]):
        intro = "Привет 👋\nПодберу подходящий вариант под вашу задачу и покажу стоимость.\n\n"
    elif any(x in text for x in ["как", "что", "расскажи", "интересно"]):
        intro = "Привет 👋\nКоротко объясню, как это работает и чем может быть полезно.\n\n"
    else:
        intro = "Привет 👋\nЯ помогаю бизнесу не терять клиентов и превращать обращения в продажи.\n\n"

    await update.message.reply_text(
        intro + "Выберите вариант:",
        reply_markup=tariff_menu
    )


# ---------------- ОСНОВНАЯ ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ---------------- ПРИМЕР ----------------
    if text == "Пример":

        tariff = context.user_data.get("tariff")

        if tariff == "Базовый":
            msg = (
                "📌 Базовый пример:\n\n"
                "Когда у бизнеса нет постоянного администратора, "
                "сообщения от клиентов могут приходить в разное время, "
                "и не всегда получается ответить сразу.\n\n"
                "Система помогает не терять такие обращения и фиксирует интерес клиента."
            )

        elif tariff == "Стандарт":
            msg = (
                "📌 Стандарт пример:\n\n"
                "Клиенты часто пишут и не дожидаются ответа, если он задерживается.\n\n"
                "Система сразу реагирует, уточняет запрос и помогает довести человека до следующего шага."
            )

        elif tariff == "Под ключ":
            msg = (
                "📌 Под ключ пример:\n\n"
                "В загруженных бизнесах менеджеры не успевают обрабатывать все обращения.\n\n"
                "Система берёт первичный диалог на себя и передаёт уже тёплого клиента."
            )

        else:
            msg = "Сначала выберите тариф."

        await update.message.reply_text(msg)
        return

    # ---------------- ВОПРОС ----------------
    if text == "Задать вопрос":
        context.user_data["step"] = "question"

        await update.message.reply_text(
            "С Вами скоро свяжутся 👍"
        )
        return

    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Вопрос клиента:\n\n{text}"
        )

        await update.message.reply_text(
            "С Вами скоро свяжутся 👍"
        )
        return

    # ---------------- ОПЛАТА ----------------
    if text == "Я оплатил":
        context.chat_data["paid"] = True

        await update.message.reply_text(
            "Принято. Начинаем работу 👍"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="Оплата получена"
        )
        return

    # ---------------- ТАРИФЫ ----------------
    if text == "Стандарт — 50 000₽ ⭐ Рекомендуем":
        context.user_data["tariff"] = "Стандарт"
        context.user_data["price"] = "50k"

        message = (
            "Стандарт ⭐\n\n"
            "Оптимальное решение для большинства бизнесов.\n\n"
            "Система:\n"
            "— быстрые ответы\n"
            "— уточнение запроса\n"
            "— отсев случайных обращений"
        )

    elif text == "Базовый — 30 000₽":
        context.user_data["tariff"] = "Базовый"
        context.user_data["price"] = "30k"

        message = (
            "Базовый вариант.\n\n"
            "Подходит для простого приёма обращений без сложной логики."
        )

    elif text == "Под ключ — 70 000₽":
        context.user_data["tariff"] = "Под ключ"
        context.user_data["price"] = "70k"

        message = (
            "Под ключ.\n\n"
            "Полная система обработки обращений с первичной квалификацией клиента."
        )

    else:
        return

    # ---------------- ОФФЕР ----------------
    await update.message.reply_text(
        message + "\n\n"
        f"Стоимость: {context.user_data['price']}\n\n"
        f"Оплата:\n{PAYMENT_LINK}",
        reply_markup=ReplyKeyboardMarkup(
            [["Я оплатил", "Пример", "Задать вопрос"]],
            resize_keyboard=True
        )
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"Тариф: {context.user_data['tariff']}\n"
            f"Стоимость: {context.user_data['price']}"
        )
    )


# ---------------- RUN ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
