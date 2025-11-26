import os
import google.generativeai as genai
from PIL import Image
import io

# Configure Gemini
def configure_ai():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not set.")
        return False
    genai.configure(api_key=api_key)
    return True

import random
from insults import INSULTS

# ... (configure_ai function remains the same)

async def analyze_drink(photo_bytes):
    if not configure_ai():
        return "Эх, мои нейронные сети отключены. Не могу разглядеть, что там. Но уверен, это что-то вкусное! (API Key missing)"

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Select a few random insults to inject into the context
        selected_insults = ", ".join(random.sample(INSULTS, 3))
        
        prompt = (
            "Ты — циничный, дерзкий и очень острый на язык барный критик. Твоя задача — жестко прожарить выбор напитка на фото. "
            "1. ВНИМАТЕЛЬНО посмотри на фото. Найди название бренда, тип напитка, закуску или обстановку. "
            "2. Если ты видишь конкретный бренд — ОБЯЗАТЕЛЬНО упомяни его и найди повод для стеба. "
            "3. Твой стиль — это смесь стендапа и народной мудрости. Используй украинские ругательства и проклятия для колорита. "
            f"Вот примеры выражений, которые ты можешь использовать (но не ограничивайся ими): {selected_insults}. "
            "4. Не используй скучные фразы типа 'хороший выбор'. "
            "Если это лагер — пошути про воду из лужи. Если стаут — про мазут. Если IPA — про освежитель воздуха. "
            "Если это водка — спроси, не страшно ли ослепнуть. "
            "Будь креативным, злым, но смешным. "
            "Ответ должен быть на русском языке (с вкраплениями украинских ругательств), коротким (1-3 предложения) и уникальным для этого фото."
        )

        generation_config = genai.types.GenerationConfig(
            temperature=1.0,  # Increase creativity
        )

        response = model.generate_content([prompt, image], generation_config=generation_config)
        print(f"AI Response: {response.text}") # Log the response
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return "Что-то у меня в глазах помутнело... Не могу разглядеть этикетку. Наверное, паленое!"
