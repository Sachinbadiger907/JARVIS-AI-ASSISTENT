"""
Jarvis Voice ID - checks if the speaker is YOU before acting on any command.
"""

import os
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

PROFILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "voice_profile.npy")
MATCH_THRESHOLD = 0.65  # lower = more lenient, higher = stricter

_encoder = None


def _get_encoder():
    global _encoder
    if _encoder is None:
        _encoder = VoiceEncoder()
    return _encoder


def is_enrolled() -> bool:
    return os.path.exists(PROFILE_PATH)


def is_matching_voice(wav_path: str) -> bool:
    """
    Returns True if the given audio matches the enrolled voice profile.
    If no profile has been enrolled yet, allows everyone through (fail-open)
    so you're never accidentally locked out before running enroll_voice.py.
    """

    if not is_enrolled():
        return True

    try:
        start_time = __import__("time").time()

        profile = np.load(PROFILE_PATH)

        encoder = _get_encoder()
        wav = preprocess_wav(wav_path)
        embedding = encoder.embed_utterance(wav)

        similarity = np.dot(profile, embedding) / (
            np.linalg.norm(profile) * np.linalg.norm(embedding)
        )

        print(f"Voice ID check took {__import__('time').time() - start_time:.2f} seconds")

        return similarity >= MATCH_THRESHOLD

    except Exception as e:
        print(f"Voice ID error: {e} - allowing through this time.")
        return True