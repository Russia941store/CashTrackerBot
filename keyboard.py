# keyboard.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def select_point_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏪 Тихвин", callback_data="point_Tikhvin")],
        [InlineKeyboardButton("🏢 Радищева", callback_data="point_Radischeva")]
    ])

def payment_options_keyboard(point):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧾 QR", callback_data="payment_QR")],
        [InlineKeyboardButton("💳 Терминал", callback_data="payment_Terminal")],
        [InlineKeyboardButton("🧬 MinionPay", callback_data="payment_MinionPay")],
        [InlineKeyboardButton("📊 Общий итог за день", callback_data="summary")],
        [InlineKeyboardButton("🔁 Изменить точку продаж", callback_data="back_to_point")]
    ])

def back_to_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Изменить способ оплаты", callback_data="back_main")]
    ])

def back_to_amount_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔢 Изменить сумму оплаты", callback_data="back_amount")],
        [InlineKeyboardButton("⬅️ Главное меню", callback_data="back_to_point")]
    ])