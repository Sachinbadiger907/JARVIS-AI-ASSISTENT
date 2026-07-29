"""
Jarvis Mobile Server - lets your phone talk to Jarvis over WiFi.
Run this alongside (or instead of) main.py, then open the shown address
in your phone's browser while on the same WiFi network.
"""

from flask import Flask, request, jsonify, render_template_string

from brain.intent import IntentDetector
from brain.actions import ActionExecutor
from brain.ai_chat import AIChat
from brain.code_writer import CodeWriter
from brain.screen_reader import ScreenReader
from brain.whatsapp_sender import WhatsAppSender


app = Flask(__name__)

intent = IntentDetector()
actions = ActionExecutor()
ai_chat = AIChat()
code_writer = CodeWriter()
screen_reader = ScreenReader()
whatsapp_sender = WhatsAppSender()


def handle_command(command: str) -> str:

    detected = intent.detect(command)

    if detected is None:
        return ai_chat.chat(command)

    action = detected["action"]
    target = detected.get("target", "")

    if action == "open":
        success = actions.open_app(target)
        return f"Opened {target}, boss." if success else f"Couldn't open {target}, boss."

    elif action == "open_and_search":
        success = actions.open_and_search(target, detected["query"])
        return "Searching, boss." if success else "Couldn't search that, boss."

    elif action == "search":
        success = actions.search(target)
        return "Searching, boss." if success else "Couldn't search that, boss."

    elif action == "type":
        success = actions.type_text(target)
        return "Done, boss." if success else "Couldn't type that, boss."

    elif action == "direct":
        success = actions.direct_action(target)
        return "Done, boss." if success else "Couldn't do that, boss."

    elif action == "close":
        success = actions.close_app(target)
        return f"Closed {target}, boss." if success else f"Couldn't close {target}, boss."

    elif action == "write_code":
        success = code_writer.generate_and_open(target)
        return "Done, opened it in VS Code, boss." if success else "Sorry, couldn't generate that code, boss."

    elif action == "run_code":
        success = code_writer.run_last_file()
        return "Running it now, boss." if success else "There's no code to run yet, boss."

    elif action == "read_screen":
        return screen_reader.read_and_explain()

    elif action == "send_whatsapp":
        success = whatsapp_sender.send_message(target, detected.get("message", ""))
        return f"Sent it to {target}, boss." if success else f"Couldn't send to {target}, boss."

    else:
        return "Not sure how to do that yet, boss."


PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Jarvis Mobile</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #0a0a0a; color: #fff; font-family: sans-serif;
               text-align: center; padding-top: 60px; }
        button { width: 140px; height: 140px; border-radius: 50%; border: none;
                 background: #2563eb; color: white; font-size: 18px; }
        button.listening { background: #dc2626; }
        #reply { margin-top: 30px; font-size: 18px; padding: 0 20px; min-height: 60px; }
        #heard { color: #888; font-size: 14px; margin-top: 15px; }
    </style>
</head>
<body>
    <h2>Jarvis</h2>
    <button id="micBtn" onclick="startListening()">🎤 Tap to talk</button>
    <div id="heard"></div>
    <div id="reply">Say something to Jarvis</div>

    <script>
        const micBtn = document.getElementById("micBtn");
        const replyDiv = document.getElementById("reply");
        const heardDiv = document.getElementById("heard");

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = "en-IN";
        recognition.interimResults = false;

        function startListening() {
            micBtn.classList.add("listening");
            micBtn.innerText = "Listening...";
            recognition.start();
        }

        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            heardDiv.innerText = "You said: " + text;
            sendCommand(text);
        };

        recognition.onerror = function(event) {
            micBtn.classList.remove("listening");
            micBtn.innerText = "🎤 Tap to talk";
            replyDiv.innerText = "Mic error: " + event.error;
        };

        recognition.onend = function() {
            micBtn.classList.remove("listening");
            micBtn.innerText = "🎤 Tap to talk";
        };

        function sendCommand(text) {
            replyDiv.innerText = "Thinking...";
            fetch("/command", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text })
            })
            .then(res => res.json())
            .then(data => {
                replyDiv.innerText = data.reply;
                speak(data.reply);
            })
            .catch(err => {
                replyDiv.innerText = "Error reaching Jarvis: " + err;
            });
        }

        function speak(text) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "en-IN";
            window.speechSynthesis.speak(utterance);
        }
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/command", methods=["POST"])
def command():
    data = request.get_json()
    text = data.get("text", "")
    reply = handle_command(text)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    print("Jarvis Mobile Server starting...")
    print("On your phone (same WiFi), open the address shown below (not 127.0.0.1 or localhost).")
    app.run(host="0.0.0.0", port=5000)