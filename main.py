import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ---------------- ЛОГИ ----------------
logging.basicConfig(level=logging.INFO)

# ---------------- ENV ----------------
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "509239406"))

if not TOKEN:
    raise ValueError("BOT_TOKEN не задан")

# ---------------- ДАННЫЕ ----------------
TARIFFS = {
    "Базовый": {
        "pay_text": "Базовый — 30 000₽",
        "link": "https://your-payment-link.ru/basic",
        "desc": (
            "Базовый вариант\n\n"
            "Подходит, если сейчас важно просто не терять входящие обращения\n\n"
            "— быстрые ответы клиентам\n"
            "— фиксация всех заявок\n"
            "— отсев случайных обращений\n\n"
            "Вы перестаёте терять тех, кто уже написал.\n\n"
            "Готовы начать?"
        ),
        "result": (
            "Результат:\n\n"
            "Ни одно обращение не теряется — каждый клиент получает ответ и фиксируется в системе"
        )
    },
    "Стандарт": {
        "pay_text": "Стандарт — 50 000₽ ⭐ Рекомендуем",
        "link": "https://your-payment-link.ru/standard",
        "desc": (
            "Стандарт ⭐\n\n"
            "Оптимальное решение для большинства бизнесов\n\n"
            "Клиент не просто получает ответ — система удерживает его внимание и ведёт диалог дальше\n\n"
            "— логика общения под ваш бизнес\n"
            "— сценарии переписки\n"
            "— удержание интереса клиента\n\n"
            "В итоге — больше людей доходят до контакта и сделки.\n\n"
            "Готовы начать?"
        ),
        "result": (
            "Результат:\n\n"
            "Клиенты не “остывают” — система удерживает их внимание и доводит до контакта"
        )
    },
    "Под ключ": {
        "pay_text": "Под ключ — 70 000₽",
        "link": "https://your-payment-link.ru/full",
        "desc": (
            "Под ключ\n\n"
            "Полноценная система обработки заявок\n\n"
            "Клиент проходит путь от первого сообщения до готовности к диалогу\n\n"
            "— автоматизация общения\n"
            "— прогрев клиента\n"
            "— формирование “тёплых” заявок\n\n"
            "Вы получаете не просто обращения, а подготовленных клиентов.\n\n"
            "Готовы начать?"
        ),
        "result": (
            "Результат:\n\n"
            "К вам приходят уже подготовленные клиенты, с которыми проще и быстрее закрывать сделки"
        )
    }
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
        ["Результат", "Задать вопрос"],
        ["Оплатить"]
    ],
    resize_keyboard=True
)

pay_menu = ReplyKeyboardMarkup(
    [
        ["Стандарт — 50 000₽ ⭐ Рекомендуем"],
        ["Базовый — 30 000₽"],
        ["Под ключ — 70 000₽"],
        ["Я оплатил"]
    ],
    resize_keyboard=True
)

# ---------------- РЕЗУЛЬТАТ ----------------
async def send_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tariff = context.user_data.get("tariff")

    if not tariff:
        await update.message.reply_text("Сначала выберите тариф.")
        return

    await update.message.reply_text(TARIFFS[tariff]["result"])

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
    user = update.effective_user

    # ---------------- Я ОПЛАТИЛ ----------------
    if text == "Я оплатил":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Пользователь оплатил\n\nID: {user.id}\nUsername: @{user.username}"
        )
        await update.message.reply_text(
            "Спасибо! Мы проверим оплату и свяжемся с вами 👍"
        )
        return

    # ---------------- РЕЗУЛЬТАТ ----------------
    if text == "Результат":
        await send_result(update, context)
        return

    # ---------------- ВОПРОС ----------------
    if text == "Задать вопрос":
        context.user_data["mode"] = "question"
        await update.message.reply_text(
            "Напишите ваш вопрос — я передам его специалисту 👇"
        )
        return

    if context.user_data.get("mode") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Вопрос от @{user.username} (ID: {user.id}):\n\n{text}"
        )
        await update.message.reply_text("С вами скоро свяжутся 👍")
        context.user_data["mode"] = None
        return

    # ---------------- ОПЛАТА ----------------
    if text == "Оплатить":
        await update.message.reply_text(
            "Выберите тариф для оплаты:",
            reply_markup=pay_menu
        )
        return

    # ---------------- ВЫБОР ТАРИФА ----------------
    tariff_map = {
        "Базовый": "Базовый",
        "Стандарт ⭐ Рекомендуем": "Стандарт",
        "Под ключ": "Под ключ"
    }

    if text in tariff_map:
        tariff = tariff_map[text]
        context.user_data["tariff"] = tariff

        await update.message.reply_text(
            TARIFFS[tariff]["desc"],
            reply_markup=action_menu
        )
        return

    # ---------------- ОПЛАТА ПО ТАРИФУ ----------------
    for tariff, data in TARIFFS.items():
        if text == data["pay_text"]:
            await update.message.reply_text(
                f"Оплата тарифа:\n👉 {data['link']}\n\nПосле оплаты нажмите «Я оплатил» 👍"
            )
            return

    # ---------------- FALLBACK ----------------
    await update.message.reply_text(
        "Пожалуйста, используйте кнопки ниже 👇"
    )

# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
