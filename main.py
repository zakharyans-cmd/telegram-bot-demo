import os
import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------------- ЛОГИ ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

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
        ["К тарифам"]
    ],
    resize_keyboard=True
)

paid_menu = ReplyKeyboardMarkup(
    [
        ["Я оплатил"],
        ["К тарифам"]
    ],
    resize_keyboard=True
)

contact_menu = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(
                "Отправить номер",
                request_contact=True
            )
        ],
        ["Пропустить"]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
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
    "Задать вопрос",
    "Отправить номер",
    "Пропустить"
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

# ---------------- ДОЖИМЫ ----------------
async def followup_2_hours(context: ContextTypes.DEFAULT_TYPE):

    job = context.job
    user_id = job.chat_id

    if job.data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "Напоминаю 👋\n\n"
            "Вы смотрели варианты автоматизации для бизнеса.\n\n"
            "Если остались вопросы — можете написать их прямо сюда."
        )
    )

async def followup_24_hours(context: ContextTypes.DEFAULT_TYPE):

    job = context.job
    user_id = job.chat_id

    if job.data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "Здравствуйте 👋\n\n"
            "Часто клиенты возвращаются к вопросу автоматизации позже, "
            "когда появляется время всё спокойно посмотреть.\n\n"
            "Если захотите — помогу подобрать оптимальный вариант "
            "именно под Вашу задачу."
        )
    )

async def followup_72_hours(context: ContextTypes.DEFAULT_TYPE):

    job = context.job
    user_id = job.chat_id

    if job.data.get("paid"):
        return

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "Добрый день 👋\n\n"
            "Если вопрос ещё актуален — можете вернуться "
            "к выбору тарифа в любое время.\n\n"
            "Я на связи."
        )
    )

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

        await update.message.reply_text(
            text,
            reply_markup=keyboard
        )

    except Exception as e:
        logger.exception(f"Error in start: {e}")

# ---------------- ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        if not update.message:
            return

        user = update.effective_user

        # ---------------- КОНТАКТ ----------------
        if update.message.contact:

            phone = update.message.contact.phone_number

            context.user_data["phone"] = phone

            await notify_admin(
                context,
                user,
                "ОСТАВИЛ ТЕЛЕФОН",
                f"\n📱 {phone}"
            )

            await update.message.reply_text(
                "Спасибо 👍\n\n"
                "Теперь можете перейти к оплате.",
                reply_markup=pay_menu
            )

            return

        text = update.message.text

        if not text:
            return

        logger.info(f"{user.id} -> {text}")

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

            await notify_admin(
                context,
                user,
                "НАЧАЛ ПОДБОР"
            )

            await update.message.reply_text(
                "Скажите, что сейчас для Вас наиболее актуально?",
                reply_markup=problem_menu
            )

            return

        # ---------------- СРАЗУ К ОПЛАТЕ ----------------
        if text == "Сразу к оплате":

            await notify_admin(
                context,
                user,
                "СРАЗУ К ОПЛАТЕ"
            )

            await update.message.reply_text(
                "Выберите тариф 👇",
                reply_markup=tariff_menu
            )

            return

        # ---------------- К ТАРИФАМ ----------------
        if text in ["К тарифам", "Посмотреть тарифы"]:

            await notify_admin(
                context,
                user,
                "ОТКРЫЛ ТАРИФЫ"
            )

            await update.message.reply_text(
                "Выберите подходящий вариант 👇",
                reply_markup=tariff_menu
            )

            return

        # ---------------- ПРОБЛЕМЫ ----------------
        if text in [
            "Теряю заявки",
            "Мало продаж",
            "Хочу автоматизацию"
        ]:

            context.user_data["problem"] = text

            await notify_admin(
                context,
                user,
                f"ПРОБЛЕМА: {text}"
            )

            if text == "Теряю заявки":

                message = (
                    "Понял Вас 👌\n\n"
                    "Обычно в такой ситуации часть клиентов теряется "
                    "из-за долгих ответов или отсутствия системы обработки.\n\n"
                    "Ниже варианты решения 👇"
                )

            elif text == "Мало продаж":

                message = (
                    "Понял Вас 👌\n\n"
                    "Часто проблема в том, что клиент "
                    "не доводится до решения.\n\n"
                    "Ниже варианты решения 👇"
                )

            else:

                message = (
                    "Понял Вас 👌\n\n"
                    "Обычно автоматизация помогает снять "
                    "рутину и ускорить обработку клиентов.\n\n"
                    "Ниже варианты решения 👇"
                )

            await update.message.reply_text(
                message,
                reply_markup=tariff_menu
            )

            return

        # ---------------- ТАРИФЫ ----------------
        if text == "Базовый":

            context.user_data["tariff"] = "Базовый"
            context.user_data["pay_link"] = PAY_LINK_BASIC
            context.user_data["price"] = "30 000₽"

            await notify_admin(
                context,
                user,
                "СМОТРИТ ТАРИФ",
                "\nТариф: Базовый"
            )

            await update.message.reply_text(
                "Базовый 👇\n\n"
                "Подходит, если важно перестать терять входящие заявки.\n\n"
                "— быстрые ответы\n"
                "— фиксация заявок\n"
                "— базовая обработка",
                reply_markup=contact_menu
            )

            return

        if text == "Стандарт ⭐ Рекомендуем":

            context.user_data["tariff"] = "Стандарт"
            context.user_data["pay_link"] = PAY_LINK_STANDARD
            context.user_data["price"] = "50 000₽"

            await notify_admin(
                context,
                user,
                "СМОТРИТ ТАРИФ",
                "\nТариф: Стандарт"
            )

            await update.message.reply_text(
                "Стандарт ⭐\n\n"
                "Подходит бизнесам, где уже есть поток клиентов, "
                "но заявки теряются в переписке.\n\n"
                "Что получите:\n"
                "— сценарии продаж\n"
                "— автоматические ответы\n"
                "— доведение клиента до заявки\n"
                "— рост конверсии\n\n"
                "🔥 Самый популярный тариф.",
                reply_markup=contact_menu
            )

            return

        if text == "Под ключ":

            context.user_data["tariff"] = "Под ключ"
            context.user_data["pay_link"] = PAY_LINK_PRO
            context.user_data["price"] = "70 000₽"

            await notify_admin(
                context,
                user,
                "СМОТРИТ ТАРИФ",
                "\nТариф: Под ключ"
            )

            await update.message.reply_text(
                "Под ключ 👇\n\n"
                "Полная система обработки клиентов.\n\n"
                "— автоматизация\n"
                "— прогрев\n"
                "— максимальная конверсия",
                reply_markup=contact_menu
            )

            return

        # ---------------- ПРОПУСТИТЬ ТЕЛЕФОН ----------------
        if text == "Пропустить":

            await notify_admin(
                context,
                user,
                "ПРОПУСТИЛ ТЕЛЕФОН"
            )

            await update.message.reply_text(
                "Хорошо 👍\n\n"
                "Можете перейти к оплате.",
                reply_markup=pay_menu
            )

            return

        # ---------------- ОПЛАТА ----------------
        if text == "Оплатить":

            pay_link = context.user_data.get("pay_link")
            price = context.user_data.get("price")

            if not pay_link:

                await update.message.reply_text(
                    "Сначала выберите тариф 👇",
                    reply_markup=tariff_menu
                )

                return

            await notify_admin(
                context,
                user,
                "ПЕРЕШЕЛ К ОПЛАТЕ",
                f"\nТариф: {context.user_data.get('tariff')}"
            )

            await update.message.reply_text(
                "Оставьте, пожалуйста, номер телефона для связи 👇\n\n"
                "Это поможет быстрее связаться с Вами "
                "после оплаты или ответить на вопросы.",
                reply_markup=contact_menu
            )

            await update.message.reply_text(
                f"Ссылка для оплаты 👇\n\n"
                f"{pay_link}\n\n"
                f"Сумма: {price}\n\n"
                "После оплаты нажмите «Я оплатил».",
                reply_markup=paid_menu
            )

            # ---------------- ДОЖИМЫ ----------------
            context.job_queue.run_once(
                followup_2_hours,
                when=7200,
                chat_id=update.effective_chat.id,
                data={"paid": False}
            )

            context.job_queue.run_once(
                followup_24_hours,
                when=86400,
                chat_id=update.effective_chat.id,
                data={"paid": False}
            )

            context.job_queue.run_once(
                followup_72_hours,
                when=259200,
                chat_id=update.effective_chat.id,
                data={"paid": False}
            )

            return

        # ---------------- ОПЛАТА ФАКТ ----------------
        if text == "Я оплатил":

            if context.user_data.get("payment_sent"):

                await update.message.reply_text(
                    "Информация об оплате уже отправлена 👍"
                )

                return

            context.user_data["payment_sent"] = True
            context.user_data["paid"] = True

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "💰 ОПЛАТА\n\n"
                    f"Имя: {user.first_name}\n"
                    f"Username: @{user.username if user.username else 'нет'}\n"
                    f"Телефон: {context.user_data.get('phone', 'не указан')}\n"
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

            await notify_admin(
                context,
                user,
                "ЗАДАЕТ ВОПРОС"
            )

            await update.message.reply_text(
                "Напишите Ваш вопрос 👇"
            )

            return

        # ---------------- FALLBACK ----------------
        await update.message.reply_text(
            "Выберите вариант из меню 👇",
            reply_markup=main_menu
        )

    except Exception as e:

        logger.exception(f"Handler error: {e}")

        await update.message.reply_text(
            "Произошла ошибка. Попробуйте ещё раз 👇",
            reply_markup=main_menu
        )

# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.CONTACT,
        handler
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handler
    )
)

if __name__ == "__main__":

    print("Bot started")

    app.run_polling()
