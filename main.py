import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "509239406"))

if not TOKEN:
    raise ValueError("BOT_TOKEN не задан")


# ---------------- ОПЛАТА ----------------
PAY_LINKS = {
    "Стандарт — 50 000₽ ⭐ Рекомендуем": "https://yookassa.ru/my/i/afs77IHpLI6Y/l"
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

cold_menu = ReplyKeyboardMarkup(
    [
        ["Да, покажи пример"],
        ["Показать как будет у меня", "Оплатить"],
        ["Сравнить тарифы", "Задать вопрос"]
    ],
    resize_keyboard=True
)

pay_menu = ReplyKeyboardMarkup(
    [
        ["Стандарт — 50 000₽ ⭐ Рекомендуем"]
    ],
    resize_keyboard=True
)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    args = context.args

    # WARM
    if args and args[0] == "warm":
        context.user_data["flow"] = "warm"

        await update.message.reply_text(
            "Как и обсуждали 👇\n\n"
            "Выберите вариант:",
            reply_markup=tariff_menu
        )

    # COLD
    else:
        context.user_data["flow"] = "cold"

        await update.message.reply_text(
            "Привет 👋\n\n"
            "Большинство бизнесов теряют клиентов в переписке\n"
            "— не отвечают вовремя\n"
            "— теряются заявки\n"
            "— клиент просто уходит\n\n"
            "Это можно исправить автоматизацией\n\n"
            "Выберите вариант 👇",
            reply_markup=tariff_menu
        )


# ---------------- JOB ----------------
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


    # К ТАРИФАМ
    if text == "К тарифам":
        await update.message.reply_text("Выберите тариф 👇", reply_markup=tariff_menu)
        return


    # СРАВНЕНИЕ
    if text == "Сравнить тарифы":
        await update.message.reply_text(
            "Коротко 👇\n\n"
            "Базовый — не терять входящие\n\n"
            "Стандарт ⭐ — ведёт клиента до заявки\n\n"
            "Под ключ — полная автоматизация\n\n"
            "Обычно берут Стандарт"
        )
        return


    # ВОПРОС
    if text == "Задать вопрос":
        context.user_data["step"] = "question"
        await update.message.reply_text("Напишите вопрос 👇")
        return


    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 ВОПРОС\n\n{user.first_name}\n{text}"
        )
        await update.message.reply_text("Ответим вам 👍")
        context.user_data["step"] = None
        return


    # ДИАГНОСТИКА
    if text == "Показать как будет у меня":
        context.user_data["step"] = "demo"
        await update.message.reply_text(
            "Напишите:\n— чем занимаетесь\n— откуда заявки"
        )
        return


    if context.user_data.get("step") == "demo":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔥 РАЗБОР\n\n{user.first_name}\n{text}"
        )

        await update.message.reply_text("Посмотрю и напишу 👍")
        context.user_data["step"] = None
        return


    # ТАРИФ
    if text in ["Базовый", "Стандарт ⭐ Рекомендуем", "Под ключ"]:

        context.user_data["tariff"] = text

        msg = {
            "Базовый": "Базовый — чтобы не терять заявки",
            "Стандарт ⭐ Рекомендуем": (
                "Стандарт ⭐\n\n"
                "— ведёт клиента\n"
                "— не теряет заявки\n"
                "— чаще всего выбирают его\n\n"
                "Можно посмотреть как будет у вас"
            ),
            "Под ключ": "Под ключ — максимум автоматизации"
        }[text]

        await update.message.reply_text(
            msg,
            reply_markup=action_menu if flow == "warm" else cold_menu
        )
        return


    # ОПЛАТА
    if text in PAY_LINKS:

        link = PAY_LINKS[text]

        await update.message.reply_text(
            f"Оплата 👇\n{link}\n\nПосле оплаты нажмите «Я оплатил»",
            reply_markup=ReplyKeyboardMarkup([["Я оплатил"]], resize_keyboard=True)
        )

        context.job_queue.run_once(
            payment_reminder,
            6 * 3600,
            chat_id=chat_id,
            data="Если остались вопросы — напишите"
        )

        context.job_queue.run_once(
            payment_reminder,
            24 * 3600,
            chat_id=chat_id,
            data="Если планировали запуск — можем начать"
        )

        return


    # fallback
    await update.message.reply_text("Выберите вариант 👇")


# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

if __name__ == "__main__":
    app.run_polling()
