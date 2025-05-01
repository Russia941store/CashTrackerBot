import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from config import BOT_TOKEN
from handlers import (
    start,
    handle_point_choice,
    handle_payment_type,
    handle_sum,
    handle_photo,
    handle_summary,
    back_to_sum
)

SELECT_POINT, CHOOSE_TYPE, SELECT_SUM, UPLOAD_PHOTO = range(4)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def notify_channel_startup(app):
    from config import CHANNEL_ID
    try:
        await app.bot.send_message(chat_id=CHANNEL_ID, text="✅ Бот успешно запущен и подключен к каналу.")
    except Exception as e:
        print(f"❌ Ошибка при отправке в канал: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.post_init = notify_channel_startup

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_POINT: [
                CallbackQueryHandler(handle_point_choice, pattern="^point_")
            ],
            CHOOSE_TYPE: [
                CallbackQueryHandler(handle_payment_type, pattern="^(payment_QR|payment_Terminal|payment_MinionPay|back_to_point)$")
            ],
            SELECT_SUM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sum),
                CallbackQueryHandler(handle_payment_type, pattern="^back_main$")
            ],
            UPLOAD_PHOTO: [
                MessageHandler(filters.PHOTO, handle_photo),
                CallbackQueryHandler(back_to_sum, pattern="^back_amount$"),
                CallbackQueryHandler(handle_payment_type, pattern="^back_main$")
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(handle_summary, pattern="^summary$"))

    print("✅ Бот запущен. Ожидаем команду /start")
    app.run_polling()

if __name__ == "__main__":
    main()