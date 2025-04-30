# handlers.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
from config import CHANNEL_ID
from keyboard import main_menu_keyboard, back_to_main_keyboard, back_to_amount_keyboard

CHOOSE_TYPE, SELECT_SUM, UPLOAD_PHOTO = range(3)

user_data = {}
transactions = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo="https://i.imgur.com/0bnQ1og.jpeg",
        caption="💬 Выберите тип оплаты:",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSE_TYPE

async def handle_payment_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_main":
        await query.message.delete()
        await query.message.chat.send_photo(
            photo="https://i.imgur.com/0bnQ1og.jpeg",
            caption="💬 Выберите тип оплаты:",
            reply_markup=main_menu_keyboard()
        )
        return CHOOSE_TYPE

    payment_type = query.data.replace("payment_", "")
    user_data[query.from_user.id] = {"type": payment_type}
    await query.message.delete()
    await query.message.chat.send_photo(
        photo="https://i.imgur.com/Wo5q3QU.jpeg",
        caption=(
            f"*💳 Тип оплаты:* {payment_type}\n\n"
            f"💬 Введите сумму в чат или измените способ оплаты"
        ),
        reply_markup=back_to_main_keyboard(),
        parse_mode="Markdown"
    )
    return SELECT_SUM

async def handle_sum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if not text.replace('.', '', 1).isdigit():
        await update.message.reply_text("❗ Пожалуйста, введите корректную сумму.")
        return SELECT_SUM

    user_data[user_id]["sum"] = float(text)
    payment_type = user_data[user_id]["type"]
    amount = user_data[user_id]["sum"]
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    await update.message.chat.send_photo(
        photo="https://i.imgur.com/tIYn2ye.jpeg",
        caption=(
            f"*🗓 {now}*\n\n"
            f"*💳 Тип оплаты:* {payment_type}\n"
            f"*💰 Сумма:* {amount} ₽\n\n"
            f"🖼 Прикрепите фото чека для завершения"
        ),
        reply_markup=back_to_amount_keyboard(),
        parse_mode="Markdown"
    )
    return UPLOAD_PHOTO

async def back_to_sum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = user_data.get(user_id)

    if not data:
        await query.message.edit_text("⚠️ Нет данных. Начните сначала /start")
        return ConversationHandler.END

    payment_type = data.get("type", "❓")
    await query.message.delete()
    await query.message.chat.send_photo(
        photo="https://i.imgur.com/Wo5q3QU.jpeg",
        caption=(
            f"*💳 Тип оплаты:* {payment_type}\n\n"
            f"💬 Введите сумму в чат или измените способ оплаты"
        ),
        reply_markup=back_to_main_keyboard(),
        parse_mode="Markdown"
    )
    return SELECT_SUM # комм

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1].file_id
    data = user_data.get(user_id)

    if not data:
        await update.message.reply_text("⚠️ Что-то пошло не так. Попробуйте снова с команды /start.")
        return ConversationHandler.END

    if data["type"] not in ["QR", "Terminal"]:
        await update.message.reply_text("⚠️ Ошибка: неизвестный тип оплаты. Начните сначала с /start.")
        return ConversationHandler.END

    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    transactions.append({
        "date": datetime.now().date(),
        "type": data["type"],
        "sum": data["sum"]
    })

    caption = (
        f"*🗓 {now}*\n\n"
        f"*💳 Тип оплаты:* {data['type']}\n"
        f"*💰 Сумма:* {data['sum']} ₽"
    )
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=caption, parse_mode="Markdown")
    await update.message.reply_text("✅ Чек отправлен.", reply_markup=main_menu_keyboard())
    return CHOOSE_TYPE

async def handle_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().date()
    summary = {"QR": 0, "Terminal": 0}

    for entry in transactions:
        if entry["date"] == today and entry["type"] in summary:
            summary[entry["type"]] += entry["sum"]

    text = (
        f"*📊 Общий итог за {today.strftime('%d.%m.%Y')}*\n\n"
        f"*🧾 QR:* {summary['QR']} ₽\n"
        f"*💳 Терминал:* {summary['Terminal']} ₽"
    )

    query = update.callback_query
    await query.answer()
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
    return ConversationHandler.END