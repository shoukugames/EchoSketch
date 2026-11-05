#!/usr/bin/env python3
# EchoSketch - asset pipeline
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pre-render every spoken word, letter, kana and phrase with Kokoro, a neural TTS model
(https://huggingface.co/hexgrad/Kokoro-82M, Apache-2.0), the same engine BeatClap uses.
English uses the voice af_heart (as in BeatClap), Japanese uses jf_alpha. The game only
plays the resulting .ogg files (English in assets/voice, Japanese in assets/voice/ja).

    pip install kokoro-onnx==0.4.9 soundfile "misaki[ja]" unidic-lite
    pip uninstall unidic      # misaki pulls in the full UniDic, which needs a 500 MB download;
                              # fugashi then falls back to unidic-lite
    # model files: https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
    tools/make_voice.py --lang en --model kokoro-v1.0.onnx --voices voices-v1.0.bin [--espeak-data DIR]
    tools/make_voice.py --lang ja --model kokoro-v1.0.onnx --voices voices-v1.0.bin [--espeak-data DIR]

Japanese text is turned into phonemes by misaki's Japanese G2P (pyopenjtalk) and fed to
Kokoro as phonemes, since espeak's Japanese support is too weak.

--espeak-data: a real (not symlinked) copy of espeakng_loader's espeak-ng-data folder at a
short path, if espeak-ng can't find its data inside a deep venv.
Needs ffmpeg for trimming, loudness normalising and OGG encoding.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from echosketch import i18n  # noqa: E402
from echosketch.catalog import ITEMS, LEVELS  # noqa: E402

# Letter names given as phonemes so each one is said as the letter's name, never a
# guessed word or a schwa ("a" as "uh").
LETTERS = dict(
    a="ˈeɪ", b="bˈiː", c="sˈiː", d="dˈiː", e="ˈiː", f="ˈɛf", g="dʒˈiː", h="ˈeɪtʃ",
    i="ˈaɪ", j="dʒˈeɪ", k="kˈeɪ", l="ˈɛl", m="ˈɛm", n="ˈɛn", o="ˈoʊ", p="pˈiː",
    q="kjˈuː", r="ˈɑːɹ", s="ˈɛs", t="tˈiː", u="jˈuː", v="vˈiː", w="dˈʌbəljˌuː",
    x="ˈɛks", y="wˈaɪ", z="zˈiː",
)
PHRASES = {
    "listen": "Listen carefully! What makes this sound?",
    "great": "Great job!",
    "awesome": "Awesome!",
    "yay": "You got it!",
    "superstar": "Super star!",
    "tryagain": "Oops! Try again.",
    "notquite": "Not quite. Listen again.",
    "timeup": "Time is up! The answer is.",
    "levelup": "Hooray! You finished the level!",
    "welcome": "Welcome to Echo Sketch! Let's listen and learn.",
    "whoplays": "Who is playing today?",
    "pick": "Pick a level!",
}
# Japanese, in kana with spaces between phrases so the reading is unambiguous
PHRASES_JA = {
    "listen": "よく きいてね! これは なんの おと かな?",
    "great": "すごい!",
    "awesome": "やったね!",
    "yay": "せいかい!",
    "superstar": "かんぺき!",
    "tryagain": "おしい! もういちど!",
    "notquite": "ちがうよ。 もういちど きいてね。",
    "timeup": "じかんぎれ! こたえは。",
    "levelup": "やったー! レベル クリア!",
    "welcome": "エコースケッチへ ようこそ! いっしょに きいて まなぼう!",
    "whoplays": "きょうは だれが あそぶ?",
    "pick": "レベルを えらんでね!",
}
# Kana whose reading on their own differs from the reading misaki picks: alone, は is
# taken as the topic particle "wa", but when spelling はち it must be "ha".
UNIT_PHONEMES_JA = {"は": "ha", "ん": "ɴː", "ン": "ɴː"}   # a bare ん is too short to hear
NUMBERS_JA = ["いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち"]
WORD_SPEED = 0.9      # a touch slower than normal for young listeners
PHRASE_SPEED = 0.95


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=i18n.LANGS, default="en")
    ap.add_argument("--model", required=True)
    ap.add_argument("--voices", required=True)
    ap.add_argument("--espeak-data")
    ap.add_argument("--voice", help="Kokoro voice (default af_heart for en, jf_alpha for ja)")
    args = ap.parse_args()
    voice = args.voice or ("jf_alpha" if args.lang == "ja" else "af_heart")

    from kokoro_onnx import EspeakConfig, Kokoro
    cfg = EspeakConfig(data_path=args.espeak_data) if args.espeak_data else None
    kokoro = Kokoro(args.model, args.voices, espeak_config=cfg)
    out = ROOT / "assets" / "voice" / ("ja" if args.lang == "ja" else "")
    out.mkdir(parents=True, exist_ok=True)
    g2p = None
    if args.lang == "ja":
        from misaki import ja
        g2p = ja.JAG2P()

    def say(text, path, speed, phonemes=False):
        # A closing stop gives a clean, falling end; without it Kokoro sometimes trails an
        # extra vowel onto short words ("dog" came out as "doggy").
        if g2p and not phonemes:
            text = g2p(text)[0]
            phonemes = True
        if text[-1] not in ".!?":
            text += "."
        x, sr = kokoro.create(text, voice=voice, speed=speed, is_phonemes=phonemes,
                              lang="ja" if g2p else "en-us")
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            sf.write(tmp.name, np.clip(x, -1, 1), sr, subtype="PCM_16")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp.name, "-af",
                            "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                            "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                            "loudnorm=I=-16:TP=-1.5,"
                            "aformat=sample_rates=44100",
                            "-ac", "1", "-c:a", "libvorbis", "-q:a", "5", str(path)], check=True)
        print(f"  {path.name:22s} {text}", flush=True)

    if args.lang == "ja":
        i18n.set_lang("ja")
        units = set()
        for key in ITEMS:
            name = i18n.item_name(key)
            say(name + "!", out / f"word_{key}.ogg", WORD_SPEED)
            units.update(u for u in i18n.spell_units(name) if i18n.is_spoken(u))
        for u in sorted(units):
            dest = ROOT / "assets" / "voice" / i18n.unit_file(u)
            if u in UNIT_PHONEMES_JA:
                say(UNIT_PHONEMES_JA[u], dest, WORD_SPEED, phonemes=True)
            else:
                say(i18n.unit_speech(u), dest, WORD_SPEED)
        for key, text in PHRASES_JA.items():
            say(text, out / f"say_{key}.ogg", PHRASE_SPEED)
        for i in range(len(LEVELS)):
            say(f"レベル {NUMBERS_JA[i]}。 {i18n.level_title(i)}!", out / f"level_{i}.ogg", PHRASE_SPEED)
        print("voice files:", len(list(out.glob("*.ogg"))))
        return

    for key, item in ITEMS.items():
        say(item["name"] + "!", out / f"word_{key}.ogg", WORD_SPEED)
    for letter, ipa in LETTERS.items():
        say(ipa, out / f"letter_{letter}.ogg", WORD_SPEED, phonemes=True)
    for key, text in PHRASES.items():
        say(text, out / f"say_{key}.ogg", PHRASE_SPEED)
    for i, lv in enumerate(LEVELS):
        say(f"Level {i + 1}. {lv['title']}!", out / f"level_{i}.ogg", PHRASE_SPEED)
    print("voice files:", len(list(out.glob("*.ogg"))))


if __name__ == "__main__":
    main()
