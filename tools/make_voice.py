#!/usr/bin/env python3
# EchoSketch - asset pipeline
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pre-render every spoken word, letter and phrase with Piper TTS using
the public-domain LJSpeech voice, so the game speaks with no TTS engine
installed.  Usage: make_voice.py /path/to/en_US-ljspeech-high.onnx"""
import subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from echosketch.catalog import ITEMS, LEVELS  # noqa: E402

LETTERS = dict(a="ay", b="bee", c="see", d="dee", e="ee", f="eff", g="jee", h="aitch", i="eye", j="jay",
               k="kay", l="ell", m="em", n="en", o="oh", p="pee", q="cue", r="are", s="ess", t="tee",
               u="you", v="vee", w="double you", x="ex", y="why", z="zee")
PHRASES = {
    "listen": "Listen carefully! What makes this sound?",
    "great": "Great job!",
    "awesome": "Awesome!",
    "yay": "You got it!",
    "superstar": "Super star!",
    "tryagain": "Oops! Try again.",
    "notquite": "Not quite. Listen again.",
    "timeup": "Time is up! The answer is.",
    "itsa": "It's a",
    "spell": "Let's spell it!",
    "levelup": "Hooray! You finished the level!",
    "welcome": "Welcome to Echo Sketch! Let's listen and learn.",
    "whoplays": "Who is playing today?",
    "pick": "Pick a level!",
}


def say(model, text, out):
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        subprocess.run(["piper", "-m", model, "-f", tmp.name, "--length-scale", "1.08",
                        "--sentence-silence", "0.1"], input=text.encode(), check=True,
                       capture_output=True)
        # trim leading/trailing silence, normalise, encode to ogg
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp.name, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        "loudnorm=I=-16:TP=-1.5,aformat=sample_rates=44100",
                        "-ac", "1", "-c:a", "libvorbis", "-q:a", "5", str(out)], check=True)


def main():
    model = sys.argv[1]
    out = ROOT / "assets" / "voice"
    out.mkdir(parents=True, exist_ok=True)
    for key, item in ITEMS.items():
        say(model, item["name"] + "!", out / f"word_{key}.ogg")
    for letter, spoken in LETTERS.items():
        say(model, spoken + ".", out / f"letter_{letter}.ogg")
    for key, text in PHRASES.items():
        say(model, text, out / f"say_{key}.ogg")
    for i, lv in enumerate(LEVELS):
        say(model, f"Level {i + 1}. {lv['title']}!", out / f"level_{i}.ogg")
    print("voice files:", len(list(out.glob("*.ogg"))))


if __name__ == "__main__":
    main()
