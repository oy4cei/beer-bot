from telegram import Update
from telegram.ext import ContextTypes
import database
import comments
import ai_service
import io

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Я Пивний Бот. 🍺\n"
        "Надішли мені фото свого напою, і я його врахую!\n"
        "Також можеш подивитися /top і /stats."
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
    try:
        await update.message.set_reaction(reaction="👀")
    except Exception:
        pass
    
    # Get AI comment
    ai_comment = await ai_service.analyze_drink(photo_bytes.read())
    
    await database.add_drink(user.id, user.username or user.first_name)
    count = await database.get_user_stats(user.id)
    
    await update.message.reply_text(
        f"{ai_comment}\n\n"
        f"(Це твій {count}-й напій у моєму списку!)"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Краще надішли фото пива! 📸")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_users = await database.get_top_users()
    if not top_users:
        await update.message.reply_text("Поки що ніхто нічого не пив. Будь першим! 🍺")
        return
    
    text = "🏆 Топ сомельє:\n\n"
    for i, (username, count) in enumerate(top_users, 1):
        text += f"{i}. {username}: {count} порцій\n"
        
    await update.message.reply_text(text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    count = await database.get_user_stats(user.id)
    
    if count == 0:
        await update.message.reply_text("Ти ще нічого не пив зі мною. Надішли фото напою! 🍻")
    else:
        await update.message.reply_text(f"📊 Твоя статистика, {user.username or user.first_name}:\n\nВипито порцій: {count} 🍺")
