"""
Jarvis Intent Detection
"""

DIRECT_COMMANDS = [
    "left click", "right click", "double click",
    "scroll up", "scroll down",
    "select all", "copy", "paste", "cut", "undo", "redo",
]

CODE_TRIGGER_WORDS = [
    "write code", "write a function", "write a program",
    "generate code", "create code", "code for", "write me code",
]

BUILD_VERBS = ["write", "build", "create", "make", "design"]
BUILD_NOUNS = ["website", "webpage", "web page", "site", "app", "game", "program", "code", "script"]


def is_build_request(text: str) -> bool:
    has_verb = any(verb in text for verb in BUILD_VERBS)
    has_noun = any(noun in text for noun in BUILD_NOUNS)
    return has_verb and has_noun


class IntentDetector:

    def detect(self, text: str):

        if not text:
            return None

        text = text.lower().strip()

        # ---------- CODE WRITING ----------
        if any(trigger in text for trigger in CODE_TRIGGER_WORDS) or is_build_request(text):
            return {"action": "write_code", "target": text}

        run_trigger_words = ["run it", "run the code", "run this", "execute it", "execute the code"]
        if any(trigger in text for trigger in run_trigger_words):
            return {"action": "run_code", "target": ""}

        # ---------- SCREEN READING ----------
        # ---------- LANGUAGE SWITCHING ----------
        if "talk in kannada" in text or "speak in kannada" in text or "switch to kannada" in text:
            return {"action": "set_language", "target": "kannada"}

        if "talk in hindi" in text or "speak in hindi" in text or "switch to hindi" in text:
            return {"action": "set_language", "target": "hindi"}

        if "talk in english" in text or "speak in english" in text or "switch to english" in text:
            return {"action": "set_language", "target": "english"}

        screen_triggers = ["read my screen", "read the screen", "what's on my screen",
                            "explain my screen", "explain the screen", "look at my screen"]
        if any(trigger in text for trigger in screen_triggers):
            return {"action": "read_screen", "target": ""}

        # ---------- WHATSAPP MESSAGING ----------
        # e.g. "message rahul that the website is done" or "send whatsapp to mom saying im coming home"
        if text.startswith("message ") or text.startswith("send whatsapp"):

            for splitter in [" that ", " saying "]:
                if splitter in text:
                    left, message = text.split(splitter, 1)

                    contact = left.replace("message", "").replace("send whatsapp", "") \
                                  .replace("to", "").strip()

                    return {"action": "send_whatsapp", "target": contact, "message": message.strip()}

        if text.startswith("type "):
            return {"action": "type", "target": text[len("type "):].strip()}

        if text.startswith("search "):
            return {"action": "search", "target": text[len("search "):].strip()}

        if " search " in text and text.startswith("open"):
            parts = text.split(" search ", 1)
            app_part = parts[0].replace("open", "").strip()
            query = parts[1].strip()
            return {"action": "open_and_search", "target": app_part, "query": query}

        # ---------- JARVIS SCREEN (must be checked before generic "open") ----------
        show_screen_phrases = ["open jarvis", "show jarvis", "jarvis screen", "wake up jarvis screen"]
        if any(phrase in text for phrase in show_screen_phrases):
            return {"action": "show_gui", "target": ""}

        hide_screen_phrases = ["close jarvis screen", "hide jarvis screen", "close jarvis window", "hide jarvis"]
        if any(phrase in text for phrase in hide_screen_phrases):
            return {"action": "hide_gui", "target": ""}

        if text.startswith("open "):
            return {"action": "open", "target": text[len("open "):].strip()}

        if text.startswith("close "):
            return {"action": "close", "target": text[len("close "):].strip()}

        for cmd in DIRECT_COMMANDS:
            if cmd in text:
                return {"action": "direct", "target": cmd}

        return None