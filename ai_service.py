import os
import asyncio
import google.generativeai as genai
from PIL import Image
import io
import random
import base64
from insults import UKRAINIAN_INSULTS, SPECIAL_INSULTS, BALKAN_INSULTS, SPANISH_INSULTS, ARABIC_INSULTS, SCOTTISH_IRISH_INSULTS, BRITISH_INSULTS

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

async def analyze_drink(photo_bytes, todays_comments=None, bot_mode="oldschool"):
    if not AI_CONFIGURED:
        return "Ех, мої нейронні мережі відключені. Не можу розгледіти, що там. Але впевнений, це щось смачне! (API Key missing)", True

    try:
        image = Image.open(io.BytesIO(photo_bytes))
        
        if bot_mode == "sir":
            prompt = (
                "Ти — надзвичайно вишуканий, високоінтелектуальний британський джентльмен, лорд, політик та філософ. "
                "Твоє завдання — прокоментувати та тонко, вишукано розкритикувати напій на фото. "
                "1. УВАЖНО подивися на фото. Визнач бренд, тип напою, келих або навколишнє оточення. "
                "2. Твій стиль — це взірець британського снобізму, тонкої іронії в стилі Оскара Уайльда, Бернарда Шоу чи Вінстона Черчилля. "
                "3. Жодних грубощів, вульгарностей, крику чи народної лайки. Тільки інтелектуальні шпильки, прихований сарказм та надзвичайно ввічлива зневага. "
                "Звертайся до користувача з підкресленою повагою: 'сер', 'міледі', 'вельмишановний пане' або подібними аристократичними зверненнями. "
                "4. Наприклад: замість 'це гівно' скажи 'вибір цього напою демонструє дивовижну сміливість перед обличчям повної відсутності смаку'. "
                "Відповідь має бути українською мовою, короткою (1-3 речення) і унікальною для цього фото."
            )
        else:
            # Determine mode based on probability for oldschool
            # 0.0 - 0.6: Special Insults (60%)
            # 0.6 - 0.8: Ukrainian Insults (20%)
            # 0.8 - 0.9: Praise (10%)
            # 0.9 - 1.0: Love Declaration Song Lyrics (10%)
            rand_val = random.random()
            
            if rand_val < 0.6:
                 # Special Insults Mode (60%)
                 selected_insults = ", ".join(random.sample(SPECIAL_INSULTS + BALKAN_INSULTS + SPANISH_INSULTS + ARABIC_INSULTS + SCOTTISH_IRISH_INSULTS + BRITISH_INSULTS, 3))
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

        if todays_comments:
            prompt += f"\n\nВАЖЛИВО: Ти сьогодні вже відповідав такі коментарі: {todays_comments}. ОБОВ'ЯЗКОВО вигадай повністю унікальний текст. НЕ ПОВТОРЮЙ ЖОДНОЇ ФРАЗИ З ПОПЕРЕДНІХ КОМЕНТАРІВ! Будь максимально оригінальним."

        prompt += "\n\nВ кінці своєї відповіді (на самому останньому рядку) обов'язково напиши одне слово: 'ALCOHOL' якщо на фото видно алкогольний напій (або щось схоже на нього), або 'NON_ALCOHOL' якщо це точно безалкогольне (чай, кава, вода, сік тощо)."

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
                    if bot_mode == "sir":
                        return "Мій вельмишановний друже, здається, це зображення дещо перевищує межі вишуканості, які мої скромні мережі здатні осягнути без легкого сум'яття. 😉", True
                    return "Мої нейронні мережі почервоніли від сорому... Щось там дуже відверте або провокаційне на фото! 😉", True
                
                result_text = response.text
                is_alcoholic = True
                if "NON_ALCOHOL" in result_text:
                    is_alcoholic = False
                    result_text = result_text.replace("NON_ALCOHOL", "").strip()
                elif "ALCOHOL" in result_text:
                    result_text = result_text.replace("ALCOHOL", "").strip()

                print(f"AI Response success: {result_text}") 
                return result_text, is_alcoholic
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
                        if bot_mode == "sir":
                            return "Я щиро перепрошую, але кількість запитів до моєї скромної персони наразі перевершує всі мислимі межі пристойності. Будь ласка, зачекайте хвилину. (API Rate Limit 429)", True
                        return "Ой, забагато запитів! Дай мені хвилинку перевести подих... (API Rate Limit 429)", True
                else:
                    import traceback
                    traceback.print_exc()
                    
                    if "403" in error_str and "leaked" in error_str:
                        return "Ой, мій API ключ забанили через витік! (Помилка 403: Key Leaked). Будь ласка, онови GEMINI_API_KEY у файлі .env.", True
                        
                    return f"Щось у мене в очах помутніло... (Помилка: {str(e)[:100]})", True
                    
        return "Щось пішло не так...", True
    except Exception as e:
        print(f"AI Error: {e}")
        if bot_mode == "sir":
            return "Вельмишановний пане, мої оптичні сенсори зазнали певного розладу. Здається, етикетка цього напою є надто загадковою для мого аналізу.", True
        return "Щось у мене в очах помутніло... Не можу розгледіти етикетку. Напевно, палене!", True


async def analyze_sommelier_collection(drink_count: int, username: str, bot_mode="oldschool") -> str:
    """Every 7 drinks: sarcastically roast the sommelier's taste and give them a ridiculous title."""
    if not AI_CONFIGURED:
        return "Мій алкогольний ШІ вирубився раніше, ніж ти встиг допити. (API Key missing)"

    try:
        if bot_mode == "sir":
            prompt = (
                f"Ти — вишуканий англійський лорд, аристократ, сноб і суддя високої кухні. "
                f"Користувач {username} щойно задокументував свій {drink_count}-й напій. "
                f"Тобі потрібно зробити таке:\n"
                f"1. Тонко, вишукано та інтелектуально, у стилі джентльмена, прокоментувати кількість та якість його напоїв (1-2 речення). "
                f"Зовні це має виглядати дуже ввічливо, але нести в собі глибоке розчарування його плебейськими звичками. "
                f"2. НАЙГОЛОВНІШЕ — присвой {username} вишуканий, але іронічний дворянський титул. "
                f"Наприклад: 'Лорд кислих елів з присмаком розчарування', 'Віконт теплих лагерів', 'Герцог безалкогольного сурогату'. "
                f"Титул має звучати помпезно, аристократично та бути унікальним, але підкреслювати відсутність смаку. "
                f"3. Оголоси це звання з тонким, інтелектуальним сарказмом. "
                f"Відповідь має бути українською мовою, 3-5 речень, без брутальних слів. Дотримуйся манер."
            )
        else:
            prompt = (
                f"Ти — жорстокий, безжалісний і надзвичайно саркастичний суддя алкогольного смаку. "
                f"Людина на ім'я {username} щойно задокументувала свій {drink_count}-й напій. "
                f"Зроби наступне:\n"
                f"1. Коротко (1-2 речення) висміяй 'асортимент' цього 'сомельє' — уяви яких покидьків напоїв вони пили судячи з кількості. "
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
            if bot_mode == "sir":
                return "Мої манери не дозволяють мені продовжувати цю розмову в такому тоні..."
            return "Навіть мій ШІ відмовляється коментувати такий жахливий смак..."

        print(f"Sommelier roast: {response.text}")
        return response.text

    except Exception as e:
        print(f"Sommelier roast error: {e}")
        if bot_mode == "sir":
            return f"Мій внутрішній лорд-дворецький зазнав повного збентеження через ваші смакові вподобання... (Помилка: {str(e)[:80]})"
        return f"Мій алкогольний ШІ впав у відчай від твого списку напоїв... (Помилка: {str(e)[:80]})"


async def analyze_sobriety_from_audio(audio_bytes: bytes, username: str, bot_mode="oldschool") -> str:
    """Analyze voice message to assess sobriety level and give harsh recommendations."""
    if not AI_CONFIGURED:
        return "Мій детектор тверезості відключено. (API Key missing)"

    try:
        if bot_mode == "sir":
            prompt = (
                f"Ти — вишуканий англійський лорд, аристократ і придворний лікар. Ти аналізуєш голосове повідомлення від {username}. "
                f"Твоє завдання — делікатно, але нищівно оцінити рівень його тверезості. "
                f"1. Оціни дикцію, темп мовлення та логіку, висловлюючись як шляхетний доктор з вищого світу. "
                f"2. Постав йому діагноз за аристократичною шкалою (наприклад, 'легке запаморочення від імперських амбіцій' або 'повна втрата джентльменської гідності'). "
                f"3. Дай вишукані рекомендації: наприклад, 'попросити прислугу заварити міцний чай', 'відпочити в бібліотеці під пледом', 'негайно припинити диктувати послання іншим лордам'. "
                f"4. Будь тонким, іронічним, розмовляй з підкресленою шаною, уникаючи грубощів та просторіч. "
                f"Відповідь має бути українською мовою, 3-5 речень, без вульгарних слів."
            )
        else:
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
            if bot_mode == "sir":
                return "Навіть мої виховані вуха відмовляються сприймати ці звуки за джентльменську мову..."
            return "Навіть мій детектор п'янства розгубився від почутого..."

        print(f"Sobriety audio analysis: {response.text}")
        return response.text

    except Exception as e:
        print(f"Sobriety audio error: {e}")
        # Fallback: roast without actual audio
        return await _sobriety_fallback(username, "голосового повідомлення", bot_mode=bot_mode)


async def analyze_sobriety_from_selfie(photo_bytes: bytes, username: str, bot_mode="oldschool") -> str:
    """Analyze selfie to assess sobriety level and give harsh recommendations."""
    if not AI_CONFIGURED:
        return "Мій детектор тверезості відключено. (API Key missing)"

    try:
        if bot_mode == "sir":
            prompt = (
                f"Ти — вишуканий англійський лорд, аристократ і художник-портретист. Ти аналізуєш селфі від {username}. "
                f"Твоє завдання — оцінити рівень його тверезості за зовнішнім виглядом. "
                f"1. Оціни поставу, вираз обличчя, напрямок погляду та загальну охайність джентльмена на портреті. "
                f"2. Вислови свій вердикт у стилі витонченої світської критики (наприклад, 'погляд випромінює глибоку тугу за втраченим королівським престолом' або 'міміка дещо втратила аристократичну стриманість'). "
                f"3. Дай вишукані рекомендації (замовити екіпаж, приховати обличчя за циліндром, випити склянку содової). "
                f"4. ЯКЩО на фото немає людини — зауваж з іронією, що джентльмену не вистачило координації, аби потрапити у кадр свого власного портрета. "
                f"5. Будь тонким, ввічливим, пиши українською мовою, 3-5 речень, уникаючи грубощів."
            )
        else:
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
            if bot_mode == "sir":
                return "Зображення на портреті настільки розмите, що мій внутрішній естетичний цензор змушений відвернути погляд..."
            return "Навіть мій алкотестер злякався твоєї пики..."

        print(f"Sobriety selfie analysis: {response.text}")
        return response.text

    except Exception as e:
        print(f"Sobriety selfie error: {e}")
        return await _sobriety_fallback(username, "селфі", bot_mode=bot_mode)


async def _sobriety_fallback(username: str, source: str, bot_mode="oldschool") -> str:
    """Fallback sobriety roast when media can't be analyzed."""
    try:
        if bot_mode == "sir":
            prompt = (
                f"Користувач {username} надіслав {source}, але наш медичний кабінет не зміг його проаналізувати. "
                f"Напиши витончений саркастичний коментар про те, що сам факт надсилання {source} нашому автоматичному джентльмену "
                f"свідчить про те, що шановний пан вже перебуває у стані приємної вечірньої розслабленості. "
                f"Дай 2-3 вишукані поради. "
                f"Відповідь українською мовою, 2-4 речення, без грубощів."
            )
        else:
            prompt = (
                f"{username} надіслав {source}, але мій детектор тверезості не зміг його проаналізувати. "
                f"Напиши смішний саркастичний коментар про те, що раз людина взагалі надсилає {source} боту — "
                f"вона точно вже не тверезий. Дай 2-3 жорсткі практичні поради. "
                f"Відповідь українською, 2-4 речення, з емодзі."
            )
        model = genai.GenerativeModel('gemini-3-flash-preview')
        response = await model.generate_content_async(prompt)
        if response.candidates:
            return response.text
        if bot_mode == "sir":
            return "Вельмишановний пане, здається, ви вже перебуваєте в тій стадії вечора, коли найкращим рішенням буде склянка чистої води та глибокий сон. 🫠"
        return "Ти явно не тверезий, якщо надсилаєш це боту 🫠"
    except Exception:
        if bot_mode == "sir":
            return "Вельмишановний пане, здається, ви вже перебуваєте в тій стадії вечора, коли найкращим рішенням буде склянка чистої води та глибокий сон. 🫠"
        return "Ти явно не тверезий, якщо надсилаєш це боту 🫠 Пий воду і лягай спати!"


