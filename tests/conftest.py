"""Shared test fixtures.

The one real file the suite touches is a generated sine wave rather than a
committed music file: it keeps binary audio (and any licensing question that
comes with it) out of the repo, and it's deterministic, so a failure is always
the code's fault and never the fixture's.
"""

import math
import struct
import wave
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TONE_PATH = REPO_ROOT / "assets" / "test_tone.wav"


def generate_test_tone(path=TEST_TONE_PATH, seconds=2, freq=440, rate=44100):
    """Write a mono 16-bit sine wave to ``path`` using only the stdlib."""
    path.parent.mkdir(parents=True, exist_ok=True)

    amplitude = int(32767 * 0.3)  # headroom, so the tone isn't jarring to hear
    frames = b"".join(
        struct.pack("<h", int(amplitude * math.sin(2 * math.pi * freq * i / rate)))
        for i in range(int(seconds * rate))
    )

    with wave.open(str(path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(rate)
        wav_file.writeframes(frames)

    return path


@pytest.fixture(scope="session")
def test_tone():
    """Path to the generated test tone, created once per session if missing."""
    if not TEST_TONE_PATH.exists():
        generate_test_tone()
    return TEST_TONE_PATH
