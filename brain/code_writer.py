"""
Jarvis Code Writer - generates code via a local coding model and opens it in VS Code
"""

import os
import re
import sys
import subprocess
import requests


# Maps import names that differ from their actual pip package name
PACKAGE_NAME_FIXES = {
    "cv2": "opencv-python",
    "PIL": "pillow",
    "sklearn": "scikit-learn",
    "yaml": "pyyaml",
    "bs4": "beautifulsoup4",
}


def extract_required_packages(code: str):
    """
    Scans generated Python code for import statements and returns
    only the third-party ones (skips built-in modules like os, sys, math).
    """

    modules = set()

    for line in code.splitlines():
        line = line.strip()

        match = re.match(r"^import (\w+)", line)
        if match:
            modules.add(match.group(1))

        match = re.match(r"^from (\w+) import", line)
        if match:
            modules.add(match.group(1))

    stdlib = getattr(sys, "stdlib_module_names", set())
    third_party = {m for m in modules if m not in stdlib}

    return {PACKAGE_NAME_FIXES.get(m, m) for m in third_party}


def install_packages(packages):

    if not packages:
        return

    print(f"Installing required libraries: {', '.join(packages)}")

    subprocess.run(
        [sys.executable, "-m", "pip", "install", *packages],
        capture_output=True
    )


OLLAMA_URL = "http://localhost:11434/api/chat"
CODE_MODEL = "qwen2.5-coder:1.5b"

CODE_FOLDER = os.path.expandvars(r"%USERPROFILE%\Desktop\Jarvis_Code")

SYSTEM_PROMPT = (
    "You are a coding assistant. Given a request, output ONLY the code. "
    "No explanations, no markdown fences, no comments about what you did. "
    "Just the raw code that fulfils the request, ready to save directly into a file."
)


def guess_file_extension(description: str) -> str:

    text = description.lower()

    if "html" in text or "website" in text or "webpage" in text:
        return ".html"
    if "css" in text:
        return ".css"
    if "javascript" in text or " js " in text:
        return ".js"
    if "java" in text and "javascript" not in text:
        return ".java"
    if "c++" in text or "cpp" in text:
        return ".cpp"
    if " c " in text or text.startswith("c "):
        return ".c"

    return ".py"  # default


def clean_code_output(raw: str) -> str:

    # Strip markdown code fences if the model added them anyway
    raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw.strip())
    raw = re.sub(r"```$", "", raw.strip())
    return raw.strip()


WEBSITE_SYSTEM_PROMPT = (
    "You are a web developer. Given a website request, output THREE separate code blocks "
    "in this EXACT format, nothing else, no explanations:\n\n"
    "----HTML----\n"
    "(the full html code here, linking to style.css and script.js)\n"
    "----CSS----\n"
    "(the full css code here)\n"
    "----JS----\n"
    "(the full javascript code here)"
)


def is_website_request(description: str) -> bool:
    text = description.lower()
    return "website" in text or "webpage" in text or "web page" in text


def split_website_code(raw: str):
    """
    Pulls out HTML/CSS/JS sections. Never crashes - falls back to putting
    everything in the HTML file if the model didn't follow the exact format.
    """

    def extract(start_marker, end_marker=None):
        pattern = re.escape(start_marker) + r"(.*?)" + (re.escape(end_marker) if end_marker else r"$")
        match = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    html = extract("----HTML----", "----CSS----")
    css = extract("----CSS----", "----JS----")
    js = extract("----JS----")

    if not html and not css and not js:
        # Model ignored the format entirely - just dump everything into HTML
        html = raw.strip()

    return clean_code_output(html), clean_code_output(css), clean_code_output(js)


class CodeWriter:

    def __init__(self):
        self.last_file = None
        self.last_extension = None

    def generate_website(self, description: str) -> bool:

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": CODE_MODEL,
                    "messages": [
                        {"role": "system", "content": WEBSITE_SYSTEM_PROMPT},
                        {"role": "user", "content": description}
                    ],
                    "stream": False,
                    "options": {"temperature": 0.3}
                },
                timeout=90
            )

            response.raise_for_status()

            raw = response.json()["message"]["content"]

            html_part, css_part, js_part = split_website_code(raw)

            safe_name = re.sub(r"[^a-z0-9]+", "_", description.lower()).strip("_")[:40]
            site_folder = os.path.join(CODE_FOLDER, safe_name or "jarvis_website")
            os.makedirs(site_folder, exist_ok=True)

            index_path = os.path.join(site_folder, "index.html")
            css_path = os.path.join(site_folder, "style.css")
            js_path = os.path.join(site_folder, "script.js")

            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html_part)
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(css_part)
            with open(js_path, "w", encoding="utf-8") as f:
                f.write(js_part)

            subprocess.Popen(["cmd", "/c", "code", site_folder])

            self.last_file = index_path
            self.last_extension = ".html"

            return True

        except requests.exceptions.ConnectionError:
            print("Could not reach Ollama for code generation.")
            return False

        except Exception as e:
            print(f"Website generation error: {e}")
            return False

    def generate_and_open(self, description: str) -> bool:

        if is_website_request(description):
            return self.generate_website(description)

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": CODE_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": description}
                    ],
                    "stream": False,
                    "options": {"temperature": 0.3}
                },
                timeout=90
            )

            response.raise_for_status()

            code = clean_code_output(response.json()["message"]["content"])

            os.makedirs(CODE_FOLDER, exist_ok=True)

            extension = guess_file_extension(description)

            safe_name = re.sub(r"[^a-z0-9]+", "_", description.lower()).strip("_")[:40]
            filename = f"{safe_name or 'jarvis_code'}{extension}"
            filepath = os.path.join(CODE_FOLDER, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)

            subprocess.Popen(["cmd", "/c", "code", filepath])

            self.last_file = filepath
            self.last_extension = extension

            return True

        except requests.exceptions.ConnectionError:
            print("Could not reach Ollama for code generation.")
            return False

        except Exception as e:
            print(f"Code generation error: {e}")
            return False

    def run_last_file(self) -> bool:

        if not self.last_file or not os.path.exists(self.last_file):
            print("No recently generated file to run.")
            return False

        try:
            if self.last_extension == ".py":

                with open(self.last_file, "r", encoding="utf-8") as f:
                    code = f.read()

                packages = extract_required_packages(code)
                install_packages(packages)

                subprocess.Popen(
                    ["cmd", "/c", "start", "cmd", "/k", f'python "{self.last_file}"']
                )
                return True

            elif self.last_extension == ".js":
                subprocess.Popen(
                    ["cmd", "/c", "start", "cmd", "/k", f'node "{self.last_file}"']
                )
                return True

            elif self.last_extension == ".html":
                os.startfile(self.last_file)
                return True

            else:
                print(f"Don't know how to run {self.last_extension} files yet.")
                return False

        except Exception as e:
            print(f"Run error: {e}")
            return False