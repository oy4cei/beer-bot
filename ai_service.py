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

async def analyze_drink(photo_bytes):
    if not configure_ai():
        return "Эх, мои нейронные сети отключены. Не могу разглядеть, что там. Но уверен, это что-то вкусное! (API Key missing)"

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        image = Image.open(io.BytesIO(photo_bytes))
        
        prompt = (
            "Ты — циничный, но веселый барный критик. Твоя задача — прокомментировать выбор напитка на фото. "
            "1. ВНИМАТЕЛЬНО посмотри на фото. Найди название бренда, тип напитка, закуску или обстановку. "
            "2. Если ты видишь конкретный бренд — ОБЯЗАТЕЛЬНО упомяни его. "
            "3. Придумай ОРИГИНАЛЬНУЮ шутку или подкол именно про этот напиток. "
            "Не используй общие фразы типа 'хороший выбор'. "
            "Если это лагер — пошути про воду. Если стаут — про нефть. Если IPA — про еловые шишки. "
            "Если это водка — спроси, где медведь. "
            "Будь дерзким, используй сленг. "
            "Ответ должен быть коротким (1-2 предложения) и уникальным для этого фото."
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
