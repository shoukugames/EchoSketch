#!/usr/bin/env python3
# EchoSketch - asset pipeline
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Synthesise the original ambient background music (a seamless loop)
and the small interface sound effects.  Everything here is generated
from scratch, so it is covered by the project's GPL-3.0 licence.
Requires: numpy, ffmpeg."""
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 44100
rng = np.random.default_rng(20261105)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env_adsr(n, a, r, peak=1.0):
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / a) if a > 0 else np.ones(n)
    rel = np.clip((n / SR - t) / r, 0, 1)
    return peak * e * np.sin(rel * np.pi / 2) ** 2


def pad_voice(freq, n):
    """Warm, slightly detuned additive pad note."""
    t = np.arange(n) / SR
    out = np.zeros(n)
    for detune in (-0.12, 0.0, 0.11):
        f = freq * 2 ** (detune / 12)
        ph = rng.uniform(0, 2 * np.pi)
        for h, amp in ((1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)):
            out += amp * np.sin(2 * np.pi * f * h * t + ph * h)
    # slow tremolo for movement
    out *= 1 + 0.15 * np.sin(2 * np.pi * rng.uniform(0.07, 0.15) * t + rng.uniform(0, 6))
    return out / 4.5


def bell(freq, seconds, bright=1.0):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for ratio, amp, dec in ((1, 1, 1.6), (2.0, 0.4 * bright, 0.9), (3.01, 0.18 * bright, 0.5), (4.2, 0.08 * bright, 0.3)):
        out += amp * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t / dec)
    out *= np.minimum(1, t / 0.004)
    return out


def reverb(x, seconds=3.2, mix=0.45):
    """Stereo FFT convolution reverb with a synthetic hall impulse."""
    n_ir = int(seconds * SR)
    t = np.arange(n_ir) / SR
    out = []
    for ch in range(2):
        ir = rng.standard_normal(n_ir) * np.exp(-t * 6.9 / seconds)
        # darken the tail
        ir = np.convolve(ir, np.ones(12) / 12, "same")
        ir[:int(0.012 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        size = 1 << int(np.ceil(np.log2(len(x) + n_ir)))
        wet = np.fft.irfft(np.fft.rfft(x[:, ch], size) * np.fft.rfft(ir, size), size)[:len(x) + n_ir]
        dry = np.concatenate([x[:, ch], np.zeros(n_ir)])
        out.append((1 - mix) * dry + mix * wet)
    return np.stack(out, axis=1)


def write(path, stereo):
    stereo = np.asarray(stereo, dtype=np.float32)
    if stereo.ndim == 1:
        stereo = np.stack([stereo, stereo], axis=1)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "libvorbis", "-q:a", "6", str(path)], input=stereo.tobytes(), check=True)
    print("wrote", path.relative_to(ROOT))


def make_music():
    # Gentle progression in D major / lydian colours, 8 s per chord.
    chords = [
        [50, 57, 62, 64, 69],   # Dadd9
        [47, 54, 59, 62, 66],   # Bm7
        [43, 55, 59, 62, 66],   # Gmaj7
        [45, 52, 57, 61, 64],   # A6sus-ish
        [50, 57, 62, 66, 71],   # D6/9
        [52, 59, 62, 66, 71],   # Em9
        [43, 50, 59, 62, 67],   # G add
        [45, 52, 57, 61, 66],   # Asus
    ]
    chord_len = 8.0
    total = chord_len * len(chords)        # 64 s loop
    n_total = int(total * SR)
    tail = int(6 * SR)
    mix = np.zeros((n_total + tail, 2))
    for ci, chord in enumerate(chords):
        start = int(ci * chord_len * SR)
        n = int((chord_len + 3.0) * SR)     # overlap into next chord
        for k, note in enumerate(chord):
            v = pad_voice(midi(note), n) * env_adsr(n, 2.5, 3.5, 0.11 if k else 0.15)
            pan = 0.5 + 0.35 * np.sin(k * 1.7 + ci)
            mix[start:start + n, 0] += v * (1 - pan)
            mix[start:start + n, 1] += v * pan
        # soft sparkling pentatonic chimes above the pad
        scale = [74, 76, 78, 81, 83, 86, 88]
        for _ in range(rng.integers(2, 5)):
            when = start + int(rng.uniform(0.5, chord_len - 1) * SR)
            note = scale[rng.integers(len(scale))]
            b = bell(midi(note), 3.5, bright=0.6) * rng.uniform(0.035, 0.06)
            pan = rng.uniform(0.2, 0.8)
            end = min(len(mix), when + len(b))
            mix[when:end, 0] += b[:end - when] * (1 - pan)
            mix[when:end, 1] += b[:end - when] * pan
    # very quiet low "ocean" noise bed for warmth
    noise = rng.standard_normal(len(mix))
    noise = np.convolve(noise, np.ones(400) / 400, "same")
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * np.arange(len(mix)) / SR / 16)
    mix += (noise * swell * 0.05)[:, None]

    wet = reverb(mix, 4.0, 0.5)
    # wrap the tail back onto the start so the loop is seamless
    loop = wet[:n_total].copy()
    over = wet[n_total:]
    loop[:len(over)] += over
    loop /= np.max(np.abs(loop)) / 0.6
    write(ROOT / "assets" / "music" / "ambient_loop.ogg", loop)


def make_sfx():
    out = ROOT / "assets" / "sfx"
    out.mkdir(parents=True, exist_ok=True)

    def seq(notes, step, length, bright=1.0, gain=0.5):
        n = int((step * len(notes) + length) * SR)
        buf = np.zeros(n)
        for i, note in enumerate(notes):
            b = bell(midi(note), length, bright)
            s = int(i * step * SR)
            buf[s:s + len(b)] += b
        buf = reverb(np.stack([buf, buf], 1), 1.2, 0.25)
        return buf / np.max(np.abs(buf)) * gain

    write(out / "correct.ogg", seq([72, 76, 79, 84], 0.09, 1.2, 1.0, 0.6))
    write(out / "levelup.ogg", seq([67, 72, 76, 79, 84, 88, 91], 0.11, 1.6, 1.0, 0.6))
    write(out / "star.ogg", seq([88, 95], 0.07, 0.8, 0.8, 0.45))
    # soft, friendly "wrong" sound: two low, round notes going down
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    f = np.where(t < 0.22, midi(57), midi(53))
    wob = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-((t % 0.22) / 0.25)) * np.minimum(1, t / 0.01)
    wob *= np.clip((0.7 - t) / 0.2, 0, 1)
    wob = reverb(np.stack([wob, wob], 1), 0.8, 0.2)
    write(out / "wrong.ogg", wob / np.max(np.abs(wob)) * 0.45)
    # button pop
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    pop = np.sin(2 * np.pi * (600 + 900 * np.exp(-t * 40)) * t) * np.exp(-t * 35)
    write(out / "pop.ogg", pop * 0.5)
    # card whoosh
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    wh = rng.standard_normal(n) * np.sin(np.pi * t / t[-1]) ** 2
    wh = np.convolve(wh, np.ones(30) / 30, "same")
    write(out / "whoosh.ogg", wh / np.max(np.abs(wh)) * 0.25)
    # gentle tick used for the last 10 seconds
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    write(out / "tick.ogg", np.sin(2 * np.pi * 1400 * t) * np.exp(-t * 80) * 0.25)


if __name__ == "__main__":
    (ROOT / "assets" / "music").mkdir(parents=True, exist_ok=True)
    make_sfx()
    make_music()
