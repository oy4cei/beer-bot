import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import database
import handlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # Initialize database
    database.init_db()
    
    # Get token from environment variable or ask user to set it
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN environment variable not set.")
        return

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(MessageHandler(filters.PHOTO, handlers.handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
