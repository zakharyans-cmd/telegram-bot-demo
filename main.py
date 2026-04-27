import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "509239406"))


# ---------------- ОПЛАТЫ ----------------
PAY_LINKS = {
    "Базовый — 30 000₽": "https://your-payment-link.ru/basic",
    "Стандарт — 50 000₽ ⭐ Рекомендуем": "https://your-payment-link.ru/standard",
    "Под ключ — 70 000₽": "https://your-payment-link.ru/full"
}


# ---------------- КНОПКИ 1 (ВХОД) ----------------
tariff_menu = ReplyKeyboardMarkup(
    [
        ["Стандарт ⭐ Рекомендуем"],
        ["Базовый"],
        ["Под ключ"]
    ],
    resize_keyboard=True
)

# ---------------- КНОПКИ 2 (ПОСЛЕ ВЫБОРА) ----------------
action_menu = ReplyKeyboardMarkup(
    [
        ["Результат", "Задать вопрос", "Оплатить"]
    ],
    resize_keyboard=True
)

# ---------------- КНОПКИ 3 (ОПЛАТА) ----------------
pay_menu = ReplyKeyboardMarkup(
    [
        ["Стандарт — 50 000₽ ⭐ Рекомендуем"],
        ["Базовый — 30 000₽"],
        ["Под ключ — 70 000₽"]
    ],
    resize_keyboard=True
)


# ---------------- РЕЗУЛЬТАТ ----------------
async def send_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tariff = context.user_data.get("tariff")

    if tariff == "Базовый":
        msg = "Результат:\n\nСистема фиксирует обращения 24/7 и не теряет клиентов"

    elif tariff == "Стандарт":
        msg = "Результат:\n\nСистема удерживает клиента и доводит до контакта даже при задержке ответа"

    elif tariff == "Под ключ":
        msg = "Результат:\n\nВы получаете уже тёплые заявки, готовые к покупке"

    else:
        msg = "Сначала выберите тариф."

    await update.message.reply_text(msg)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "Привет 👋\n"
        "Я помогаю бизнесу превращать обращения в продажи.\n\n"
        "Выберите вариант:",
        reply_markup=tariff_menu
    )


# ---------------- ОСНОВНАЯ ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # результат
    if text == "Результат":
        await send_result(update, context)
        return

    # вопрос
    if text == "Задать вопрос":
        context.user_data["step"] = "question"
        await update.message.reply_text("Напишите ваш вопрос 👇")
        return

    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Вопрос:\n\n{update.message.text}"
        )
        await update.message.reply_text("С вами скоро свяжутся 👍")
        context.user_data["step"] = None
        return

    # ОПЛАТА → показываем тарифы с ценами
    if text == "Оплатить":
        await update.message.reply_text(
            "Выберите тариф для оплаты:",
            reply_markup=pay_menu
        )
        return

    # ---------------- ТАРИФЫ (ШАГ 1) ----------------
    if text in ["Базовый", "Стандарт ⭐ Рекомендуем", "Под ключ"]:

        mapping = {
            "Базовый": "Базовый",
            "Стандарт ⭐ Рекомендуем": "Стандарт",
            "Под ключ": "Под ключ"
        }

        context.user_data["tariff"] = mapping[text]

        msg = {
            "Базовый": (
                "Базовый вариант\n\n"
                "Простой приём заявок и обработка обращений\n\n"
                "— быстрые ответы\n"
                "— отсев случайных клиентов\n\n"
                "Готовы начать?"
            ),
            "Стандарт": (
                "Стандарт ⭐\n\n"
                "Оптимальное решение для большинства бизнесов\n\n"
                "— удержание клиента\n"
                "— настройка сценариев\n\n"
                "Готовы начать?"
            ),
            "Под ключ": (
                "Под ключ\n\n"
                "Полная система обработки заявок под ключ\n\n"
                "— тёплые лиды\n"
                "— автоматизация общения\n\n"
                "Готовы начать?"
            )
        }[mapping[text]]

        await update.message.reply_text(msg, reply_markup=action_menu)
        return

    # ---------------- ТАРИФЫ (ШАГ 2 ОПЛАТА) ----------------
    if text in PAY_LINKS:
        link = PAY_LINKS[text]

        await update.message.reply_text(
            f"Оплата тарифа:\n👉 {link}\n\nПосле оплаты нажмите «Я оплатил» 👍"
        )
        return


# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
