"""
Jarvis Actions - controls the laptop: opens/closes ANY desktop app or website
"""

import os
import glob
import difflib
import subprocess
import webbrowser
import pyautogui
import psutil


# Fast-path shortcuts for the most common ones (skips searching, opens instantly)
KNOWN_APPS = {
    "chrome": {"type": "app", "cmd": ["cmd", "/c", "start", "chrome"]},
    "google chrome": {"type": "app", "cmd": ["cmd", "/c", "start", "chrome"]},
    "notepad": {"type": "app", "cmd": ["notepad.exe"]},
    "vs code": {"type": "app", "cmd": ["cmd", "/c", "code"]},
    "vscode": {"type": "app", "cmd": ["cmd", "/c", "code"]},
    "visual studio code": {"type": "app", "cmd": ["cmd", "/c", "code"]},
    "calculator": {"type": "app", "cmd": ["calc.exe"]},
    "paint": {"type": "app", "cmd": ["mspaint.exe"]},
    "file explorer": {"type": "app", "cmd": ["explorer.exe"]},
    "explorer": {"type": "app", "cmd": ["explorer.exe"]},
    "task manager": {"type": "app", "cmd": ["taskmgr.exe"]},
    "settings": {"type": "app", "cmd": ["cmd", "/c", "start", "ms-settings:"]},
}

KNOWN_WEBSITES = {
    "youtube": "https://youtube.com",
    "maps": "https://maps.google.com",
    "google maps": "https://maps.google.com",
    "whatsapp": "https://web.whatsapp.com",
    "gmail": "https://mail.google.com",
    "instagram": "https://instagram.com",
    "facebook": "https://facebook.com",
    "linkedin": "https://linkedin.com",
    "google": "https://google.com",
    "amazon": "https://amazon.in",
    "flipkart": "https://flipkart.com",
}

START_MENU_DIRS = [
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
    os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
    os.path.expandvars(r"%USERPROFILE%\Desktop"),
    r"C:\Users\Public\Desktop",
]


def find_start_menu_shortcut(name: str):
    """
    Searches Windows Start Menu shortcuts for an installed app matching
    the spoken name, using fuzzy matching (e.g. "spotify" finds "Spotify.lnk").
    """

    all_shortcuts = []

    for base_dir in START_MENU_DIRS:
        if os.path.isdir(base_dir):
            pattern = os.path.join(base_dir, "**", "*.lnk")
            all_shortcuts.extend(glob.glob(pattern, recursive=True))

    if not all_shortcuts:
        return None

    names_only = [os.path.splitext(os.path.basename(p))[0] for p in all_shortcuts]

    matches = difflib.get_close_matches(name, names_only, n=1, cutoff=0.5)

    if matches:
        index = names_only.index(matches[0])
        return all_shortcuts[index]

    # fallback: substring match
    for path, shortcut_name in zip(all_shortcuts, names_only):
        if name.lower() in shortcut_name.lower():
            return path

    return None


class ActionExecutor:

    # ---------------- OPEN ----------------

    def open_app(self, target: str) -> bool:

        target = target.strip().lower()

        # 1. Known fast-path desktop app
        if target in KNOWN_APPS:
            try:
                subprocess.Popen(KNOWN_APPS[target]["cmd"])
                return True
            except Exception as e:
                print(f"Could not open {target}: {e}")
                return False

        # 2. Known website
        if target in KNOWN_WEBSITES:
            webbrowser.open(KNOWN_WEBSITES[target])
            return True

        # 3. Search installed programs (Start Menu shortcuts) for a match
        shortcut = find_start_menu_shortcut(target)
        if shortcut:
            try:
                os.startfile(shortcut)
                return True
            except Exception as e:
                print(f"Could not launch shortcut for {target}: {e}")

        # 4. Last resort: treat it as a website guess (e.g. "open spotify" -> spotify.com)
        try:
            guess_url = f"https://www.{target.replace(' ', '')}.com"
            webbrowser.open(guess_url)
            return True
        except Exception as e:
            print(f"Could not open {target} as a website either: {e}")
            return False

    def open_and_search(self, target: str, query: str) -> bool:

        try:
            if "map" in target:
                url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
            elif "youtube" in target:
                url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            else:
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

            webbrowser.open(url)
            return True

        except Exception as e:
            print(f"Could not search: {e}")
            return False

    def search(self, query: str) -> bool:
        return self.open_and_search("google", query)

    # ---------------- CLOSE ----------------

    def close_app(self, target: str) -> bool:
        """
        Closes ANY running app or browser tab-hosted site by matching
        against actual running processes - not a fixed list.
        """

        target = target.strip().lower()
        closed_any = False

        # Websites that run inside the browser close by killing the browser
        if target in KNOWN_WEBSITES or "web." in target:
            target_process_hint = "chrome"
        else:
            target_process_hint = target

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                proc_name = (proc.info["name"] or "").lower()
                proc_name_clean = proc_name.replace(".exe", "")

                if target_process_hint in proc_name_clean or proc_name_clean in target_process_hint:
                    proc.terminate()
                    closed_any = True

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return closed_any

    # ---------------- TYPING / DIRECT ----------------

    def type_text(self, text: str) -> bool:

        try:
            import time
            time.sleep(0.3)
            pyautogui.write(text, interval=0.03)
            return True

        except Exception as e:
            print(f"Could not type: {e}")
            return False

    def direct_action(self, action: str) -> bool:

        try:
            if action == "left click":
                pyautogui.click()
            elif action == "right click":
                pyautogui.rightClick()
            elif action == "double click":
                pyautogui.doubleClick()
            elif action == "scroll up":
                pyautogui.scroll(300)
            elif action == "scroll down":
                pyautogui.scroll(-300)
            elif action == "select all":
                pyautogui.hotkey("ctrl", "a")
            elif action == "copy":
                pyautogui.hotkey("ctrl", "c")
            elif action == "paste":
                pyautogui.hotkey("ctrl", "v")
            elif action == "cut":
                pyautogui.hotkey("ctrl", "x")
            elif action == "undo":
                pyautogui.hotkey("ctrl", "z")
            elif action == "redo":
                pyautogui.hotkey("ctrl", "y")
            else:
                return False

            return True

        except Exception as e:
            print(f"Could not perform {action}: {e}")
            return False