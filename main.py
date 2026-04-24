import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 509239406

PAYMENT_LINK = "https://your-payment-link.ru"


# ---------------- КНОПКИ ----------------
tariff_menu = ReplyKeyboardMarkup(
    [
        ["Базовый — 30 000₽"],
        ["Стандарт — 40 000₽"],
        ["Под ключ — 60 000₽"]
    ],
    resize_keyboard=True
)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()

    await update.message.reply_text(
        "Помогаю бизнесу не терять заявки и превращать обращения в клиентов.\n\n"
        "Выберите вариант:",
        reply_markup=tariff_menu
    )


# ---------------- ТАРИФЫ ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ---------------- БАЗОВЫЙ ----------------
    if text == "Базовый — 30 000₽":
        context.user_data["tariff"] = "Базовый"
        context.user_data["price"] = "30k"

        message = (
            "Базовый вариант.\n\n"
            "Подходит, если сейчас главное — не терять заявки.\n"
            "Бот берёт первичные обращения и быстро отвечает клиентам,\n"
            "чтобы они не уходили, пока вы заняты."
        )

    # ---------------- СТАНДАРТ ----------------
    elif text == "Стандарт — 40 000₽":
        context.user_data["tariff"] = "Стандарт"
        context.user_data["price"] = "40k"

        message = (
            "Стандарт.\n\n"
            "Это уже про контроль качества заявок.\n\n"
            "Бот:\n"
            "— быстро отвечает\n"
            "— отсеивает случайные обращения\n"
            "— оставляет только заинтересованных клиентов\n\n"
            "Меньше мусора → больше нормальных диалогов."
        )

    # ---------------- ПОД КЛЮЧ ----------------
    elif text == "Под ключ — 60 000₽":
        context.user_data["tariff"] = "Под ключ"
        context.user_data["price"] = "60k"

        message = (
            "Под ключ.\n\n"
            "Это полноценная система обработки заявок.\n\n"
            "Она не просто отвечает — она прогревает клиента и доводит его до готового запроса.\n"
            "Фактически — первый уровень продаж автоматизирован."
        )

    else:
        return

    # ---------------- ОФФЕР (ПРЕМИУМ-СТИЛЬ) ----------------
    await update.message.reply_text(
        message + "\n\n"
        f"Стоимость: {context.user_data['price']}\n\n"
        f"Подключение по ссылке:\n{PAYMENT_LINK}\n\n"
        "Если есть вопросы — можно задать, с вами свяжется менеджер.",
        reply_markup=ReplyKeyboardMarkup(
            [["Я оплатил", "Задать вопрос"]],
            resize_keyboard=True
        )
    )

    # ---------------- АДМИН ----------------
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "Заявка\n\n"
            f"Тариф: {context.user_data['tariff']}\n"
            f"Цена: {context.user_data['price']}"
        )
    )


# ---------------- ВОПРОСЫ ----------------
async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # 💰 ОПЛАТА
    if text == "Я оплатил":
        context.chat_data["paid"] = True

        await update.message.reply_text(
            "Принято 👍 начинаем работу."
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="Оплата получена — проверить"
        )

    # ❓ ВОПРОС
    elif text == "Задать вопрос":
        context.user_data["step"] = "question"

        await update.message.reply_text(
            "Конечно 👍\n"
            "С вами свяжется менеджер и ответит в Telegram."
        )

    # 💬 ОТВЕТ НА ВОПРОС
    elif context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Вопрос клиента:\n\n{text}"
        )

        await update.message.reply_text(
            "Спасибо 👍\n"
            "С вами свяжется менеджер и поможет разобраться."
        )


# ---------------- RUN ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, payment))

app.run_polling()
