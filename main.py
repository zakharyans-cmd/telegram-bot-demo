import os
import time
import logging

from telegram import (
    Update,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------------- ЛОГИ ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- НАСТРОЙКИ ----------------
TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN:
    raise ValueError("BOT_TOKEN not set")

if not ADMIN_ID:
    raise ValueError("ADMIN_ID not set")

ADMIN_ID = int(ADMIN_ID)

# ---------------- ОПЛАТА ----------------
PAY_LINK_BASIC = "https://yookassa.ru/my/i/afvRwpMt2kxa/l"
PAY_LINK_STANDARD = "https://yookassa.ru/my/i/afvR6WwgBU92/l"
PAY_LINK_PRO = "https://yookassa.ru/my/i/afvSFHFX15eq/l"

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
        ["Оплатить"],
        ["Я оплатил"],
        ["К тарифам"]
    ],
    resize_keyboard=True
)

# ---------------- ДОПУСТИМЫЕ КНОПКИ ----------------
allowed_buttons = {
    "Подобрать вариант",
    "Продолжить подбор",
    "Сразу к оплате",
    "Посмотреть тарифы",
    "Теряю заявки",
    "Мало продаж",
    "Хочу автоматизацию",
    "Базовый",
    "Стандарт ⭐ Рекомендуем",
    "Под ключ",
    "Оплатить",
    "К тарифам",
    "Я оплатил",
    "Задать вопрос"
}

# ---------------- АНАЛИТИКА ----------------
async def notify_admin(context, user, action, extra=""):
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"📊 ДЕЙСТВИЕ\n\n"
                f"👤 {user.first_name}\n"
                f"🆔 {user.id}\n"
                f"📎 @{user.username if user.username else 'нет'}\n"
                f"⚡ {action}\n"
                f"{extra}"
            )
        )
    except Exception as e:
        logger.error(f"notify_admin error: {e}")

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data.clear()

        user_type = "cold"

        if context.args and len(context.args) > 0:
            user_type = context.args[0]

        context.user_data["user_type"] = user_type

        await notify_admin(
            context,
            update.effective_user,
            f"START ({user_type})"
        )

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
                "Я помогу Вам подобрать решение, "
                "которое поможет не терять клиентов и увеличить продажи."
            )
            keyboard = main_menu

        await update.message.reply_text(text, reply_markup=keyboard)

    except Exception as e:
        logger.exception(e)

# ---------------- ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        if not update.message:
            return

        user = update.effective_user
        text = update.message.text

        if not text:
            return

        # ---------------- АНТИСПАМ ----------------
        now = time.time()

        last_action = context.user_data.get("last_action", 0)

        if now - last_action < 1:
            return

        context.user_data["last_action"] = now

        logger.info(f"{user.id} -> {text}")

        # ---------------- УЖЕ ОПЛАТИЛ ----------------
        if context.user_data.get("paid"):
            await update.message.reply_text(
                "Оплата уже отправлена 👍\n\n"
                "С Вами скоро свяжутся.",
                reply_markup=main_menu
            )
            return

        # ---------------- ВОПРОС ----------------
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

            await update.message.reply_text(
                "С Вами скоро свяжутся 👍",
                reply_markup=main_menu
            )

            context.user_data["step"] = None
            return

        # ---------------- FALLBACK ----------------
        if text not in allowed_buttons:
            await update.message.reply_text(
                "Выберите вариант из меню 👇",
                reply_markup=main_menu
            )
            return

        # ---------------- ПОДБОР ----------------
        if text in ["Подобрать вариант", "Продолжить подбор"]:

            await notify_admin(context, user, "НАЧАЛ ПОДБОР")

            await update.message.reply_text(
                "Скажите, что сейчас для Вас наиболее актуально?",
                reply_markup=problem_menu
            )
            return

        # ---------------- СРАЗУ К ОПЛАТЕ ----------------
        if text == "Сразу к оплате":

            await notify_admin(context, user, "СРАЗУ К ОПЛАТЕ")

            await update.message.reply_text(
                "Выберите тариф 👇",
                reply_markup=tariff_menu
            )
            return

        # ---------------- ТАРИФЫ ----------------
        if text in ["К тарифам", "Посмотреть тарифы"]:

            await notify_admin(context, user, "ОТКРЫЛ ТАРИФЫ")

            await update.message.reply_text(
                "Выберите подходящий вариант 👇",
                reply_markup=tariff_menu
            )
            return

        # ---------------- ПРОБЛЕМЫ ----------------
        if text in ["Теряю заявки", "Мало продаж", "Хочу автоматизацию"]:

            context.user_data["problem"] = text

            await notify_admin(context, user, f"ПРОБЛЕМА: {text}")

            await update.message.reply_text(
                "Понял Вас 👌\n\n"
                "Ниже варианты решения 👇",
                reply_markup=tariff_menu
            )
            return

        # ---------------- ТАРИФ БАЗОВЫЙ ----------------
        if text == "Базовый":

            context.user_data["tariff"] = "Базовый"
            context.user_data["pay_link"] = PAY_LINK_BASIC

            await notify_admin(context, user, "СМОТРИТ ТАРИФ БАЗОВЫЙ")

            await update.message.reply_text(
                "Базовый 👌\n\n"
                "Подходит, если важно перестать терять заявки и быстрее отвечать клиентам.\n\n"
                "Включает:\n"
                "— автоматические ответы\n"
                "— меню с выбором услуг\n"
                "— сбор заявок\n"
                "— уведомления о новых клиентах\n"
                "— удобное общение через Telegram\n\n"
                "Хороший вариант для небольшого бизнеса или старта автоматизации.\n\n"
                "Стоимость зависит от задач бизнеса 👌",
                reply_markup=pay_menu
            )
            return

        # ---------------- ТАРИФ СТАНДАРТ ----------------
        if text == "Стандарт ⭐ Рекомендуем":

            context.user_data["tariff"] = "Стандарт"
            context.user_data["pay_link"] = PAY_LINK_STANDARD

            await notify_admin(context, user, "СМОТРИТ ТАРИФ СТАНДАРТ")

            await update.message.reply_text(
                "Стандарт ⭐\n\n"
                "Оптимальный вариант для большинства бизнесов.\n\n"
                "Включает:\n"
                "— автоматические ответы\n"
                "— обработку заявок\n"
                "— прогрев клиентов\n"
                "— уведомления о новых лидах\n\n"
                "Стоимость зависит от задач бизнеса 👌",
                reply_markup=pay_menu
            )
            return

        # ---------------- ТАРИФ ПОД КЛЮЧ ----------------
        if text == "Под ключ":

            context.user_data["tariff"] = "Под ключ"
            context.user_data["pay_link"] = PAY_LINK_PRO

            await notify_admin(context, user, "СМОТРИТ ТАРИФ ПОД КЛЮЧ")

            await update.message.reply_text(
                "Под ключ 🚀\n\n"
                "Полная система автоматизации под Ваш бизнес.\n\n"
                "Включает:\n"
                "— индивидуальную настройку бота\n"
                "— автоматическую обработку клиентов\n"
                "— прогрев и сопровождение заявок\n"
                "— уведомления и распределение лидов\n"
                "— настройку сценариев под Ваши задачи\n"
                "— помощь с запуском и внедрением\n\n"
                "Подходит бизнесам, где важно масштабирование и стабильный поток клиентов.\n\n"
                "Стоимость рассчитывается индивидуально 👌",
                reply_markup=pay_menu
            )
            return

        # ---------------- ОПЛАТА ----------------
        if text == "Оплатить":

            pay_link = context.user_data.get("pay_link")

            if not pay_link:
                await update.message.reply_text(
                    "Сначала выберите тариф 👇",
                    reply_markup=tariff_menu
                )
                return

            await notify_admin(context, user, "ПЕРЕШЕЛ К ОПЛАТЕ")

            await update.message.reply_text(
                f"Ссылка для оплаты 👇\n\n"
                f"{pay_link}\n\n"
                "После оплаты нажмите «Я оплатил».",
                reply_markup=pay_menu
            )
            return

        # ---------------- Я ОПЛАТИЛ ----------------
        if text == "Я оплатил":

            if context.user_data.get("payment_sent"):
                return

            context.user_data["payment_sent"] = True
            context.user_data["paid"] = True

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
                "Спасибо за оплату 👍\n\n"
                "Проверяем поступление платежа.\n\n"
                "Скоро с Вами свяжутся для уточнения деталей.",
                reply_markup=main_menu
            )
            return

        # ---------------- ВОПРОС ----------------
        if text == "Задать вопрос":

            context.user_data["step"] = "question"

            await notify_admin(context, user, "ЗАДАЕТ ВОПРОС")

            await update.message.reply_text("Напишите Ваш вопрос 👇")
            return

        await update.message.reply_text(
            "Выберите вариант из меню 👇",
            reply_markup=main_menu
        )

    except Exception as e:
        logger.exception(e)

        await update.message.reply_text(
            "Ошибка. Попробуйте ещё раз 👇",
            reply_markup=main_menu
        )

# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

if __name__ == "__main__":
    print("Bot started")
    app.run_polling()
