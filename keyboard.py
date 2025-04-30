# keyboard.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧾 QR", callback_data="payment_QR")],
        [InlineKeyboardButton("💳 Терминал", callback_data="payment_Terminal")],
        [InlineKeyboardButton("📊 Общий итог за день", callback_data="summary")]
    ])

def back_to_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Изменить способ оплаты", callback_data="back_main")]
    ])

def back_to_amount_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔢 Изменить сумму оплаты", callback_data="back_amount")],
        [InlineKeyboardButton("⬅️ Главное меню", callback_data="back_main")]
    ])