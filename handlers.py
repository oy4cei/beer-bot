from telegram import Update
from telegram.ext import ContextTypes
import database
import comments
import ai_service
import io

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Пивной Бот. 🍺\n"
        "Пришли мне фото своего напитка, и я его учту!"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo_file = await update.message.photo[-1].get_file()
    
    # Download photo to memory
    photo_bytes = io.BytesIO()
    await photo_file.download_to_memory(photo_bytes)
    photo_bytes.seek(0)
    
    # Notify user that we are thinking
    await update.message.reply_chat_action("typing")
    
    # Get AI comment
    ai_comment = await ai_service.analyze_drink(photo_bytes.read())
    
    database.add_drink(user.id, user.username or user.first_name)
    count = database.get_user_stats(user.id)
    
    await update.message.reply_text(
        f"{ai_comment}\n\n"
        f"(Это твой {count}-й напиток в моем списке!)"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Лучше пришли фото пива! 📸")
