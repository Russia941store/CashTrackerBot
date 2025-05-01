from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.helpers import escape_markdown
from datetime import datetime, timedelta
from config import CHANNEL_ID, MINION_CHANNEL_ID
from keyboard import (
    select_point_keyboard,
    payment_options_keyboard,
    back_to_main_keyboard,
    back_to_amount_keyboard,
)

SELECT_POINT, CHOOSE_TYPE, SELECT_SUM, UPLOAD_PHOTO = range(4)

user_data = {}
transactions = []

def get_now():
    return datetime.utcnow() + timedelta(hours=5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo="https://i.imgur.com/NwMaRuo.jpeg",
        caption="🏬 *Выберите точку продаж:*",
        reply_markup=select_point_keyboard(),
        parse_mode="Markdown"
    )
    return SELECT_POINT

async def handle_point_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "point_Tikhvin":
        point = "Тихвин"
    elif query.data == "point_Radishcheva":
        point = "Радищева"
    else:
        point = "❓"

    user_data[query.from_user.id] = {"point": point}

    await query.message.delete()
    await query.message.chat.send_photo(
        photo="https://i.imgur.com/0bnQ1og.jpeg",
        caption=f"🏬 *Точка продаж:* {escape_markdown(point)}\n\n💬 Выберите способ оплаты:",
        reply_markup=payment_options_keyboard(point),
        parse_mode="Markdown"
    )
    return CHOOSE_TYPE

async def handle_payment_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "back_to_point":
        await query.message.delete()
        await query.message.chat.send_photo(
            photo="https://i.imgur.com/NwMaRuo.jpeg",
            caption="🏬 *Выберите точку продаж:*",
            reply_markup=select_point_keyboard(),
            parse_mode="Markdown"
        )
        return SELECT_POINT

    payment_type = query.data.replace("payment_", "")
    user_data[user_id]["type"] = payment_type
    point = user_data[user_id].get("point", "❓")

    await query.message.delete()
    await query.message.chat.send_photo(
        photo="https://i.imgur.com/Wo5q3QU.jpeg",
        caption=(
            f"*🏬 Точка продаж:* {escape_markdown(point)}\n"
            f"*💳 Тип оплаты:* {escape_markdown(payment_type)}\n\n"
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
    point = user_data[user_id]["point"]
    amount = user_data[user_id]["sum"]
    now = get_now().strftime("%d.%m.%Y %H:%M")

    await update.message.chat.send_photo(
        photo="https://i.imgur.com/tIYn2ye.jpeg",
        caption=(
            f"*🗓 {now}*\n\n"
            f"*🏬 Точка продаж:* {escape_markdown(point)}\n"
            f"*💳 Тип оплаты:* {escape_markdown(payment_type)}\n"
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

    point = data.get("point", "❓")
    payment_type = data.get("type", "❓")

    await query.message.delete()
    await query.message.chat.send_photo(
        photo="https://i.imgur.com/Wo5q3QU.jpeg",
        caption=(
            f"*🏬 Точка продаж:* {escape_markdown(point)}\n"
            f"*💳 Тип оплаты:* {escape_markdown(payment_type)}\n\n"
            f"💬 Введите сумму в чат или измените способ оплаты"
        ),
        reply_markup=back_to_main_keyboard(),
        parse_mode="Markdown"
    )
    return SELECT_SUM

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1].file_id
    data = user_data.get(user_id)

    if not data:
        await update.message.reply_text("⚠️ Что-то пошло не так. Попробуйте снова с команды /start.")
        return ConversationHandler.END

    now = get_now()
    now_str = now.strftime("%d.%m.%Y %H:%M")

    transactions.append({
        "date": now.date(),
        "type": data["type"],
        "sum": data["sum"],
        "point": data["point"]
    })

    if data["type"] == "MinionPay":
        short_point = "T" if data["point"] == "Тихвин" else "R"
        caption = (
            f"*🗓 {now_str}*\n\n"
            f"*📍 Точка:* {short_point}\n"
            f"*💳 Тип оплаты:* {escape_markdown(data['type'])}\n"
            f"*💰 Сумма:* {data['sum']} ₽\n"
        )
        await context.bot.send_photo(
            chat_id=MINION_CHANNEL_ID,
            photo=photo,
            caption=caption,
            parse_mode="Markdown"
        )
    else:
        caption = (
            f"*🗓 {now_str}*\n\n"
            f"*🏬 Точка продаж:* {escape_markdown(data['point'])}\n"
            f"*💳 Тип оплаты:* {escape_markdown(data['type'])}\n"
            f"*💰 Сумма:* {data['sum']} ₽"
        )
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photo,
            caption=caption,
            parse_mode="Markdown"
        )

    await update.message.chat.send_photo(
        photo="https://i.imgur.com/NwMaRuo.jpeg",
        caption="✅ Чек успешно отправлен!\n\n🏬 *Выберите точку продаж:*",
        reply_markup=select_point_keyboard(),
        parse_mode="Markdown"
    )
    return SELECT_POINT

async def handle_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    user_point = user_data.get(user_id, {}).get("point")

    today = get_now().date()
    summary = {"QR": 0, "Terminal": 0, "MinionPay": 0}

    for entry in transactions:
        if entry["date"] == today and entry["point"] == user_point:
            summary[entry["type"]] += entry["sum"]

    text = (
        f"*📊 Общий итог за {today.strftime('%d.%m.%Y')}*\n\n"
        f"*🏬 Точка:* {escape_markdown(user_point)}\n\n"
        f"*🧾 QR:* {summary['QR']} ₽\n"
        f"*💳 Терминал:* {summary['Terminal']} ₽\n"
        f"*🧬 MinionPay:* {summary['MinionPay']} ₽"
    )

    query = update.callback_query
    await query.answer()
    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo="https://i.imgur.com/D8YKlfV.jpeg",
        caption=text,
        parse_mode="Markdown"
    )
    return ConversationHandler.END