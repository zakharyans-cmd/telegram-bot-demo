import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "509239406"))

if not TOKEN:
    raise ValueError("BOT_TOKEN не задан")


# ---------------- ОПЛАТА ----------------
PAY_LINK_STANDARD = "https://yookassa.ru/my/i/afs77IHpLI6Y/l"


# ---------------- КНОПКИ ----------------
main_menu = ReplyKeyboardMarkup(
    [
        ["Подобрать вариант"],
        ["Посмотреть тарифы", "Задать вопрос"]
    ],
    resize_keyboard=True
)

warm_menu = ReplyKeyboardMarkup(
    [
        ["Продолжить подбор"],
        ["Сразу к оплате", "Задать вопрос"]
    ],
    resize_keyboard=True
)

problem_menu = ReplyKeyboardMarkup(
    [
        ["Теряю заявки"],
        ["Мало продаж"],
        ["Хочу автоматизацию"]
    ],
    resize_keyboard=True
)

tariff_menu = ReplyKeyboardMarkup(
    [
        ["Базовый"],
        ["Стандарт ⭐ Рекомендуем"],
        ["Под ключ"]
    ],
    resize_keyboard=True
)

pay_menu = ReplyKeyboardMarkup(
    [
        ["Оплатить 50 000₽"],
        ["К тарифам"]
    ],
    resize_keyboard=True
)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    user_type = "cold"

    if context.args and context.args[0] == "warm":
        user_type = "warm"

    context.user_data["user_type"] = user_type

    if user_type == "warm":
        text = (
            "Привет 👋\n\n"
            "Рад Вас видеть снова.\n"
            "Давайте быстро подберём подходящее решение под Ваш бизнес."
        )
        keyboard = warm_menu
    else:
        text = (
            "Привет 👋\n\n"
            "Я помогу Вам подобрать решение, которое поможет не терять клиентов и увеличить продажи."
        )
        keyboard = main_menu

    await update.message.reply_text(text, reply_markup=keyboard)


# ---------------- ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text
    user = update.effective_user


    # ---------------- ПОДБОР ----------------
    if text in ["Подобрать вариант", "Продолжить подбор"]:

        await update.message.reply_text(
            "Понял Вас 👍\n\n"
            "Скажите, что сейчас для Вас наиболее актуально?",
            reply_markup=problem_menu
        )
        return


    # ---------------- ПРОБЛЕМА ----------------
    if text == "Теряю заявки":
        context.user_data["problem"] = text

        await update.message.reply_text(
            "Понял Вас.\n\n"
            "Это значит, что клиенты уже пишут, но часть из них теряется на этапе переписки или ответа.\n\n"
            "Есть 3 варианта решения:",
            reply_markup=tariff_menu
        )
        return


    if text == "Мало продаж":
        context.user_data["problem"] = text

        await update.message.reply_text(
            "Понял Вас.\n\n"
            "В этом случае проблема чаще всего в том, что клиенты не доходят до принятия решения.\n\n"
            "Есть 3 варианта решения:",
            reply_markup=tariff_menu
        )
        return


    if text == "Хочу автоматизацию":
        context.user_data["problem"] = text

        await update.message.reply_text(
            "Понял Вас.\n\n"
            "Это про выстраивание системы, которая сама ведёт клиента до заявки или покупки.\n\n"
            "Есть 3 варианта решения:",
            reply_markup=tariff_menu
        )
        return


    # ---------------- ТАРИФЫ ----------------
    if text == "Базовый":
        context.user_data["tariff"] = "Базовый"

        await update.message.reply_text(
            "Базовый вариант 👇\n\n"
            "Подходит, если важно просто перестать терять входящие заявки.\n\n"
            "— быстрые ответы клиентам\n"
            "— фикса
