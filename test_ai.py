import os
import google.generativeai as genai
from PIL import Image
import io

# Hardcode key for testing to ensure env var isn't the issue
# (In real app we use env var, but here we want to be sure)
API_KEY = os.environ.get("GEMINI_API_KEY")

def test_gemini():
    print(f"Testing with API Key: {API_KEY[:5]}...")
    genai.configure(api_key=API_KEY)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create a simple dummy image (red square) to test vision
        img = Image.new('RGB', (100, 100), color = 'red')
        
        prompt = "What color is this image? Answer in one word."
        
        print("Sending request to Gemini...")
        response = model.generate_content([prompt, img])
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    from ai_service import analyze_drink

    # Create a simple dummy image (red square)
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()

    print("Testing analyze_drink...")
    try:
        result = asyncio.run(analyze_drink(img_bytes))
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
