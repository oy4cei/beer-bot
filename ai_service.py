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
        return "Ех, мої нейронні мережі відключені. Не можу розгледіти, що там. Але впевнений, це щось смачне! (API Key missing)"

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
                "Ти — цинічний, зухвалий і дуже гострий на язик барний критик. Твоє завдання — жорстко просмажити вибір напою на фото. "
                "1. УВАЖНО подивися на фото. Знайди назву бренду, тип напою, закуску або обстановку. "
                "2. Якщо ти бачиш конкретний бренд — ОБОВ'ЯЗКОВО згадай його і знайди привід для стьобу. "
                "3. Твій стиль — це суміш стендапу і народної мудрості. Використовуй рідкісні та колоритні лайки. "
                f"Ось приклади виразів, які ти повинен використовувати: {selected_insults}. "
                "4. Не використовуй нудні фрази. Будь креативним, злим, але смішним. "
                "Відповідь має бути українською мовою, короткою (1-3 речення) і унікальною для цього фото."
            )
        elif rand_val < 0.9:
             # Ukrainian Insults Mode (20%)
             selected_insults = ", ".join(random.sample(UKRAINIAN_INSULTS, 3))
             prompt = (
                "Ти — цинічний, зухвалий і дуже гострий на язик барний критик. Твоє завдання — жорстко просмажити вибір напою на фото. "
                "1. УВАЖНО подивися на фото. Знайди назву бренду, тип напою, закуску або обстановку. "
                "2. Якщо ти бачиш конкретний бренд — ОБОВ'ЯЗКОВО згадай його і знайди привід для стьобу. "
                "3. Твій стиль — це суміш стендапу і народної мудрості. Використовуй українські лайки та прокльони для колориту. "
                f"Ось приклади виразів, які ти можеш використовувати (але не обмежуйся ними): {selected_insults}. "
                "4. Не використовуй нудні фрази типу 'хороший вибір'. "
                "Відповідь має бути українською мовою (з вкрапленнями українських лайок), короткою (1-3 речення) і унікальною для цього фото."
            )
        else:
             # Praise Mode (10%)
             from comments import PRAISE_COMMENTS
             selected_praise = random.choice(PRAISE_COMMENTS)
             prompt = (
                "Ти — захоплений, емоційний і трохи божевільний фанат алкоголю. Твоє завдання — розхвалити напій на фото до небес! "
                "1. УВАЖНО подивися на фото. Знайди найкращі риси напою (колір, піну, бренд) і захоплюйся ними. "
                "2. Твій стиль — це нестримний захват, капс і емодзі. Ти буквально плачеш від краси. "
                f"Почни свою відповідь або використовуй всередині цю фразу: '{selected_praise}'. "
                "3. Придумай неймовірні, космічні епітети. Порівнюй напій з божественним нектаром. "
                "4. Ігноруй будь-які недоліки. Для тебе це — ідеал. "
                "Відповідь має бути українською мовою, емоційною, короткою (1-3 речення) і сповненою любові."
            )

        generation_config = genai.types.GenerationConfig(
            temperature=1.0,  # Increase creativity
        )

        response = model.generate_content([prompt, image], generation_config=generation_config)
        print(f"AI Response: {response.text}") # Log the response
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return "Щось у мене в очах помутніло... Не можу розгледіти етикетку. Напевно, палене!"
