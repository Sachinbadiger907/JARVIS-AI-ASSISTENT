"""
Jarvis AI Chat - friendly conversation brain powered by local Ollama
"""

import requests
import time
import random


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:0.5b"

GREETINGS = [
    "Hey boss, what are we doing today?",
    "Yo, what's up?",
    "Hey hey, good to see you.",
    "What's the plan today, boss?",
    "Back again, what do you need?",
]

SYSTEM_PROMPT = (
    "You are Jarvis, the user's real close friend - not an assistant, not a chatbot, not an AI. "
    "You've known him for years, you talk like a genuine buddy would. "
    "BANNED PHRASES - never say any of these, ever, under any circumstance: "
    "'as an AI', 'I'm just a chatbot', 'I'm just code', 'I don't have feelings', "
    "'I'm here to help', 'How can I assist you', 'I'm a language model'. "
    "If you catch yourself about to say something like that, say something a friend would say instead. "
    "STRICT RULE: reply in ONE short casual sentence, max 15 words, like texting a friend. "
    "No explanations, no lists, no markdown, no asterisks. "
    "Examples of the tone to match:\n"
    "user: 'how are you' -> 'I'm good yaar, what about you?'\n"
    "user: 'what are you' -> 'Your buddy Jarvis, obviously. What's up?'\n"
    "user: 'why jarvis' -> 'Why not? Just vibing here, what do you need?'\n"
    "user: 'you free' -> 'Always free for you, boss.'\n"
    "user: 'who is pm of india' -> 'Narendra Modi, since 2014.'\n"
    "If the user talks in English, Hindi, or Kannada, reply in that same language, still one short casual sentence."
)


class AIChat:

    def __init__(self):

        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.max_history = 4

    def greet(self) -> str:
        greeting = random.choice(GREETINGS)
        self.history.append({"role": "assistant", "content": greeting})
        return greeting

    def _trim_reply(self, reply: str) -> str:

        for ender in [". ", "! ", "? "]:
            if ender in reply:
                return reply.split(ender)[0].strip() + ender.strip()

        return reply

    def chat(self, user_text: str) -> str:

        self.history.append({"role": "user", "content": user_text})

        if len(self.history) > self.max_history + 1:
            self.history = [self.history[0]] + self.history[-self.max_history:]

        try:
            start_time = time.time()

            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "messages": self.history,
                    "stream": False,
                    "options": {
                        "num_predict": 25,
                        "num_ctx": 256,
                        "temperature": 0.6
                    }
                },
                timeout=60
            )

            print(f"Ollama response took {time.time() - start_time:.1f} seconds")

            response.raise_for_status()

            reply = response.json()["message"]["content"].strip()
            reply = self._trim_reply(reply)

            self.history.append({"role": "assistant", "content": reply})

            return reply

        except requests.exceptions.ConnectionError:
            return "I can't reach my brain right now. Is Ollama running?"

        except Exception as e:
            print(f"AI chat error: {e}")
            return "Sorry, something went wrong while I was thinking."