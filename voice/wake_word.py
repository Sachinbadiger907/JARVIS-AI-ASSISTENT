"""
Jarvis Wake Word Detection
"""

WAKE_WORDS = ["jarvis", "hey jarvis", "ok jarvis", "okay jarvis"]


def check_wake_word(text: str):
    """
    Checks if the wake word is present in the recognized text.
    Returns (True, remaining_command) if found, else (False, None).
    """

    if not text:
        return False, None

    text = text.lower().strip()

    for wake in sorted(WAKE_WORDS, key=len, reverse=True):

        if text.startswith(wake):
            remaining = text[len(wake):].strip()
            return True, remaining

        if wake in text:
            remaining = text.replace(wake, "", 1).strip()
            return True, remaining

    return False, None