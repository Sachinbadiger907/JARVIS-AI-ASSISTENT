"""
Jarvis - Main Entry Point
"""

import sys
import os
import subprocess

# When run via pythonw.exe (no console window), stdout/stderr are None -
# redirect print() output to a log file instead, so it doesn't crash.
if sys.stdout is None:
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_log.txt")
    log_file = open(log_path, "a", encoding="utf-8")
    sys.stdout = log_file
    sys.stderr = log_file

from voice.listener import Listener
from voice.speaker import Speaker
from voice.wake_word import check_wake_word
from brain.intent import IntentDetector
from brain.actions import ActionExecutor
from brain.ai_chat import AIChat
from brain.code_writer import CodeWriter
from brain.screen_reader import ScreenReader
from brain.whatsapp_sender import WhatsAppSender
from brain import voice_id
import status_bridge


class Jarvis:

    def __init__(self):
        self.listener = Listener()
        self.speaker = Speaker()
        self.intent = IntentDetector()
        self.actions = ActionExecutor()
        self.ai_chat = AIChat()
        self.code_writer = CodeWriter()
        self.screen_reader = ScreenReader()
        self.whatsapp_sender = WhatsAppSender()
        self.gui_process = None
        status_bridge.set_status("idle")

    def speak(self, text):
        status_bridge.set_status("speaking")
        self.speaker.speak(text)
        status_bridge.set_status("idle")

    def show_jarvis_screen(self):

        if self.gui_process is not None and self.gui_process.poll() is None:
            self.speak("Already on screen, boss.")
            return

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            gui_path = os.path.join(script_dir, "gui_app.py")

            self.gui_process = subprocess.Popen(
                ["pythonw", gui_path]
            )
            self.speak("Here I am, boss.")

        except Exception as e:
            print(f"Could not open Jarvis screen: {e}")
            self.speak("Couldn't open the screen, boss.")

    def hide_jarvis_screen(self):

        if self.gui_process is not None and self.gui_process.poll() is None:
            self.gui_process.terminate()
            self.gui_process = None
            self.speak("Closed the screen, boss.")
        else:
            self.speak("The screen isn't open, boss.")

    def handle_command(self, command: str):

        detected = self.intent.detect(command)

        if detected is None:
            reply = self.ai_chat.chat(command)
            self.speak(reply)
            return

        action = detected["action"]
        target = detected.get("target", "")

        if action == "open":
            success = self.actions.open_app(target)
            self.speak(f"Opened {target}, boss." if success else f"Couldn't open {target}, boss.")

        elif action == "open_and_search":
            success = self.actions.open_and_search(target, detected["query"])
            self.speak("Searching, boss." if success else "Couldn't search that, boss.")

        elif action == "search":
            success = self.actions.search(target)
            self.speak("Searching, boss." if success else "Couldn't search that, boss.")

        elif action == "type":
            success = self.actions.type_text(target)
            self.speak("Done, boss." if success else "Couldn't type that, boss.")

        elif action == "direct":
            success = self.actions.direct_action(target)
            self.speak("Done, boss." if success else "Couldn't do that, boss.")

        elif action == "close":
            success = self.actions.close_app(target)
            self.speak(f"Closed {target}, boss." if success else f"Couldn't close {target}, boss.")

        elif action == "write_code":
            self.speak("Writing that code for you, boss, give me a second.")
            success = self.code_writer.generate_and_open(target)
            self.speak("Done, opened it in VS Code, boss. Say run it whenever you want to test it." if success else "Sorry, couldn't generate that code, boss.")

        elif action == "run_code":
            self.speak("Checking for any libraries it needs, then running it, boss.")
            success = self.code_writer.run_last_file()
            self.speak("Running it now, boss." if success else "There's no code to run yet, boss.")

        elif action == "show_gui":
            self.show_jarvis_screen()

        elif action == "hide_gui":
            self.hide_jarvis_screen()

        elif action == "set_language":
            success = self.listener.set_language(target)
            confirmations = {"english": "Okay, talking in English now, boss.",
                              "hindi": "Theek hai boss, ab Hindi mein baat karte hain.",
                              "kannada": "Sari boss, Kannada dalli maatadona."}
            self.speak(confirmations.get(target, "Okay, boss.") if success else "Couldn't switch that, boss.")

        elif action == "read_screen":
            self.speak("Let me take a look, boss.")
            explanation = self.screen_reader.read_and_explain()
            self.speak(explanation)

        elif action == "send_whatsapp":
            success = self.whatsapp_sender.send_message(target, detected.get("message", ""))
            self.speak(f"Sent it to {target}, boss." if success else f"Couldn't send to {target}, boss - check the contact list.")

        else:
            self.speak("Not sure how to do that yet, boss.")

    def start(self):

        # Starts completely SILENT and ASLEEP - no greeting, no sound,
        # until you explicitly say "hey jarvis"
        active = False

        SLEEP_WORDS = ("exit", "sleep", "stop listening", "go to sleep")
        QUIT_WORDS = ("shutdown jarvis", "close completely", "quit program")

        print("Jarvis is asleep and silent. Say 'Hey Jarvis' to wake it up.")

        if voice_id.is_enrolled():
            print("Voice ID is active - only your enrolled voice will be accepted.")
        else:
            print("No voice enrolled yet - run enroll_voice.py to restrict Jarvis to your voice only.")

        while True:

            status_bridge.set_status("listening")
            heard = self.listener.listen()
            status_bridge.set_status("idle")

            if not heard:
                continue

            if not voice_id.is_matching_voice(self.listener.last_audio_path):
                print("Voice not recognized - ignoring.")
                continue

            is_wake, stripped_command = check_wake_word(heard)

            if not active:
                # ASLEEP - ignore everything except the wake word
                if not is_wake:
                    continue

                self.speak("Hi boss, how can I help you?")
                active = True
                continue

            # AWAKE - strip "jarvis" if said out of habit, otherwise use as-is
            command = stripped_command if is_wake else heard

            if not command:
                continue

            if any(phrase in command for phrase in QUIT_WORDS):
                self.speak("Shutting down completely, boss.")
                print("Exiting Jarvis...")
                break

            if any(phrase == command.strip() or phrase in command for phrase in SLEEP_WORDS):
                self.speak("Going to sleep, boss. Say hey Jarvis when you need me.")
                active = False
                continue

            self.handle_command(command)


if __name__ == "__main__":
    Jarvis().start()
    