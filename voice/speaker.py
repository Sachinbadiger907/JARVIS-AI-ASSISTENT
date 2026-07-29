"""
Jarvis Speaker - uses Edge-TTS, auto-picks voice based on the language of the text
"""

import asyncio
import os
import re
import tempfile

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import edge_tts
import pygame


VOICES = {
    "en": "en-IN-PrabhatNeural",
    "hi": "hi-IN-MadhurNeural",
    "kn": "kn-IN-GaganNeural",
}

AUDIO_PATH = os.path.join(tempfile.gettempdir(), "jarvis_reply.mp3")


def detect_language(text: str) -> str:

    if re.search(r"[\u0C80-\u0CFF]", text):
        return "kn"

    if re.search(r"[\u0900-\u097F]", text):
        return "hi"

    return "en"


class Speaker:

    def __init__(self):
        pygame.mixer.init()

    def speak(self, text):

        print(f"Jarvis: {text}")

        language = detect_language(text)
        voice = VOICES.get(language, VOICES["en"])

        try:
            asyncio.run(self._generate(text, voice))

            pygame.mixer.music.load(AUDIO_PATH)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)

            pygame.mixer.music.unload()

        except Exception as e:
            print(f"Speech error: {e}")

    async def _generate(self, text, voice):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(AUDIO_PATH)