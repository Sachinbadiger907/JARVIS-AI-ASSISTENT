"""
Run this ONCE to teach Jarvis what YOUR voice sounds like.
After this, Jarvis will ignore everyone else's voice automatically.

This version waits until you actually start talking to begin recording
(instead of a fixed timer), which gives a much cleaner voice sample.
"""

import os
import speech_recognition as sr
from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np

PROFILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_profile.npy")


def main():
    print("=" * 50)
    print("VOICE ENROLLMENT")
    print("=" * 50)
    print("\nWe'll record 2 samples for better accuracy.")
    print("Each time, just talk naturally for a few sentences once it says 'Listening...'")

    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.5

    encoder = VoiceEncoder()
    embeddings = []

    for sample_num in range(1, 3):
        input(f"\nSample {sample_num}/2 - Press Enter, then start talking right after...")

        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening... (talk now, describe your day or anything for 5-10 seconds)")
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=12)

        wav_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "enroll_temp.wav")
        with open(wav_path, "wb") as f:
            f.write(audio.get_wav_data())

        print("Processing...")
        wav = preprocess_wav(wav_path)
        embedding = encoder.embed_utterance(wav)
        embeddings.append(embedding)

        os.remove(wav_path)

    # Average the samples for a more robust, reliable profile
    final_embedding = np.mean(embeddings, axis=0)

    np.save(PROFILE_PATH, final_embedding)

    print(f"\nDone! Your voice profile is saved (built from 2 samples).")
    print("Jarvis will now only respond to your voice.")


if __name__ == "__main__":
    main()