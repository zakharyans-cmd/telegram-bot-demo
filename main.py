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
    try:
        context.user_data.clear()

        user_type = "cold"

        if context.args and len(context.args) > 0 and context.args[0] == "warm":
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


    # ---------------- ПРОБЛЕМЫ ----------------
    if text == "Теряю заявки":
        context.user_data["problem"] = text

        await update.message.reply_text(
            "Понял Вас.\n\n"
            "Это значит, что часть клиентов теряется на этапе переписки или ответа.\n\n"
            "Есть 3 варианта решения:",
            reply_markup=tariff_menu
        )
        return


    if text == "Мало продаж":
        context.user_data["problem"] = text

        await update.message.reply_text(
            "Понял Вас.\n\n"
            "Часто проблема в том, что клиент не доводится до решения.\n\n"
            "Есть 3 варианта решения:",
            reply_markup=tariff_menu
        )
        return


    if text == "Хочу автоматизацию":
        context.user_data["problem"] = text

        await update.message.reply_text(
            "Понял Вас.\n\n"
            "Это про систему, которая сама ведёт клиента к заявке.\n\n"
            "Есть 3 варианта решения:",
            reply_markup=tariff_menu
        )
        return


    # ---------------- ТАРИФЫ ----------------
    if text == "Базовый":
        context.user_data["tariff"] = "Базовый"

        await update.message.reply_text(
            "Базовый вариант 👇\n\n"
            "Подходит, если важно перестать терять входящие заявки.\n\n"
            "— быстрые ответы\n"
            "— фиксация заявок\n"
            "— базовая обработка\n\n",
            reply_markup=pay_menu
        )
        return


    if text == "Стандарт ⭐ Рекомендуем":
        context.user_data["tariff"] = "Стандарт"

        await update.message.reply_text(
            "Стандарт ⭐\n\n"
            "Оптимальный вариант для большинства бизнесов.\n\n"
            "— удержание клиента\n"
            "— сценарии переписки\n"
            "— рост конверсии\n\n"
            "Чаще всего выбирают именно его.",
            reply_markup=pay_menu
        )
        return


    if text == "Под ключ":
        context.user_data["tariff"] = "Под ключ"

        await update.message.reply_text(
            "Под ключ 👇\n\n"
            "Полная система обработки клиентов.\n\n"
            "— автоматизация\n"
            "— прогрев\n"
            "— максимальная конверсия",
            reply_markup=pay_menu
        )
        return


    # ---------------- ОПЛАТА ----------------
    if text == "Оплатить 50 000₽":
        await update.message.reply_text(
            f"Ссылка для оплаты Стандарта 👇\n\n{PAY_LINK_STANDARD}\n\n"
            "После оплаты нажмите «Я оплатил».",
            reply_markup=ReplyKeyboardMarkup(
                [["Я оплатил"], ["К тарифам"]],
                resize_keyboard=True
            )
        )
        return


    # ---------------- ОПЛАТА ФАКТ ----------------
    if text == "Я оплатил":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "💰 ОПЛАТА\n\n"
                f"Имя: {user.first_name}\n"
                f"Username: @{user.username if user.username else 'нет'}\n"
                f"Проблема: {context.user_data.get('problem')}\n"
                f"Тариф: {context.user_data.get('tariff')}"
            )
        )

        await update.message.reply_text(
            "Спасибо! Проверим оплату 👍\n\n"
            "После подтверждения оплаты начинаем настройку системы под Ваш бизнес.\n"
            "С Вами свяжутся для уточнения деталей."
        )
        return


    # ---------------- ВОПРОС ----------------
    if text == "Задать вопрос":
        context.user_data["step"] = "question"

        await update.message.reply_text("Напишите Ваш вопрос 👇")
        return


    if context.user_data.get("step") == "question":
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
        context.user_data["step"] = None
        return


# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.bot.delete_webhook(drop_pending_updates=True)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

if __name__ == "__main__":
    print("Bot started")
    app.run_polling()
