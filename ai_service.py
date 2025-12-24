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
from insults import UKRAINIAN_INSULTS, SPECIAL_INSULTS

# ... (configure_ai function remains the same)

async def analyze_drink(photo_bytes):
    if not configure_ai():
        return "Эх, мои нейронные сети отключены. Не могу разглядеть, что там. Но уверен, это что-то вкусное! (API Key missing)"

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Determine mode based on probability
        # 0.0 - 0.7: Special Insults (70%)
        # 0.7 - 0.9: Ukrainian Insults (20%)
        # 0.9 - 1.0: Praise (10%)
        
        rand_val = random.random()
        
        if rand_val < 0.7:
             # Special Insults Mode (70%)
             selected_insults = ", ".join(random.sample(SPECIAL_INSULTS, 3))
             prompt = (
                "Ты — циничный, дерзкий и очень острый на язык барный критик. Твоя задача — жестко прожарить выбор напитка на фото. "
                "1. ВНИМАТЕЛЬНО посмотри на фото. Найди название бренда, тип напитка, закуску или обстановку. "
                "2. Если ты видишь конкретный бренд — ОБЯЗАТЕЛЬНО упомяни его и найди повод для стеба. "
                "3. Твой стиль — это смесь стендапа и народной мудрости. Используй редкие и колоритные ругательства. "
                f"Вот примеры выражений, которые ты должен использовать: {selected_insults}. "
                "4. Не используй скучные фразы. Будь креативным, злым, но смешным. "
                "Ответ должен быть на русском языке, коротким (1-3 предложения) и уникальным для этого фото."
            )
        elif rand_val < 0.9:
             # Ukrainian Insults Mode (20%)
             selected_insults = ", ".join(random.sample(UKRAINIAN_INSULTS, 3))
             prompt = (
                "Ты — циничный, дерзкий и очень острый на язык барный критик. Твоя задача — жестко прожарить выбор напитка на фото. "
                "1. ВНИМАТЕЛЬНО посмотри на фото. Найди название бренда, тип напитка, закуску или обстановку. "
                "2. Если ты видишь конкретный бренд — ОБЯЗАТЕЛЬНО упомяни его и найди повод для стеба. "
                "3. Твой стиль — это смесь стендапа и народной мудрости. Используй украинские ругательства и проклятия для колорита. "
                f"Вот примеры выражений, которые ты можешь использовать (но не ограничивайся ими): {selected_insults}. "
                "4. Не используй скучные фразы типа 'хороший выбор'. "
                "Ответ должен быть на русском языке (с вкраплениями украинских ругательств), коротким (1-3 предложения) и уникальным для этого фото."
            )
        else:
             # Praise Mode (10%)
             from comments import PRAISE_COMMENTS
             selected_praise = random.choice(PRAISE_COMMENTS)
             prompt = (
                "Ты — восторженный, эмоциональный и немного сумасшедший фанат алкоголя. Твоя задача — восхвалить напиток на фото до небес! "
                "1. ВНИМАТЕЛЬНО посмотри на фото. Найди лучшие черты напитка (цвет, пену, бренд) и восторгайся ими. "
                "2. Твой стиль — это безудержный восторг, капс и эмодзи. Ты буквально плачешь от красоты. "
                f"Начни свой ответ или используй внутри эту фразу: '{selected_praise}'. "
                "3. Придумай невероятные, космические эпитеты. Сравнивай напиток с божественным нектаром. "
                "4. Игнорируй любые недостатки. Для тебя это — идеал. "
                "Ответ должен быть на русском языке, эмоциональным, коротким (1-3 предложения) и полным любви."
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
