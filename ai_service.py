import os
import asyncio
import google.generativeai as genai
from PIL import Image
import io
import random
import base64
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

        # Safety settings to allow roasting without being blocked
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        max_retries = 3
        base_delay = 5
        
        for attempt in range(max_retries):
            try:
                # Use gemini-3-flash-preview as per Google documentation
                model = genai.GenerativeModel('gemini-3-flash-preview', safety_settings=safety_settings)
                
                # Wrap image in dict for more explicit SDK handling
                content_list = [prompt, {"mime_type": "image/jpeg", "data": photo_bytes}]
                
                response = await model.generate_content_async(content_list, generation_config=generation_config)
                
                # Check if it was blocked
                if not response.candidates:
                    print(f"AI Blocked (no candidates). Feedback: {response.prompt_feedback}")
                    return "Мої нейронні мережі почервоніли від сорому... Щось там дуже відверте або провокаційне на фото! 😉"
                
                print(f"AI Response success: {response.text}") 
                return response.text
            except Exception as e:
                error_str = str(e).lower()
                print(f"AI Error on attempt {attempt+1}: {e}")
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
                    import traceback
                    traceback.print_exc()
                    
                    if "403" in error_str and "leaked" in error_str:
                        return "Ой, мій API ключ забанили через витік! (Помилка 403: Key Leaked). Будь ласка, онови GEMINI_API_KEY у файлі .env."
                        
                    return f"Щось у мене в очах помутніло... (Помилка: {str(e)[:100]})"
                    
        return "Щось пішло не так..."
    except Exception as e:
        print(f"AI Error: {e}")
        return "Щось у мене в очах помутніло... Не можу розгледіти етикетку. Напевно, палене!"


async def analyze_sommelier_collection(drink_count: int, username: str) -> str:
    """Every 3 drinks: sarcastically roast the sommelier's taste and give them a ridiculous title."""
    if not AI_CONFIGURED:
        return "Мій алкогольний ИИ вирубився раніше, ніж ти встиг допити. (API Key missing)"

    try:
        prompt = (
            f"Ти — жорстокий, безжалісний і надзвичайно саркастичний суддя алкогольного смаку. "
            f"Людина на ім'я {username} щойно задокументувала свій {drink_count}-й напій. "
            f"Зроби наступне:\n"
            f"1. Коротко (1-2 речення) висміяй 'ассортимент' цього 'сомельє' — уяви яких покидьків напоїв вони пили судячи з кількості. "
            f"2. НАЙГОЛОВНІШЕ — вигадай для {username} УНІКАЛЬНЕ, ПРИНИЗЛИВЕ ЗВАННЯ, яке відображає їхній 'витончений' смак. "
            f"Звання має бути смішним, образливим і по-справжньому прожарити людину. "
            f"Наприклад: 'Гросмейстер Теплого Пива', 'Лицар Розведеного Вина', 'Архієпископ Дешевої Горілки', 'Барон Протухлого Сидру'. "
            f"Але будь НАБАГАТО креативнішим і жорсткішим! "
            f"3. Оголоси це звання з помпою і сарказмом, наче вручаєш нобелівку лузеру. "
            f"Відповідь має бути українською мовою, 3-5 речень, з емодзі. Будь безжалісним!"
        )

        generation_config = genai.types.GenerationConfig(temperature=1.2)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        model = genai.GenerativeModel('gemini-3-flash-preview', safety_settings=safety_settings)
        response = await model.generate_content_async(prompt, generation_config=generation_config)

        if not response.candidates:
            return "Навіть мій ШІ відмовляється коментувати такий жахливий смак..."

        print(f"Sommelier roast: {response.text}")
        return response.text

    except Exception as e:
        print(f"Sommelier roast error: {e}")
        return f"Мій алкогольний ШІ впав у відчай від твого списку напоїв... (Помилка: {str(e)[:80]})"


async def analyze_sobriety_from_audio(audio_bytes: bytes, username: str) -> str:
    """Analyze voice message to assess sobriety level and give harsh recommendations."""
    if not AI_CONFIGURED:
        return "Мій детектор тверезості відключено. (API Key missing)"

    try:
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

        prompt = (
            f"Ти — безжалісний нарколог-детектив і аналізуєш голосове повідомлення від {username}. "
            f"Твоє завдання — визначити рівень тверезості/сп'яніння цієї людини. "
            f"1. Оціни темп мовлення, дикцію, зв'язність думок, мукання і взагалі все підозріле. "
            f"2. Постав ДІАГНОЗ: шкала від 0 (монах-трезвенник) до 10 (після весілля в селі). "
            f"3. Дай ЖОРСТКІ рекомендації що робити далі. Наприклад: 'ляж спати', 'здай телефон другу', "
            f"'замов таксі і не торкайся до керма', 'пий воду як кит', 'подзвони мамі — хай сміється'. "
            f"4. ВАЖЛИВО: будь саркастичним, смішним, але чесним. Не соромся. "
            f"Відповідь має бути українською мовою, 3-5 речень, з емодзі."
        )

        generation_config = genai.types.GenerationConfig(temperature=1.1)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        model = genai.GenerativeModel('gemini-3-flash-preview', safety_settings=safety_settings)
        content_list = [prompt, {"mime_type": "audio/ogg", "data": audio_bytes}]
        response = await model.generate_content_async(content_list, generation_config=generation_config)

        if not response.candidates:
            return "Навіть мій детектор п'янства розгубився від почутого..."

        print(f"Sobriety audio analysis: {response.text}")
        return response.text

    except Exception as e:
        print(f"Sobriety audio error: {e}")
        # Fallback: just roast without actual audio analysis
        return await _sobriety_fallback(username, "голосового повідомлення")


async def analyze_sobriety_from_selfie(photo_bytes: bytes, username: str) -> str:
    """Analyze selfie to assess sobriety level and give harsh recommendations."""
    if not AI_CONFIGURED:
        return "Мій детектор тверезості відключено. (API Key missing)"

    try:
        prompt = (
            f"Ти — безжалісний нарколог-детектив і аналізуєш селфі від {username}. "
            f"Твоє завдання — визначити рівень тверезості/сп'яніння цієї людини за виглядом. "
            f"1. Оціни вираз обличчя, очі (чи скляні?), поставу, загальний вигляд. "
            f"2. Постав ДІАГНОЗ: шкала від 0 (монах-трезвенник) до 10 (після весілля в селі). "
            f"3. Дай ЖОРСТКІ рекомендації що робити далі. Наприклад: 'ляж спати', 'здай телефон другу', "
            f"'замов таксі і не торкайся до керма', 'пий воду як кит', 'подзвони мамі — хай сміється'. "
            f"4. ЯКЩО на фото немає людини — скажи, що навіть сфотографуватися себе тверезо не вийшло. "
            f"5. Будь саркастичним, смішним, але чесним. "
            f"Відповідь має бути українською мовою, 3-5 речень, з емодзі."
        )

        generation_config = genai.types.GenerationConfig(temperature=1.1)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        model = genai.GenerativeModel('gemini-3-flash-preview', safety_settings=safety_settings)
        content_list = [prompt, {"mime_type": "image/jpeg", "data": photo_bytes}]
        response = await model.generate_content_async(content_list, generation_config=generation_config)

        if not response.candidates:
            return "Навіть мій алкотестер злякався твоєї пики..."

        print(f"Sobriety selfie analysis: {response.text}")
        return response.text

    except Exception as e:
        print(f"Sobriety selfie error: {e}")
        return await _sobriety_fallback(username, "селфі")


async def _sobriety_fallback(username: str, source: str) -> str:
    """Fallback sobriety roast when media can't be analyzed."""
    try:
        prompt = (
            f"{username} надіслав {source}, але мій детектор тверезості не зміг його проаналізувати. "
            f"Напиши смішний саркастичний коментар про те, що раз людина взагалі надсилає {source} боту — "
            f"вона точно вже не тверезий. Дай 2-3 жорсткі практичні поради. "
            f"Відповідь українською, 2-4 речення, з емодзі."
        )
        model = genai.GenerativeModel('gemini-3-flash-preview')
        response = await model.generate_content_async(prompt)
        return response.text if response.candidates else "Ти явно не тверезий, якщо надсилаєш це боту 🫠"
    except Exception:
        return "Ти явно не тверезий, якщо надсилаєш це боту 🫠 Пий воду і лягай спати!"
