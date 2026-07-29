"""
Jarvis Listener - supports English, Hindi, and Kannada.
Also saves each recording to a temp wav file so voice_id.py can verify
whose voice it is before Jarvis acts on it.
"""

import speech_recognition as sr
import socket
import os
import tempfile

socket.setdefaulttimeout(8)

LANGUAGE_CODES = {
    "english": "en-IN",
    "hindi": "hi-IN",
    "kannada": "kn-IN",
}

LAST_AUDIO_PATH = os.path.join(tempfile.gettempdir(), "jarvis_last_audio.wav")


class Listener:

    def __init__(self):

        self.recognizer = sr.Recognizer()

        self.recognizer.energy_threshold = 50
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.pause_threshold = 1.0
        self.recognizer.non_speaking_duration = 0.5

        self.language_order = ["en-IN", "hi-IN", "kn-IN"]
        self.last_audio_path = LAST_AUDIO_PATH

    def set_language(self, language_name: str):

        code = LANGUAGE_CODES.get(language_name.lower())

        if not code:
            return False

        self.language_order = [code] + [c for c in LANGUAGE_CODES.values() if c != code]
        return True

    def listen(self):

        try:
            with sr.Microphone() as source:

                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(source)

        except Exception as e:
            print(f"Mic error: {e}")
            return None

        # Save the raw audio so it can be checked against the enrolled voice
        try:
            with open(self.last_audio_path, "wb") as f:
                f.write(audio.get_wav_data())
        except Exception as e:
            print(f"Could not save audio for voice ID: {e}")

        for lang in self.language_order:
            try:
                text = self.recognizer.recognize_google(audio, language=lang)
                print(f"You ({lang}):", text)
                return text.lower().strip()

            except sr.UnknownValueError:
                continue

            except sr.RequestError:
                print("No Internet connection.")
                return None

        return None