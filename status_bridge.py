"""
Jarvis Status Bridge - lets main.py and gui_app.py (separate processes)
share Jarvis's current state (idle/listening/speaking) via a small shared file.
"""

import os
import tempfile

STATUS_PATH = os.path.join(tempfile.gettempdir(), "jarvis_status.txt")


def set_status(status: str):
    try:
        with open(STATUS_PATH, "w", encoding="utf-8") as f:
            f.write(status)
    except Exception:
        pass


def get_status() -> str:
    try:
        with open(STATUS_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "idle"