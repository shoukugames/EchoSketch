#!/usr/bin/env python3
# EchoSketch - asset pipeline
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Write CREDITS.md from assets/sounds/credits.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from echosketch import CREATORS, EMAIL, RELEASE_DATE, WEBSITE, __version__  # noqa: E402
from echosketch.catalog import CATEGORIES, ITEMS  # noqa: E402


def main():
    credits = json.loads((ROOT / "assets" / "sounds" / "credits.json").read_text(encoding="utf-8"))
    out = [
        "# EchoSketch Credits", "",
        f"**EchoSketch v{__version__}** — released {RELEASE_DATE}", "",
        f"Created by **{' & '.join(CREATORS)}**  ", f"Website: <{WEBSITE}>  ", f"Email: <{EMAIL}>", "",
        "EchoSketch is licensed under the GNU General Public License v3.0 (see `LICENSE`).",
        "The third-party assets below keep their own licences, all of which allow redistribution",
        "with this GPL-3.0 program.", "",
        "## Pictures", "",
        "Cartoon pictures: [Twemoji](https://github.com/jdecked/twemoji) — Copyright 2019 Twitter, Inc and other",
        "contributors. Graphics licensed under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/).", "",
        "## Fonts", "",
        "- [Andika](https://software.sil.org/andika/) — SIL International, SIL Open Font License 1.1 "
        "(`assets/fonts/Andika-OFL.txt`)",
        "- [Fredoka](https://github.com/hafontia-zz/Fredoka) — Milena Brandão, SIL Open Font License 1.1 "
        "(`assets/fonts/Fredoka-OFL.txt`)",
        "- [M PLUS Rounded 1c](https://fonts.google.com/specimen/M+PLUS+Rounded+1c) (Japanese) — Coji Morishita, "
        "M+ Fonts Project, SIL Open Font License 1.1 (`assets/fonts/MPLUSRounded1c-OFL.txt`)", "",
        "## Voice", "",
        "Spoken words, letters, kana and phrases were generated with the",
        "[Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) neural text-to-speech model (Apache-2.0)",
        "via [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx): voice `af_heart` for English and",
        "`jf_alpha` for Japanese, with Japanese pronunciation from",
        "[misaki](https://github.com/hexgrad/misaki) (Apache-2.0).", "",
        "## Music and sound effects", "",
        "The ambient background music and interface sound effects are original, synthesised by",
        "`tools/make_music.py`, and are part of EchoSketch (GPL-3.0).", "",
        "## Real-world sound recordings", "",
        "From [Wikimedia Commons](https://commons.wikimedia.org/). Each clip was trimmed and loudness-",
        "normalised by `tools/fetch_sounds.py`; follow the link for the original and full licence.", "",
    ]
    for cat, title in CATEGORIES.items():
        out += [f"### {title}", "", "| Sound | Original file | Author | Licence |", "|---|---|---|---|"]
        for key, item in ITEMS.items():
            if item["category"] != cat:
                continue
            for src in credits.get(key, []):
                author = src["author"].replace("|", "/").replace("\n", " ")
                lic = src["license"]
                if src.get("license_url"):
                    lic = f"[{lic}]({src['license_url']})"
                out.append(f"| {item['name']} | [{src['file']}]({src['page']}) | {author} | {lic} |")
        out.append("")
    (ROOT / "CREDITS.md").write_text("\n".join(out), encoding="utf-8")
    print("CREDITS.md written")


if __name__ == "__main__":
    main()
