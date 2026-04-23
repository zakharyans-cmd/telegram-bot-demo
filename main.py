import os
import gspread
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 509239406

# --- GOOGLE SHEETS (CRM) ---
# нужен service_account json (подключим потом если надо)
# пока просто структура
def save_to_sheet(data):
    try:
        gc = gspread.service_account(filename="credentials.json")
        sh = gc.open("Leads")
        worksheet = sh.sheet1
        worksheet.append_row([
            data.get("tariff"),
            data.get("name"),
            data.get("business"),
            data.get("status")
        ])
    except:
        pass


# --- МЕНЮ ---
keyboard = [
    ["🥉 Старт 30k"],
    ["🥈 Рост 40k"],
    ["🥇 Агентство 60k"]
]

menu = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# --- ДОДЖИМ (6 / 24 / 48 часов) ---
async def remind_6h(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        context.job.chat_id,
        "👋 Напоминание: вы смотрели настройку системы.\n\nЕсли актуально — можем запустить сегодня."
    )

async def remind_24h(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        context.job.chat_id,
        "⏳ Всё ещё актуально?\n\nСистема может уже принимать заявки за вас."
    )

async def remind_48h(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        context.job.chat_id,
        "📌 Последнее напоминание\n\nЕсли хотите — могу запустить систему сегодня."
    )


# --- СТАРТ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "🚀 Мы настраиваем систему продаж для бизнеса:\n\n"
        "— заявки 24/7\n"
        "— автоматизация\n"
        "— рост конверсии\n\n"
        "👇 Выберите уровень:",
        reply_markup=menu
    )


# --- ОБРАБОТЧИК ---
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # --- 30K ---
    if text == "🥉 Старт 30k":
        context.user_data.update({
            "tariff": "30k",
            "level": "basic",
            "status": "new"
        })

        await update.message.reply_text(
            "🥉 БАЗОВАЯ СИСТЕМА\n\n"
            "✔ заявки в Telegram\n"
            "✔ быстрый запуск\n\n"
            "Как вас зовут?",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["step"] = "name"
        return

    # --- 40K ---
    if text == "🥈 Рост 40k":
        context.user_data.update({
            "tariff": "40k",
            "level": "growth",
            "status": "new"
        })

        await update.message.reply_text(
            "🥈 СИСТЕМА РОСТА\n\n"
            "✔ заявки + автоответ\n"
            "✔ выше конверсия\n\n"
            "Как вас зовут?",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["step"] = "name"
        return

    # --- 60K ---
    if text == "🥇 Агентство 60k":
        context.user_data.update({
            "tariff": "60k",
            "level": "agency",
            "status": "new"
        })

        await update.message.reply_text(
            "🥇 АГЕНТСКАЯ СИСТЕМА\n\n"
            "✔ CRM-логика\n"
            "✔ контроль заявок\n"
            "✔ максимальная конверсия\n\n"
            "Как вас зовут?",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["step"] = "name"
        return


    # --- ИМЯ ---
    if context.user_data.get("step") == "name":
        context.user_data["name"] = text
        context.user_data["step"] = "business"

        await update.message.reply_text("Чем вы занимаетесь?")
        return


    # --- ФИНАЛ / ОПЛАТА ---
    if context.user_data.get("step") == "business":
        context.user_data["business"] = text

        data = context.user_data

        # CRM сохранение
        save_to_sheet(data)

        # уведомление тебе
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🔥 НОВЫЙ ЛИД\n\n"
                f"Тариф: {data['tariff']}\n"
                f"Имя: {data['name']}\n"
                f"Бизнес: {data['business']}\n"
                f"Статус: {data['status']}"
            )
        )

        await update.message.reply_text(
            "🔥 Отлично, я всё понял.\n\n"
            "Я могу запустить систему для вашего бизнеса.\n\n"
            "💳 Оплата:\n"
            "По ссылке или переводом (будет подключено через кассу)\n\n"
            "После оплаты нажмите 👇",
            reply_markup=ReplyKeyboardMarkup([["💰 Я оплатил"]], resize_keyboard=True)
        )

        # запуск дожима
        job = context.job_queue
        job.run_once(remind_6h, 21600, chat_id=update.effective_chat.id)
        job.run_once(remind_24h, 86400, chat_id=update.effective_chat.id)
        job.run_once(remind_48h, 172800, chat_id=update.effective_chat.id)

        context.user_data["step"] = "done"
        return


    # --- ОПЛАТА (НЕ ФЕЙК) ---
    if text == "💰 Я оплатил":
        context.user_data["status"] = "pending_payment"

        await update.message.reply_text(
            "👍 Спасибо!\n\n"
            "Я получил уведомление об оплате.\n"
            "Сейчас проверю поступление и начну настройку."
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="💰 КЛИЕНТ НАЖАЛ 'Я ОПЛАТИЛ' (нужно проверить)"
        )


# --- ЗАПУСК ---
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
