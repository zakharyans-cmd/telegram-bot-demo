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


# ---------------- КНОПКИ ----------------
tariff_menu = ReplyKeyboardMarkup(
    [
        ["Стандарт ⭐ Рекомендуем"],
        ["Базовый"],
        ["Под ключ"]
    ],
    resize_keyboard=True
)

action_menu = ReplyKeyboardMarkup(
    [
        ["Результат", "Задать вопрос", "Оплатить"]
    ],
    resize_keyboard=True
)

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
        msg = (
            "Результат:\n\n"
            "Ни одно обращение не теряется — каждый клиент получает ответ и фиксируется в системе"
        )

    elif tariff == "Стандарт":
        msg = (
            "Результат:\n\n"
            "Клиенты не “остывают” — система удерживает их внимание и доводит до контакта"
        )

    elif tariff == "Под ключ":
        msg = (
            "Результат:\n\n"
            "К вам приходят уже подготовленные клиенты, с которыми проще и быстрее закрывать сделки"
        )

    else:
        msg = "Сначала выберите тариф."

    await update.message.reply_text(msg)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "Привет 👋\n\n"
        "Большинство бизнесов теряют часть клиентов ещё на этапе переписки — даже не замечая этого.\n\n"
        "Кто-то не дождался ответа, кто-то передумал, а кто-то просто “пропал”.\n\n"
        "В итоге — вы теряете деньги\n"
        "Я помогаю это исправить\n\n"
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
        await update.message.reply_text(
            "Напишите ваш вопрос — я передам его специалисту 👇"
        )
        return

    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Вопрос:\n\n{update.message.text}"
        )
        await update.message.reply_text("С вами скоро свяжутся 👍")
        context.user_data["step"] = None
        return

    # ОПЛАТА
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
                "Подходит, если сейчас важно просто не терять входящие обращения\n\n"
                "— быстрые ответы клиентам\n"
                "— фиксация всех заявок\n"
                "— отсев случайных обращений\n\n"
                "Вы перестаёте терять тех, кто уже написал.\n\n"
                "Готовы начать?"
            ),
            "Стандарт": (
                "Стандарт ⭐\n\n"
                "Оптимальное решение для большинства бизнесов\n\n"
                "Клиент не просто получает ответ — система удерживает его внимание и ведёт диалог дальше\n\n"
                "— логика общения под ваш бизнес\n"
                "— сценарии переписки\n"
                "— удержание интереса клиента\n\n"
                "В итоге — больше людей доходят до контакта и сделки.\n\n"
                "Готовы начать?"
            ),
            "Под ключ": (
                "Под ключ\n\n"
                "Полноценная система обработки заявок\n\n"
                "Клиент проходит путь от первого сообщения до готовности к диалогу\n\n"
                "— автоматизация общения\n"
                "— прогрев клиента\n"
                "— формирование “тёплых” заявок\n\n"
                "Вы получаете не просто обращения, а подготовленных клиентов.\n\n"
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
