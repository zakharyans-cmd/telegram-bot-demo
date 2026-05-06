import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ---------------- ЛОГИ ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- НАСТРОЙКИ ----------------
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "509239406"))

if not TOKEN:
    raise ValueError("BOT_TOKEN не задан")

# ---------------- ОПЛАТА ----------------
PAY_LINK_STANDARD = "https://yookassa.ru/my/i/afs77IHpLI6Y/l"

# ---------------- КНОПКИ ----------------
main_menu = ReplyKeyboardMarkup(
    [["Подобрать вариант"], ["Посмотреть тарифы", "Задать вопрос"]],
    resize_keyboard=True
)

warm_menu = ReplyKeyboardMarkup(
    [["Продолжить подбор"], ["Сразу к оплате", "Задать вопрос"]],
    resize_keyboard=True
)

problem_menu = ReplyKeyboardMarkup(
    [["Теряю заявки"], ["Мало продаж"], ["Хочу автоматизацию"]],
    resize_keyboard=True
)

tariff_menu = ReplyKeyboardMarkup(
    [["Базовый"], ["Стандарт ⭐ Рекомендуем"], ["Под ключ"]],
    resize_keyboard=True
)

pay_menu = ReplyKeyboardMarkup(
    [["Оплатить 50 000₽"], ["К тарифам"]],
    resize_keyboard=True
)

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data.clear()

        context.user_data["stage"] = "start"
        context.user_data["score"] = 0

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

    except Exception as e:
        logger.error(f"Error in start: {e}")


# ---------------- ХЕНДЛЕР ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text
    user = update.effective_user

    stage = context.user_data.get("stage", "start")


    # ---------------- ПОДБОР ----------------
    if text in ["Подобрать вариант", "Продолжить подбор"]:
        context.user_data["stage"] = "problem"
        context.user_data["score"] += 1

        await update.message.reply_text(
            "Понял Вас 👍\n\nЧто сейчас для Вас наиболее актуально?",
            reply_markup=problem_menu
        )
        return


    # ---------------- ПРОБЛЕМЫ ----------------
    if text in ["Теряю заявки", "Мало продаж", "Хочу автоматизацию"]:
        if stage not in ["problem"]:
            return

        context.user_data["problem"] = text
        context.user_data["stage"] = "tariff"
        context.user_data["score"] += 2

        await update.message.reply_text(
            "Понял Вас 👍\n\nЕсть 3 варианта решения:",
            reply_markup=tariff_menu
        )
        return


    # ---------------- ТАРИФЫ ----------------
    if text in ["Базовый", "Стандарт ⭐ Рекомендуем", "Под ключ"]:
        if stage not in ["tariff"]:
            return

        context.user_data["tariff"] = text
        context.user_data["stage"] = "payment"
        context.user_data["score"] += 2

        if text == "Базовый":
            desc = "Подходит, если важно перестать терять заявки."
        elif text.startswith("Стандарт"):
            desc = "Оптимальный вариант для роста конверсии."
        else:
            desc = "Полная система автоматизации и прогрева."

        await update.message.reply_text(
            f"{text} 👇\n\n{desc}\n\nПеред оплатой:\n"
            "🔹 Вы можете начать внедрение уже сегодня\n"
            "🔹 Средний рост конверсии 20–40%\n",
            reply_markup=pay_menu
        )
        return


    # ---------------- ОПЛАТА ----------------
    if text == "Оплатить 50 000₽":
        await update.message.reply_text(
            f"Ссылка для оплаты 👇\n\n{PAY_LINK_STANDARD}\n\n"
            "После оплаты напишите «Я оплатил».",
            reply_markup=ReplyKeyboardMarkup(
                [["Я оплатил"], ["К тарифам"]],
                resize_keyboard=True
            )
        )
        return


    # ---------------- ОПЛАТА ФАКТ ----------------
    if text == "Я оплатил":
        context.user_data["stage"] = "paid"

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "💰 ОПЛАТА\n\n"
                f"Имя: {user.first_name}\n"
                f"Username: @{user.username if user.username else 'нет'}\n"
                f"Проблема: {context.user_data.get('problem', 'не указано')}\n"
                f"Тариф: {context.user_data.get('tariff', 'не указано')}\n"
                f"Score: {context.user_data.get('score', 0)}"
            )
        )

        await update.message.reply_text("Спасибо! Проверяем оплату 👍")

        # дожимная фраза (как ты просил)
        await update.message.reply_text(
            "Если возникнут вопросы — мы всегда на связи 👍"
        )

        return


    # ---------------- ВОПРОС ----------------
    if text == "Задать вопрос":
        context.user_data["stage"] = "question"

        await update.message.reply_text("Напишите Ваш вопрос 👇")
        return


    if context.user_data.get("stage") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "📩 ВОПРОС\n\n"
                f"{user.first_name}\n"
                f"@{user.username if user.username else 'нет'}\n\n"
                f"{text}"
            )
        )

        await update.message.reply_text("С Вами скоро свяжутся 👍")
        context.user_data["stage"] = "start"
        return


    # ---------------- К ТАРИФАМ ----------------
    if text == "К тарифам":
        context.user_data["stage"] = "tariff"

        await update.message.reply_text(
            "Выберите вариант:",
            reply_markup=tariff_menu
        )
        return


# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.bot.delete_webhook(drop_pending_updates=True)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

if __name__ == "__main__":
    print("Bot started")
