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
        "Також можеш подивитися /top і /stats.\n\n"
        "🎤 Надішли голосове — оціню твою тверезість!\n"
        "🤳 Надішли селфі — поставлю діагноз!"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = user.username or user.first_name
    photo_file = await update.message.photo[-1].get_file()

    # Download photo to memory
    photo_bytes = io.BytesIO()
    await photo_file.download_to_memory(photo_bytes)
    photo_bytes.seek(0)
    raw_bytes = photo_bytes.read()

    # Notify user that we are thinking
    await update.message.reply_chat_action("typing")
    try:
        await update.message.set_reaction(reaction="👀")
    except Exception:
        pass

    # Check if this is a selfie (photo sent without caption mentioning drink,
    # or has a face — we use a heuristic: if message has "selfie" or "я" in caption,
    # OR if there's no drink context — detect via AI)
    caption = (update.message.caption or "").lower()
    selfie_keywords = ["селфі", "selfie", "я ", "мене", "моє фото", "дивись на мене"]
    is_selfie = any(kw in caption for kw in selfie_keywords)

    if is_selfie:
        # Sobriety analysis for selfie
        await update.message.reply_chat_action("typing")
        result = await ai_service.analyze_sobriety_from_selfie(raw_bytes, user_name)
        await update.message.reply_text(f"🔬 *ДІАГНОЗ ТВЕРЕЗОСТІ*\n\n{result}", parse_mode="Markdown")
        return

    # Regular drink photo flow
    todays_comments = await database.get_todays_comments()
    ai_comment, is_alcoholic = await ai_service.analyze_drink(raw_bytes, todays_comments)
    
    if not is_alcoholic:
        try:
            await update.message.set_reaction(reaction="🤮")
        except Exception:
            pass

    await database.add_drink(user.id, user_name, ai_comment=ai_comment)
    count = await database.get_user_stats(user.id)

    await update.message.reply_text(
        f"{ai_comment}\n\n"
        f"(Це твій {count}-й напій у моєму списку!)"
    )

    # Every 7 drinks — roast the sommelier and award a title
    if count % 7 == 0:
        await update.message.reply_chat_action("typing")
        roast = await ai_service.analyze_sommelier_collection(count, user_name)
        await update.message.reply_text(
            f"🏅 *МОМЕНТ ІСТИНИ, {user_name.upper()}!*\n\n{roast}",
            parse_mode="Markdown"
        )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = user.username or user.first_name

    await update.message.reply_chat_action("typing")
    try:
        await update.message.set_reaction(reaction="🎤")
    except Exception:
        pass

    # Download voice message
    voice_file = await update.message.voice.get_file()
    voice_bytes = io.BytesIO()
    await voice_file.download_to_memory(voice_bytes)
    voice_bytes.seek(0)

    result = await ai_service.analyze_sobriety_from_audio(voice_bytes.read(), user_name)
    await update.message.reply_text(
        f"🔬 *АНАЛІЗ ТВЕРЕЗОСТІ* — {user_name}\n\n{result}",
        parse_mode="Markdown"
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
