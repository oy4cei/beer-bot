import os
import asyncio
import google.generativeai as genai
from PIL import Image
import io
import random
from insults import UKRAINIAN_INSULTS, SPECIAL_INSULTS

AI_CONFIGURED = False

# Configure Gemini
def configure_ai():
    global AI_CONFIGURED
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not set.")
        return False
    genai.configure(api_key=api_key)
    AI_CONFIGURED = True
    return True

async def analyze_drink(photo_bytes):
    if not AI_CONFIGURED:
        return "Ех, мої нейронні мережі відключені. Не можу розгледіти, що там. Але впевнений, це щось смачне! (API Key missing)"

    try:
        
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Determine mode based on probability
        # 0.0 - 0.6: Special Insults (60%)
        # 0.6 - 0.8: Ukrainian Insults (20%)
        # 0.8 - 0.9: Praise (10%)
        # 0.9 - 1.0: Love Declaration Song Lyrics (10%)
        
        rand_val = random.random()
        
        if rand_val < 0.6:
             # Special Insults Mode (60%)
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
        elif rand_val < 0.8:
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
        elif rand_val < 0.9:
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
        else:
             # Love Declaration Song Lyrics (10%)
             from comments import LOVE_SONG_LYRICS
             prompt = (
                "Ти — палкий, романтичний поет-алкоголік, і ти освідчуєшся в коханні алкогольному напою на фото. "
                "1. УВАЖНО подивися на фото і розпізнай напій (пиво, горілка, вино тощо). "
                "2. Напиши палке зізнання в любові саме цьому напою, використовуючи рядки з пісні Ницо Потворно 'Ти'. "
                "3. ОБОВ'ЯЗКОВО органічно інтегруй 1-2 найяскравіші фрази чи рядки з цього тексту в своє зізнання: "
                f"\\n{LOVE_SONG_LYRICS}\\n"
                "4. Відповідь має бути українською мовою, 2-4 речення, сповнена пристрасті до напою."
            )

        generation_config = genai.types.GenerationConfig(
            temperature=1.0,  # Increase creativity
        )

        max_retries = 3
        base_delay = 5
        
        for attempt in range(max_retries):
            try:
                # Use gemini-1.5-flash for much higher Free Tier quota (15 RPM, 1500 RPD)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = await model.generate_content_async([prompt, image], generation_config=generation_config)
                print(f"AI Response: {response.text}") # Log the response
                return response.text
            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "resource" in error_str or "exhausted" in error_str or "too many" in error_str or "quota" in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limit hit, retrying in {delay} seconds (attempt {attempt + 1}/{max_retries})...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        print("Max retries reached for 429 Rate Limit.")
                        return "Ой, забагато запитів! Дай мені хвилинку перевести подих... (API Rate Limit 429)"
                else:
                    print(f"AI Error: {e}")
                    return "Щось у мене в очах помутніло... Не можу розгледіти етикетку. Напевно, палене!"
                    
        return "Щось пішло не так..."
    except Exception as e:
        print(f"AI Error: {e}")
        return "Щось у мене в очах помутніло... Не можу розгледіти етикетку. Напевно, палене!"

