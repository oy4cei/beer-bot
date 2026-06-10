import os
import sys
import unittest
import asyncio
import io
from PIL import Image
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure the root folder is in python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import database
import ai_service

# Helper to generate real tiny JPEG image bytes so PIL doesn't crash
def get_dummy_image_bytes():
    img = Image.new('RGB', (10, 10), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

class TestBeerBotModes(unittest.TestCase):
    def setUp(self):
        # Use an in-memory or custom database for tests
        database.DB_NAME = "test_beer_bot.db"
        database.init_db()
        self.dummy_img = get_dummy_image_bytes()

    def tearDown(self):
        if os.path.exists("test_beer_bot.db"):
            os.remove("test_beer_bot.db")

    def test_database_settings(self):
        async def run_test():
            # Default mode should be 'oldschool'
            mode = await database.get_user_mode(12345)
            self.assertEqual(mode, 'oldschool')

            # Setting mode to 'sir'
            await database.set_user_mode(12345, 'sir')
            mode = await database.get_user_mode(12345)
            self.assertEqual(mode, 'sir')

            # Setting back to 'oldschool'
            await database.set_user_mode(12345, 'oldschool')
            mode = await database.get_user_mode(12345)
            self.assertEqual(mode, 'oldschool')
        
        asyncio.run(run_test())

    @patch('google.generativeai.GenerativeModel')
    def test_ai_service_prompt_routing_oldschool(self, mock_gen_model_class):
        async def run_test():
            # Mock generativeai behaviour
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.candidates = [MagicMock()]
            mock_response.text = "Це якесь пійло! ALCOHOL"
            
            # Use AsyncMock for async methods
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)
            mock_gen_model_class.return_value = mock_model

            ai_service.AI_CONFIGURED = True

            # Run analyze_drink in oldschool mode
            comment, is_alcoholic = await ai_service.analyze_drink(self.dummy_img, bot_mode="oldschool")
            
            self.assertEqual(comment, "Це якесь пійло!")
            self.assertTrue(is_alcoholic)

            # Retrieve the prompt passed to generate_content_async
            call_args = mock_model.generate_content_async.call_args[0][0]
            prompt = call_args[0]
            
            # Verify the prompt contents (should be standup/critic style)
            self.assertIn("барний критик", prompt)
            self.assertNotIn("британський джентльмен", prompt)
        
        asyncio.run(run_test())

    @patch('google.generativeai.GenerativeModel')
    def test_ai_service_prompt_routing_sir(self, mock_gen_model_class):
        async def run_test():
            # Mock generativeai behaviour
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.candidates = [MagicMock()]
            mock_response.text = "Вибір вельми оригінальний. ALCOHOL"
            
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)
            mock_gen_model_class.return_value = mock_model

            ai_service.AI_CONFIGURED = True

            # Run analyze_drink in sir mode
            comment, is_alcoholic = await ai_service.analyze_drink(self.dummy_img, bot_mode="sir")
            
            self.assertEqual(comment, "Вибір вельми оригінальний.")
            self.assertTrue(is_alcoholic)

            # Retrieve the prompt passed to generate_content_async
            call_args = mock_model.generate_content_async.call_args[0][0]
            prompt = call_args[0]
            
            # Verify the prompt contents (should be gentleman style)
            self.assertIn("британський джентльмен", prompt)
            self.assertNotIn("барний критик", prompt)

        asyncio.run(run_test())

    @patch('google.generativeai.GenerativeModel')
    def test_ai_sommelier_collection_routing(self, mock_gen_model_class):
        async def run_test():
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.candidates = [MagicMock()]
            mock_response.text = "Герцог кислих елів"
            
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)
            mock_gen_model_class.return_value = mock_model

            ai_service.AI_CONFIGURED = True

            # Run in sir mode
            roast = await ai_service.analyze_sommelier_collection(7, "tester", bot_mode="sir")
            self.assertEqual(roast, "Герцог кислих елів")

            prompt = mock_model.generate_content_async.call_args[0][0]
            self.assertIn("англійський лорд", prompt)
            self.assertIn("іронічний дворянський титул", prompt)

            # Run in oldschool mode
            await ai_service.analyze_sommelier_collection(7, "tester", bot_mode="oldschool")
            prompt = mock_model.generate_content_async.call_args[0][0]
            self.assertIn("саркастичний суддя", prompt)
            self.assertIn("ПРИНИЗЛИВЕ ЗВАННЯ", prompt)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
