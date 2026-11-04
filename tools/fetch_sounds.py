#!/usr/bin/env python3
# EchoSketch - asset pipeline
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Download the real-world recordings from Wikimedia Commons, cut the
loudest part, normalise loudness and write assets/sounds/<id>.ogg.

Also writes assets/sounds/credits.json with author/licence for each file.
Requires: ffmpeg, numpy.  Downloads are cached in build/cache/.
"""
import html, json, re, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from echosketch.catalog import ITEMS  # noqa: E402

CACHE = ROOT / "build" / "cache" / "sounds"
OUT = ROOT / "assets" / "sounds"
UA = {"User-Agent": "EchoSketchAssetPipeline/0.1 (https://shoukugames.org/)"}
API = "https://commons.wikimedia.org/w/api.php"
SR = 44100
OK_LICENSE = re.compile(r"^(CC0|Public domain|PD|CC BY(-SA)? [0-9.]+)", re.I)


def get(url, tries=6):
    for attempt in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or attempt == tries - 1:
                raise
            time.sleep(10 * (attempt + 1))


def strip_html(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def metadata(titles):
    info = {}
    titles = list(titles)
    for i in range(0, len(titles), 40):
        chunk = titles[i:i + 40]
        q = {"action": "query", "format": "json", "prop": "imageinfo",
             "iiprop": "url|extmetadata", "titles": "|".join("File:" + t for t in chunk)}
        data = json.loads(get(API + "?" + urllib.parse.urlencode(q)))
        norm = {n["to"]: n["from"] for n in data["query"].get("normalized", [])}
        for page in data["query"]["pages"].values():
            title = page["title"]
            orig = norm.get(title, title)[5:]
            if "imageinfo" not in page:
                raise SystemExit(f"missing on Commons: {orig}")
            ii = page["imageinfo"][0]
            m = ii.get("extmetadata", {})
            info[orig] = {
                "file": orig,
                "url": ii["url"],
                "page": ii["descriptionurl"],
                "license": m.get("LicenseShortName", {}).get("value", "?"),
                "license_url": m.get("LicenseUrl", {}).get("value", ""),
                "author": strip_html(m.get("Artist", {}).get("value", "unknown"))[:200],
            }
        time.sleep(2)
    return info


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def loudest_window(x, seconds):
    n = int(seconds * SR)
    if len(x) <= n:
        return x
    env = np.convolve(x.astype(np.float64) ** 2, np.ones(SR // 10), "same")
    csum = np.concatenate([[0], np.cumsum(env)])
    hop = SR // 20
    starts = np.arange(0, len(x) - n, hop)
    best = starts[np.argmax(csum[starts + n] - csum[starts])]
    return x[best:best + n]


def trim_silence(x, thresh=0.06):
    # smoothed envelope so background hiss does not count as "sound"
    win = max(1, SR // 50)
    env = np.sqrt(np.convolve(x.astype(np.float64) ** 2, np.ones(win) / win, "same"))
    idx = np.where(env > thresh * np.max(env))[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - SR // 50)
    b = min(len(x), idx[-1] + SR // 10)
    return x[a:b]


def finish(x):
    x = x - np.mean(x)
    x = trim_silence(x)
    fade = min(len(x) // 4, int(0.04 * SR))
    x[:fade] *= np.linspace(0, 1, fade)
    tail = min(len(x) // 3, int(0.4 * SR))
    x[-tail:] *= np.linspace(1, 0, tail) ** 2
    # loudness: aim for an RMS of -18 dBFS on the loud part, peak <= -1 dBFS
    active = x[np.abs(x) > 0.05 * np.max(np.abs(x))]
    rms = np.sqrt(np.mean(active ** 2)) if len(active) else 1
    x = x * (10 ** (-18 / 20) / rms)
    peak = np.max(np.abs(x))
    if peak > 0.89:
        x = x * (0.89 / peak)
    return x.astype(np.float32)


def encode(x, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "libvorbis", "-q:a", "5", str(out)], input=x.tobytes(), check=True)


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    wanted = {}
    for key, item in ITEMS.items():
        srcs = item["source"] if isinstance(item["source"], list) else [item["source"]]
        wanted[key] = srcs
    allfiles = sorted({s for v in wanted.values() for s in v})
    meta = metadata(allfiles)
    for m in meta.values():
        if not OK_LICENSE.match(m["license"]):
            raise SystemExit(f"licence not GPL-compatible: {m['file']} ({m['license']})")

    credits = {}
    for key, srcs in wanted.items():
        parts = []
        for s in srcs:
            cached = CACHE / re.sub(r"[^\w.-]", "_", s)
            if not cached.exists():
                print("download", s)
                cached.write_bytes(get(meta[s]["url"]))
                time.sleep(1.5)
            parts.append(trim_silence(decode(cached)))
        if len(parts) > 1:
            gap = np.zeros(int(0.3 * SR), dtype=np.float32)
            x = np.concatenate([np.concatenate([p, gap]) for p in parts])
        else:
            x = parts[0]
        x = finish(loudest_window(x, ITEMS[key].get("clip", 5)))
        encode(x, OUT / f"{key}.ogg")
        credits[key] = [meta[s] for s in srcs]
        print(f"{key:12s} {len(x) / SR:4.1f}s  <- {', '.join(srcs)}")
    (OUT / "credits.json").write_text(json.dumps(credits, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
