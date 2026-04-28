import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "509239406"))

if not TOKEN:
    raise ValueError("BOT_TOKEN не задан")


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
        ["Сравнить тарифы", "Задать вопрос", "Оплатить"],
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


# ---------------- НАПОМИНАНИЯ ----------------
async def payment_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    hours = context.job.data

    user_data = context.application.user_data.get(chat_id, {})
    if user_data.get("paid") or user_data.get("asked"):
        return

    messages = {
        6: "Напомню 👇\n\nВы смотрели подключение системы.\nЕсли остались вопросы — можете задать их здесь.",
        24: "Возвращаюсь к вам 👇\n\nТакие решения обычно быстро окупаются за счёт возврата потерянных клиентов.",
        48: "Последний раз напомню 👇\n\nЕсли тема ещё актуальна — напишите, подскажу лучший вариант под вашу задачу."
    }

    await context.bot.send_message(chat_id=chat_id, text=messages[hours])


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
    if not update.message:
        return

    text = update.message.text

    # К тарифам
    if text == "К тарифам":
        context.user_data.pop("tariff", None)

        await update.message.reply_text(
            "Давайте сравним варианты 👇\nВыберите тариф:",
            reply_markup=tariff_menu
        )
        return

    # Сравнение тарифов
    if text == "Сравнить тарифы":
        await update.message.reply_text(
            "Сравнение вариантов 👇\n\n"
            "Базовый — 30 000₽\n"
            "Подходит, если нужно просто не терять входящие\n"
            "— отвечает клиентам\n"
            "— фиксирует заявки\n"
            "— убирает “случайных”\n\n"
            "Стандарт — 50 000₽ ⭐\n"
            "Оптимальный вариант\n"
            "— удерживает клиента в диалоге\n"
            "— ведёт по сценарию\n"
            "— доводит до контакта\n\n"
            "👉 чаще всего выбирают именно его\n\n"
            "Под ключ — 70 000₽\n"
            "Максимальный результат\n"
            "— полный прогрев клиента\n"
            "— автоматизация общения\n"
            "— приходят уже “тёплые” заявки\n\n"
            "Если сомневаетесь — берите «Стандарт» 👍"
        )
        return

    # Вопрос
    if text == "Задать вопрос":
        context.user_data["step"] = "question"
        context.user_data["asked"] = True

        await update.message.reply_text(
            "Напишите ваш вопрос — я передам его специалисту 👇"
        )
        return

    if context.user_data.get("step") == "question":
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Вопрос от {update.effective_user.id}\nТариф: {context.user_data.get('tariff')}\n\n{update.message.text}"
        )
        await update.message.reply_text("С вами скоро свяжутся 👍")
        context.user_data["step"] = None
        return

    # Я оплатил
    if text == "Я оплатил":
        context.user_data["paid"] = True

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Пользователь {update.effective_user.id} сообщил об оплате\nТариф: {context.user_data.get('tariff')}"
        )

        await update.message.reply_text("Спасибо! Мы проверим оплату и свяжемся с вами 👍")
        return

    # Оплатить
    if text == "Оплатить":
        await update.message.reply_text(
            "Выберите тариф для оплаты:",
            reply_markup=pay_menu
        )
        return

    # Выбор тарифа
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

    # Оплата тарифа
    if text in PAY_LINKS:
        link = PAY_LINKS[text]

        await update.message.reply_text(
            f"Оплата тарифа:\n👉 {link}\n\n"
            "После оплаты мы сразу начинаем настройку.\n"
            "Обычно запуск занимает 1 день.\n\n"
            "После оплаты нажмите «Я оплатил» 👍",
            reply_markup=ReplyKeyboardMarkup([["Я оплатил"], ["К тарифам"]], resize_keyboard=True)
        )

        chat_id = update.effective_chat.id

        context.job_queue.run_once(payment_reminder, 6 * 3600, chat_id=chat_id, data=6)
        context.job_queue.run_once(payment_reminder, 24 * 3600, chat_id=chat_id, data=24)
        context.job_queue.run_once(payment_reminder, 48 * 3600, chat_id=chat_id, data=48)

        return

    # fallback
    await update.message.reply_text("Пожалуйста, используйте кнопки ниже 👇")


# ---------------- ЗАПУСК ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
