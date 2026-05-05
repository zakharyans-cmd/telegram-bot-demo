import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "509239406"))

if not TOKEN:
    raise ValueError("BOT_TOKEN не задан")


# ---------------- ОПЛАТЫ ----------------
PAY_LINKS = {
    "Базовый — 30 000₽": "ССЫЛКА_ЮКАССА_БАЗОВЫЙ",
    "Стандарт — 50 000₽ ⭐ Рекомендуем": "ССЫЛКА_ЮКАССА_СТАНДАРТ",
    "Под ключ — 70 000₽": "ССЫЛКА_ЮКАССА_ПОД_КЛЮЧ"
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
        ["Показать как будет у меня", "Оплатить"],
        ["Задать вопрос", "К тарифам"]
    ],
    resize_keyboard=True
)

cold_action_menu = ReplyKeyboardMarkup(
    [
        ["Да, покажи пример"],
        ["Показать как будет у меня", "Оплатить"],
        ["Сравнить тарифы", "Задать вопрос"],
        ["К тарифам"]
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


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    args = context.args

    if args and args[0] == "warm":
        context.user_data["flow"] = "warm"

        await update.message.reply_text(
            "Как и обсуждали 👇\n\n"
            "Вот варианты, выберите, что ближе:",
            reply_markup=tariff_menu
        )

    else:
        context.user_data["flow"] = "cold"

        await update.message.reply_text(
            "Привет 👋\n\n"
            "Большинство бизнесов теряют часть клиентов ещё в переписке\n\n"
            "— не ответили вовремя\n"
            "— забыли написать\n"
            "— клиент просто пропал\n\n"
            "В итоге — теряются деньги\n\n"
            "Это можно закрыть ботом\n\n"
            "Посмотрите варианты 👇",
            reply_markup=tariff_menu
        )


# ---------------- НАПОМИНАНИЕ ----------------
async def payment_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=context.job.data
    )


# ---------------- ЛОГИКА ----------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text
    user = update.effective_user
    flow = context.user_data.get("flow", "cold")
    chat_id = update.effective_chat.id


    # К тарифам
    if text == "К тарифам":
        context.user_data.pop("tariff", None)

        await update.message.reply_text(
            "Выберите тариф 👇",
            reply_markup=tariff_menu
        )
        return


    # Сравнение
    if text == "Сравнить тарифы":
        await update.message.reply_text(
            "Коротко 👇\n\n"
            "Базовый — чтобы не терять входящие\n\n"
            "Стандарт ⭐ — ведёт клиента и доводит до заявки\n\n"
            "Под ключ — полностью закрывает общение\n\n"
            "Если сомневаетесь — берите «Стандарт»"
        )
        return


    # Вопрос
    if text == "Задать вопрос":
        context.user_data["step"] = "question"

        await update.message.reply_text(
            "Напишите вопрос 👇\nОтвечаю обычно в течение 10–15 минут"
        )
        return


    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "📩 ВОПРОС\n\n"
                f"{user.first_name}\n"
                f"@{user.username if user.username else 'нет'}\n"
                f"Тариф: {context.user_data.get('tariff')}\n\n"
                f"{update.message.text}"
            )
        )

        await update.message.reply_text("Отвечу вам в ближайшее время 👍")
        context.user_data["step"] = None
        return


    # Диагностика
    if text == "Показать как будет у меня":
        context.user_data["step"] = "diagnostic"

        await update.message.reply_text(
            "Напишите 👇\n\n"
            "— чем занимаетесь\n"
            "— откуда приходят заявки\n\n"
            "Покажу, как это будет у вас"
        )
        return


    if context.user_data.get("step") == "diagnostic":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🔥 РАЗБОР\n\n"
                f"{user.first_name}\n"
                f"@{user.username if user.username else 'нет'}\n\n"
                f"{update.message.text}"
            )
        )

        await update.message.reply_text(
            "Посмотрю и напишу 👇"
        )

        # умный дожим после диагностики
        context.job_queue.run_once(
            payment_reminder,
            6 * 3600,
            chat_id=chat_id,
            data="Посмотрел ваш случай\n\nЕсть точки, где теряются клиенты\n\nМогу расписать"
        )

        context.job_queue.run_once(
            payment_reminder,
            24 * 3600,
            chat_id=chat_id,
            data="Напомню про ваш вопрос\n\nЕсли актуально — напишите"
        )

        context.user_data["step"] = None
        return


    # Я оплатил
    if text == "Я оплатил":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "💰 ОПЛАТА\n\n"
                f"{user.first_name}\n"
                f"@{user.username if user.username else 'нет'}\n"
                f"Тариф: {context.user_data.get('tariff')}"
            )
        )

        await update.message.reply_text(
            "Отлично 👍\n\n"
            "Напишите:\n"
            "— чем занимаетесь\n"
            "— куда подключаем\n\n"
            "Начнём 👇"
        )
        return


    # Оплатить
    if text == "Оплатить":
        await update.message.reply_text(
            "Выберите тариф 👇",
            reply_markup=pay_menu
        )
        return


    # выбор тарифа
    if text in ["Базовый", "Стандарт ⭐ Рекомендуем", "Под ключ"]:

        mapping = {
            "Базовый": "Базовый",
            "Стандарт ⭐ Рекомендуем": "Стандарт",
            "Под ключ": "Под ключ"
        }

        tariff = mapping[text]
        context.user_data["tariff"] = tariff

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔥 ЛИД\n{user.first_name}\nТариф: {tariff}"
        )

        if tariff == "Стандарт":
            msg = (
                "Стандарт ⭐\n\n"
                "Оптимальный вариант\n\n"
                "— отвечает за вас\n"
                "— не теряет клиентов\n"
                "— доводит до заявки\n\n"
                "Обычно окупается быстро\n\n"
                "Можно посмотреть под вас\n"
                "или сразу запустить 👇"
            )

        elif tariff == "Базовый":
            msg = (
                "Базовый\n\n"
                "Закрывает базовую проблему\n"
                "— клиенту всегда отвечают\n\n"
                "Можно потом масштабировать\n\n"
                "Хотите покажу под вас?"
            )

        else:
            msg = (
                "Под ключ\n\n"
                "Полная автоматизация\n\n"
                "Вы получаете уже тёплых клиентов\n\n"
                "Могу показать, как это будет у вас"
            )

        await update.message.reply_text(
            msg,
            reply_markup=action_menu if flow == "warm" else cold_action_menu
        )

        # умный дожим после выбора тарифа
        context.job_queue.run_once(
            payment_reminder,
            3 * 3600,
            chat_id=chat_id,
            data="Вы смотрели вариант\n\nЕсли есть сомнения — напишите"
        )

        context.job_queue.run_once(
            payment_reminder,
            12 * 3600,
            chat_id=chat_id,
            data="Если откладываете — это нормально\n\nМогу коротко сказать, подойдёт ли вам"
        )

        return


    # оплата
    if text in PAY_LINKS:
        link = PAY_LINKS[text]

        await update.message.reply_text(
            f"Оплата 👇\n{link}\n\nПосле оплаты напишите «Я оплатил»",
            reply_markup=ReplyKeyboardMarkup([["Я оплатил"], ["К тарифам"]], resize_keyboard=True)
        )

        # умный дожим оплаты
        context.job_queue.run_once(
            payment_reminder,
            4 * 3600,
            chat_id=chat_id,
            data="Вы открывали оплату\n\nЕсли остался вопрос — напишите"
        )

        context.job_queue.run_once(
            payment_reminder,
            20 * 3600,
            chat_id=chat_id,
            data="Если коротко:\n\nэто решает проблему потери клиентов\n\nЕсли актуально — имеет смысл внедрить"
        )

        return


    await update.message.reply_text("Выберите вариант 👇")


# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

if __name__ == "__main__":
    app.run_polling()
