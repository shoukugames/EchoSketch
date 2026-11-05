# EchoSketch - a sound matching game for young children
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Sound loading, voice sequencing and background-music ducking."""
import pygame

from . import i18n
from .paths import ASSETS

MUSIC_VOLUME = 0.32
MUSIC_DUCKED = 0.07


class Audio:
    def __init__(self, music_on=True):
        self.ok = True
        try:
            pygame.mixer.pre_init(44100, -16, 2, 1024)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
            pygame.mixer.set_reserved(2)
        except pygame.error:
            self.ok = False
        self._cache = {}
        self.voice_ch = pygame.mixer.Channel(0) if self.ok else None
        self.clue_ch = pygame.mixer.Channel(1) if self.ok else None
        self.music_on = music_on
        self._music_vol = 0.0
        self._queue = []
        self._wait = 0.0
        if self.ok:
            try:
                pygame.mixer.music.load(str(ASSETS / "music" / "ambient_loop.ogg"))
                pygame.mixer.music.set_volume(0.0)
                pygame.mixer.music.play(-1, fade_ms=0)
            except pygame.error:
                pass

    # ---- loading ---------------------------------------------------------
    def sound(self, rel):
        if not self.ok:
            return None
        if rel not in self._cache:
            try:
                self._cache[rel] = pygame.mixer.Sound(str(ASSETS / rel))
            except (pygame.error, FileNotFoundError):
                self._cache[rel] = None
        return self._cache[rel]

    def clue(self, item):
        return self.sound(f"sounds/{item}.ogg")

    @staticmethod
    def _voice_dir():
        return "voice/ja/" if i18n.lang() == "ja" else "voice/"

    def word(self, item):
        return self.sound(f"{self._voice_dir()}word_{item}.ogg")

    def unit(self, unit):
        """One spelling unit: a letter in English, a kana in Japanese."""
        return self.sound("voice/" + i18n.unit_file(unit))

    def say(self, key):
        return self.sound(f"{self._voice_dir()}say_{key}.ogg")

    # ---- playback --------------------------------------------------------
    def sfx(self, name, volume=1.0):
        s = self.sound(f"sfx/{name}.ogg")
        if s:
            ch = s.play()
            if ch:
                ch.set_volume(volume)

    def play_clue(self, item):
        s = self.clue(item)
        if s and self.clue_ch:
            self.clue_ch.play(s)

    def sequence(self, steps):
        """Run steps one after another, replacing any running sequence.

        Steps: ("voice", Sound), ("clue", item), ("wait", secs), ("call", fn).
        """
        self.stop_voice()
        self._queue = list(steps)
        self._wait = 0.0

    def stop_voice(self):
        self._queue = []
        self._wait = 0.0
        if self.voice_ch:
            self.voice_ch.stop()
        if self.clue_ch:
            self.clue_ch.stop()

    @property
    def busy(self):
        return bool(self._queue) or self._wait > 0 or self.talking

    @property
    def talking(self):
        return bool(self.ok and (self.voice_ch.get_busy() or self.clue_ch.get_busy()))

    def update(self, dt):
        if self._wait > 0:
            self._wait -= dt
        while self._queue and self._wait <= 0:
            kind, val = self._queue.pop(0)
            if kind == "voice":
                if val is not None and self.voice_ch:
                    self.voice_ch.play(val)
                    self._wait = val.get_length() + 0.08
            elif kind == "clue":
                s = self.clue(val)
                if s and self.clue_ch:
                    self.clue_ch.play(s)
                    self._wait = s.get_length() + 0.15
            elif kind == "wait":
                self._wait = val
            elif kind == "call":
                val()
        # gently duck the music under speech and clue sounds
        if self.ok:
            target = 0.0 if not self.music_on else (MUSIC_DUCKED if self.talking else MUSIC_VOLUME)
            rate = 1.5 if target < self._music_vol else 0.35
            step = rate * dt
            if abs(target - self._music_vol) <= step:
                self._music_vol = target
            else:
                self._music_vol += step if target > self._music_vol else -step
            pygame.mixer.music.set_volume(self._music_vol)


def spelling_steps(audio, item, on_letter=None, intro=True):
    """Voice steps that say the word, spell it piece by piece (letters in English, kana in
    Japanese), then say it again. on_letter(i) gets the index into i18n.spell_units()."""
    units = i18n.spell_units(i18n.item_name(item))
    steps = []
    if intro:
        steps.append(("voice", audio.word(item)))
        steps.append(("wait", 0.25))
    for i, u in enumerate(units):
        if not i18n.is_spoken(u):
            continue
        if on_letter:
            steps.append(("call", (lambda idx=i: on_letter(idx))))
        steps.append(("voice", audio.unit(u)))
    if on_letter:
        steps.append(("call", lambda: on_letter(-1)))
    steps.append(("wait", 0.2))
    steps.append(("voice", audio.word(item)))
    return steps
