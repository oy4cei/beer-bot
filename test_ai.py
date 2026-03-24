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
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
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
    from ai_service import analyze_drink, configure_ai

    # Ensure the key is in env
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set. Please set it or use a .env file.")
        # Removed hardcoded key that was leaked
        # os.environ["GEMINI_API_KEY"] = "..." 
        import sys
        sys.exit(1)
    
    print("Configuring AI...")
    configure_ai()

    # Create a simple dummy image (red square)
    img = Image.new('RGB', (224, 224), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG') # JPEG is safer for vision
    img_bytes = img_byte_arr.getvalue()

    print("Testing analyze_drink with dummy RED image...")
    try:
        # Run the async function
        result = asyncio.run(analyze_drink(img_bytes))
        print(f"\nFINAL RESULT:\n{result}")
    except Exception as e:
        print(f"\nFATAL TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
