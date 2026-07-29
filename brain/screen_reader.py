"""
Jarvis Screen Reader - reads what's on screen and explains it in simple words
"""

import os
import tempfile
import requests
import pyautogui
import pytesseract
from PIL import Image

# Default install location on Windows - update this path if you installed it elsewhere
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:0.5b"

SCREEN_PROMPT = (
    "You are Jarvis, explaining what's on the user's screen like a friendly "
    "teacher would to a beginner. Keep it under 50 words, simple and clear, "
    "casual spoken tone, no markdown or bullet points. If the screen text "
    "looks like code, briefly explain what the code does. If it's an error "
    "message, explain what likely caused it in plain language."
)


class ScreenReader:

    def read_and_explain(self) -> str:

        try:
            screenshot_path = os.path.join(tempfile.gettempdir(), "jarvis_screen.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)

            extracted_text = pytesseract.image_to_string(Image.open(screenshot_path)).strip()

            if not extracted_text:
                return "I can't find any readable text on your screen right now, boss."

            # Limit text sent to the model so it doesn't choke on huge screens
            extracted_text = extracted_text[:2000]

            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "system", "content": SCREEN_PROMPT},
                        {"role": "user", "content": f"Here's the text on my screen:\n\n{extracted_text}"}
                    ],
                    "stream": False,
                    "options": {"num_predict": 80, "temperature": 0.4}
                },
                timeout=75
            )

            response.raise_for_status()

            return response.json()["message"]["content"].strip()

        except pytesseract.TesseractNotFoundError:
            return "Tesseract OCR isn't installed yet, boss, I can't read the screen without it."

        except requests.exceptions.ConnectionError:
            return "Can't reach my brain right now, boss, is Ollama running?"

        except Exception as e:
            print(f"Screen reading error: {e}")
            return "Sorry boss, something went wrong reading your screen."