#!/usr/bin/env python3
# EchoSketch - asset pipeline
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fetch the cartoon pictures (Twemoji, CC-BY 4.0) and render them to
crisp 320px PNGs, and fetch the Andika, Fredoka and M PLUS Rounded 1c (Japanese) fonts
(SIL OFL 1.1).
Requires: rsvg-convert."""
import subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from echosketch.catalog import ITEMS  # noqa: E402

TWEMOJI = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.1.0/assets/svg/{}.svg"
FONTS = {
    "Andika-Bold.ttf": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/andika/Andika-Bold.ttf",
    "Andika-Regular.ttf": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/andika/Andika-Regular.ttf",
    "Andika-OFL.txt": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/andika/OFL.txt",
    "Fredoka.ttf": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/fredoka/Fredoka%5Bwdth,wght%5D.ttf",
    "Fredoka-OFL.txt": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/fredoka/OFL.txt",
    # Japanese; the licence text is assets/fonts/MPLUSRounded1c-OFL.txt (Google Fonts ships none)
    "MPLUSRounded1c-Bold.ttf": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/mplusrounded1c/MPLUSRounded1c-Bold.ttf",
    "MPLUSRounded1c-Medium.ttf": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/mplusrounded1c/MPLUSRounded1c-Medium.ttf",
}
# extra pictures used by the interface itself
UI = {"ui_speaker": "1f50a", "ui_star": "2b50", "ui_trophy": "1f3c6", "ui_ear": "1f442",
      "ui_lock": "1f512", "ui_child": "1f9d2", "ui_parent": "1f468-200d-1f469-200d-1f467",
      "ui_party": "1f389", "ui_clock": "23f1", "ui_sparkle": "2728", "ui_heart": "1f496",
      "ui_question": "2753", "ui_check": "2705", "ui_book": "1f4d6"}
CACHE = ROOT / "build" / "cache"
UA = {"User-Agent": "EchoSketchAssetPipeline/0.1 (https://shoukugames.org/)"}


def fetch(url, dest):
    if not dest.exists():
        dest.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())
        time.sleep(0.3)
    return dest


def main():
    img_out = ROOT / "assets" / "images"
    font_out = ROOT / "assets" / "fonts"
    (CACHE / "svg").mkdir(parents=True, exist_ok=True)
    img_out.mkdir(parents=True, exist_ok=True)
    font_out.mkdir(parents=True, exist_ok=True)
    jobs = {k: v["emoji"] for k, v in ITEMS.items()}
    jobs.update(UI)
    for key, cp in jobs.items():
        svg = fetch(TWEMOJI.format(cp), CACHE / "svg" / f"{cp}.svg")
        subprocess.run(["rsvg-convert", "-w", "320", "-h", "320", "-o", str(img_out / f"{key}.png"), str(svg)],
                       check=True)
        print("image", key)
    for name, url in FONTS.items():
        fetch(url, font_out / name)
        print("font", name)


if __name__ == "__main__":
    main()
