from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
        "🤳 Надішли селфі — поставлю діагноз!\n\n"
        "⚙️ Використовуй команду /menu, щоб обрати версію бота (Сэр бирбот або Олдскул бирбот)!"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_mode = await database.get_user_mode(user_id)
    
    # Format message with styling
    mode_text = "🎩 *Сэр бирбот*" if current_mode == "sir" else "🍺 *Олдскул бирбот*"
    
    text = (
        "⚙️ *Налаштування версії бота*\n\n"
        f"Поточний активний режим: {mode_text}\n\n"
        "Оберіть бажану версію:\n"
        "🎩 *Сэр бирбот* — вишуканий англійський лорд, що критикує з витонченим сарказмом джентльмена, без грубощів.\n"
        "🍺 *Олдскул бирбот* — класичний, прямий та нещадний барний критик із гострим слівцем."
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🎩 Сэр бирбот", callback_data="set_mode_sir"),
            InlineKeyboardButton("🍺 Олдскул бирбот", callback_data="set_mode_oldschool")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data == "set_mode_sir":
        new_mode = "sir"
        mode_text = "🎩 *Сэр бирбот*"
    elif data == "set_mode_oldschool":
        new_mode = "oldschool"
        mode_text = "🍺 *Олдскул бирбот*"
    else:
        return
        
    await database.set_user_mode(user_id, new_mode)
    
    text = (
        "⚙️ *Налаштування версії бота*\n\n"
        f"Поточний активний режим: {mode_text}\n\n"
        "Оберіть бажану версію:\n"
        "🎩 *Сэр бирбот* — вишуканий англійський лорд, що критикує з витонченим сарказмом джентльмена, без грубощів.\n"
        "🍺 *Олдскул бирбот* — класичний, прямий та нещадний барний критик із гострим слівцем."
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🎩 Сэр бирбот", callback_data="set_mode_sir"),
            InlineKeyboardButton("🍺 Олдскул бирбот", callback_data="set_mode_oldschool")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

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

    # Retrieve bot mode
    bot_mode = await database.get_user_mode(user.id)

    # Check if this is a selfie
    caption = (update.message.caption or "").lower()
    selfie_keywords = ["селфі", "selfie", "я ", "мене", "моє фото", "дивись на мене"]
    is_selfie = any(kw in caption for kw in selfie_keywords)

    if is_selfie:
        # Sobriety analysis for selfie
        await update.message.reply_chat_action("typing")
        result = await ai_service.analyze_sobriety_from_selfie(raw_bytes, user_name, bot_mode=bot_mode)
        header = "🔬 *АНАЛІЗ ТВЕРЕЗОСТІ*" if bot_mode == "sir" else "🔬 *ДІАГНОЗ ТВЕРЕЗОСТІ*"
        await update.message.reply_text(f"{header}\n\n{result}", parse_mode="Markdown")
        return

    # Regular drink photo flow
    todays_comments = await database.get_todays_comments()
    ai_comment, is_alcoholic = await ai_service.analyze_drink(raw_bytes, todays_comments, bot_mode=bot_mode)
    
    if not is_alcoholic:
        try:
            await update.message.set_reaction(reaction="🤢" if bot_mode == "sir" else "🤮")
        except Exception:
            pass

    await database.add_drink(user.id, user_name, ai_comment=ai_comment)
    count = await database.get_user_stats(user.id)

    if bot_mode == "sir":
        suffix = f"(Це ваша {count}-а порція напою в моєму записнику.)"
    else:
        suffix = f"(Це твій {count}-й напій у моєму списку!)"

    await update.message.reply_text(
        f"{ai_comment}\n\n"
        f"{suffix}"
    )

    # Every 7 drinks — roast the sommelier and award a title
    if count % 7 == 0:
        await update.message.reply_chat_action("typing")
        roast = await ai_service.analyze_sommelier_collection(count, user_name, bot_mode=bot_mode)
        header = f"🏅 *МОМЕНТ ІСТИНИ, {user_name.upper()}!*"
        if bot_mode == "sir":
            header = f"🎖 *УРОЧИСТЕ ПРИСВОЄННЯ ТИТУЛУ, {user_name.upper()}!*"
        await update.message.reply_text(
            f"{header}\n\n{roast}",
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

    bot_mode = await database.get_user_mode(user.id)

    result = await ai_service.analyze_sobriety_from_audio(voice_bytes.read(), user_name, bot_mode=bot_mode)
    header = f"🔬 *КЛІНІЧНИЙ АНАЛІЗ ТВЕРЕЗОСТІ* — {user_name}" if bot_mode == "sir" else f"🔬 *АНАЛІЗ ТВЕРЕЗОСТІ* — {user_name}"
    await update.message.reply_text(
        f"{header}\n\n{result}",
        parse_mode="Markdown"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_mode = await database.get_user_mode(update.effective_user.id)
    if bot_mode == "sir":
        await update.message.reply_text("Я був би вельми вдячний, якби ви надіслали фотознімок вашого благородного напою. 📸")
    else:
        await update.message.reply_text("Краще надішли фото пива! 📸")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_users = await database.get_top_users()
    bot_mode = await database.get_user_mode(update.effective_user.id)
    if not top_users:
        if bot_mode == "sir":
            await update.message.reply_text("На превеликий жаль, ніхто ще не задокументував свої дегустації. Станьте першим першопрохідцем! 🍺")
        else:
            await update.message.reply_text("Поки що ніхто нічого не пив. Будь першим! 🍺")
        return

    if bot_mode == "sir":
        text = "🏆 Реєстр поважних дегустаторів:\n\n"
        for i, (username, count) in enumerate(top_users, 1):
            text += f"{i}. Вельмишановний {username}: {count} дегустацій\n"
    else:
        text = "🏆 Топ сомельє:\n\n"
        for i, (username, count) in enumerate(top_users, 1):
            text += f"{i}. {username}: {count} порцій\n"

    await update.message.reply_text(text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    count = await database.get_user_stats(user.id)
    bot_mode = await database.get_user_mode(user.id)

    if count == 0:
        if bot_mode == "sir":
            await update.message.reply_text("Ви ще не зволили розділити дегустацію зі мною. Надішліть, будь ласка, фото напою! 🍻")
        else:
            await update.message.reply_text("Ти ще нічого не пив зі мною. Надішли фото напою! 🍻")
    else:
        if bot_mode == "sir":
            await update.message.reply_text(f"📊 Ваша шляхетна статистика, пане {user.username or user.first_name}:\n\nКількість задокументованих дегустацій: {count} 🍺")
        else:
            await update.message.reply_text(f"📊 Твоя статистика, {user.username or user.first_name}:\n\nВипито порцій: {count} 🍺")

