# EchoSketch - a sound matching game for young children
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Drawing helpers: fonts, pictures, buttons, the animated sky, confetti."""
import math
import random

import pygame

from . import i18n
from .paths import ASSETS

W, H = 1280, 720

INK = (49, 46, 84)
INK_SOFT = (104, 100, 140)
WHITE = (255, 255, 255)
CREAM = (255, 251, 240)
SHADOW = (30, 30, 70)
GOOD = (102, 187, 106)
BAD = (239, 108, 98)
SUN = (255, 202, 40)
SKY_TOP = (126, 203, 255)
SKY_BOTTOM = (214, 240, 255)
PALETTE = [(255, 112, 112), (255, 167, 38), (255, 213, 79), (102, 187, 106),
           (77, 182, 172), (100, 181, 246), (149, 117, 205), (240, 98, 146)]

_fonts = {}
_images = {}


FONT_FILES = {
    "en": {"title": "Fredoka.ttf", "body": "Andika-Bold.ttf", "plain": "Andika-Regular.ttf"},
    # M PLUS Rounded 1c has kana, kanji and Latin, so Japanese text never mixes fonts
    "ja": {"title": "MPLUSRounded1c-Bold.ttf", "body": "MPLUSRounded1c-Bold.ttf",
           "plain": "MPLUSRounded1c-Medium.ttf"},
}
JA_SCALE = 0.86   # full-width kana look bigger than Latin letters at the same size


def font(size, kind="body", lang=None):
    """kind: 'title', 'body' or 'plain'; the font family follows the current language
    unless lang is given."""
    lang = lang or i18n.lang()
    key = (size, kind, lang)
    if key not in _fonts:
        name = FONT_FILES[lang][kind]
        px = max(8, int(size * JA_SCALE)) if lang == "ja" else size
        try:
            f = pygame.font.Font(str(ASSETS / "fonts" / name), px)
        except (OSError, pygame.error):
            f = pygame.font.Font(None, px)
        if kind == "title" and lang == "en":
            f.set_bold(True)
        _fonts[key] = f
    return _fonts[key]


def fit_size(msg, size, max_w, kind="body", lang=None):
    """Largest size <= size at which msg fits in max_w pixels."""
    while size > 10 and font(size, kind, lang).size(str(msg))[0] > max_w:
        size -= 2
    return size


def image(name, size=None):
    key = (name, size)
    if key not in _images:
        if (name, None) not in _images:
            try:
                surf = pygame.image.load(str(ASSETS / "images" / f"{name}.png")).convert_alpha()
            except (pygame.error, FileNotFoundError):
                surf = pygame.Surface((64, 64), pygame.SRCALPHA)
                pygame.draw.circle(surf, PALETTE[0], (32, 32), 30)
            _images[(name, None)] = surf
        base = _images[(name, None)]
        _images[key] = base if size is None else pygame.transform.smoothscale(base, (size, size))
    return _images[key]


def text(surface, msg, size, color, center=None, kind="body", topleft=None, midleft=None,
         outline=None, outline_w=3, shadow=False, alpha=255, max_w=None, lang=None):
    if max_w:
        size = fit_size(msg, size, max_w, kind, lang)
    f = font(size, kind, lang)
    img = f.render(str(msg), True, color)
    if outline:
        o = f.render(str(msg), True, outline)
        base = pygame.Surface((img.get_width() + outline_w * 2, img.get_height() + outline_w * 2), pygame.SRCALPHA)
        for dx in range(-outline_w, outline_w + 1):
            for dy in range(-outline_w, outline_w + 1):
                if dx * dx + dy * dy <= outline_w * outline_w + 1:
                    base.blit(o, (dx + outline_w, dy + outline_w))
        base.blit(img, (outline_w, outline_w))
        img = base
    if shadow:
        sh = f.render(str(msg), True, SHADOW)
        sh.set_alpha(60)
        r = img.get_rect()
        _place(r, center, topleft, midleft)
        surface.blit(sh, r.move(2, 4))
    if alpha < 255:
        img.set_alpha(alpha)
    r = img.get_rect()
    _place(r, center, topleft, midleft)
    surface.blit(img, r)
    return r


def _place(r, center, topleft, midleft):
    if center is not None:
        r.center = center
    elif topleft is not None:
        r.topleft = topleft
    elif midleft is not None:
        r.midleft = midleft


NO_LINE_START = set("、。，．！？!?)）」』】・ー…ぁぃぅぇぉっゃゅょァィゥェォッャュョ:：")


def wrap(msg, size, width, kind="plain"):
    """Break msg into lines no wider than width: at spaces, and inside a word (as Japanese
    needs) when a single word is too wide, never starting a line with closing punctuation."""
    f = font(size, kind)
    lines, cur = [], ""
    for word in msg.split():
        trial = (cur + " " + word).strip()
        if f.size(trial)[0] <= width:
            cur = trial
            continue
        if cur and f.size(word)[0] <= width:
            lines.append(cur)
            cur = word
            continue
        # break inside the word, character by character
        if cur:
            cur += " "
        for ch in word:
            if f.size(cur + ch)[0] <= width or not cur.strip():
                cur += ch
            elif ch in NO_LINE_START and len(cur) > 1:
                lines.append(cur[:-1])
                cur = cur[-1] + ch
            else:
                lines.append(cur.rstrip())
                cur = ch
    if cur:
        lines.append(cur)
    return lines


def lighten(c, amt=0.35):
    return tuple(min(255, int(v + (255 - v) * amt)) for v in c[:3])


def darken(c, amt=0.25):
    return tuple(max(0, int(v * (1 - amt))) for v in c[:3])


def panel(surface, rect, color=CREAM, radius=26, shadow=10, border=None, border_w=4, alpha=255):
    rect = pygame.Rect(rect)
    if shadow:
        sh = pygame.Surface((rect.w + 20, rect.h + 20), pygame.SRCALPHA)
        pygame.draw.rect(sh, (*SHADOW, 50), pygame.Rect(10, 10 + shadow // 2, rect.w, rect.h), border_radius=radius)
        surface.blit(sh, (rect.x - 10, rect.y - 10 + shadow // 2))
    if alpha < 255:
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (*color[:3], alpha), s.get_rect(), border_radius=radius)
        surface.blit(s, rect)
    else:
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, rect, border_w, border_radius=radius)
    return rect


class Button:
    """A chunky, friendly button with hover bounce and press squash."""

    def __init__(self, rect, label="", color=PALETTE[5], icon=None, size=34, on_click=None,
                 text_color=WHITE, radius=None, icon_size=None, sound="pop", label_lang=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.color = color
        self.icon = icon
        self.size = size
        self.on_click = on_click
        self.text_color = text_color
        self.radius = radius if radius is not None else min(self.rect.h // 2, 30)
        self.icon_size = icon_size or int(self.rect.h * 0.62)
        self.hover = 0.0
        self.pressed = False
        self.enabled = True
        self.visible = True
        self.sound = sound
        self.label_lang = label_lang     # draw the label in this language's font

    def handle(self, e, app):
        if not (self.visible and self.enabled):
            return False
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.rect.collidepoint(e.pos):
            self.pressed = True
            return True
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            was = self.pressed
            self.pressed = False
            if was and self.rect.collidepoint(e.pos):
                if self.sound:
                    app.audio.sfx(self.sound, 0.6)
                if self.on_click:
                    self.on_click()
                return True
        return False

    def update(self, dt):
        over = self.visible and self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())
        self.hover += ((1.0 if over else 0.0) - self.hover) * min(1, dt * 12)

    def draw(self, surface):
        if not self.visible:
            return
        lift = int(self.hover * 4) - (3 if self.pressed else 0)
        r = self.rect.move(0, -lift)
        base = self.color if self.enabled else (190, 190, 200)
        depth = 7 if not self.pressed else 3
        pygame.draw.rect(surface, darken(base, 0.28), r.move(0, depth), border_radius=self.radius)
        pygame.draw.rect(surface, lighten(base, 0.12 * self.hover) if self.hover else base, r,
                         border_radius=self.radius)
        hl = pygame.Rect(r.x + 10, r.y + 6, r.w - 20, max(6, r.h // 3))
        s = pygame.Surface(hl.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 55), s.get_rect(), border_radius=self.radius)
        surface.blit(s, hl)
        content = []
        if self.icon:
            content.append(("img", image(self.icon, self.icon_size)))
        size = self.size
        if self.label:
            content.append(("txt", self.label))
            room = r.w - 36 - (self.icon_size + 12 if self.icon else 0)
            size = fit_size(self.label, self.size, room, lang=self.label_lang)
        widths = [c[1].get_width() if c[0] == "img" else font(size, lang=self.label_lang).size(c[1])[0]
                  for c in content]
        total = sum(widths) + 12 * (len(content) - 1)
        x = r.centerx - total // 2
        for (kind, val), w in zip(content, widths):
            if kind == "img":
                surface.blit(val, val.get_rect(midleft=(x, r.centery)))
            else:
                text(surface, val, size, self.text_color, midleft=(x, r.centery + 1),
                     outline=darken(base, 0.35), outline_w=2, lang=self.label_lang)
            x += w + 12


class HoldButton(Button):
    """Must be held down (keeps little ones out of the grown-ups area)."""

    HOLD = 2.0

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.held = 0.0

    def handle(self, e, app):
        if not (self.visible and self.enabled):
            return False
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.rect.collidepoint(e.pos):
            self.pressed = True
            return True
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.pressed = False
            self.held = 0.0
        return False

    def update(self, dt):
        super().update(dt)
        if self.pressed and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.held += dt
            if self.held >= self.HOLD:
                self.pressed = False
                self.held = 0.0
                if self.on_click:
                    self.on_click()
        else:
            self.held = max(0.0, self.held - dt * 2)

    def draw(self, surface):
        super().draw(surface)
        if self.held > 0:
            frac = min(1, self.held / self.HOLD)
            r = self.rect.inflate(14, 14)
            pygame.draw.arc(surface, SUN, r, math.pi / 2, math.pi / 2 + frac * 2 * math.pi, 6)


# ---------------------------------------------------------------------------
# The animated sky that sits behind every screen
# ---------------------------------------------------------------------------

def vertical_gradient(size, top, bottom):
    surf = pygame.Surface(size)
    w, h = size
    for y in range(h):
        t = y / max(1, h - 1)
        c = [int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)]
        pygame.draw.line(surf, c, (0, y), (w, y))
    return surf


def make_cloud(scale=1.0):
    w, h = int(240 * scale), int(120 * scale)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    puffs = [(0.25, 0.62, 0.22), (0.45, 0.45, 0.28), (0.68, 0.55, 0.24), (0.82, 0.68, 0.16), (0.12, 0.72, 0.14)]
    for px, py, pr in puffs:
        pygame.draw.circle(s, (255, 255, 255, 235), (int(px * w), int(py * h)), int(pr * w))
    pygame.draw.rect(s, (255, 255, 255, 235), (int(0.1 * w), int(0.62 * h), int(0.78 * w), int(0.24 * h)),
                     border_radius=int(0.12 * h))
    return s


class Sky:
    def __init__(self, tint=None):
        top = SKY_TOP
        bottom = SKY_BOTTOM
        if tint:
            top = tuple(int(a * 0.75 + b * 0.25) for a, b in zip(SKY_TOP, tint))
        self.bg = vertical_gradient((W, H), top, bottom)
        self.hills = self._hills()
        rnd = random.Random(7)
        self.clouds = []
        for i in range(6):
            sc = rnd.uniform(0.55, 1.1)
            self.clouds.append([rnd.uniform(-200, W), rnd.uniform(20, 300), rnd.uniform(6, 16) * sc,
                                make_cloud(sc)])
        self.t = 0.0
        self.motes = [[rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1.5, 3.5), rnd.uniform(0, 6.28)]
                      for _ in range(26)]

    def _hills(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        layers = [((150, 220, 140), 560, 40, 0.004, 1.0), ((118, 200, 120), 600, 34, 0.006, 2.2),
                  ((96, 180, 105), 640, 26, 0.009, 4.0)]
        for color, base, amp, freq, phase in layers:
            pts = [(0, H)]
            for x in range(0, W + 20, 20):
                pts.append((x, base + amp * math.sin(x * freq + phase) + amp * 0.4 * math.sin(x * freq * 2.7)))
            pts.append((W, H))
            pygame.draw.polygon(s, color, pts)
        return s

    def update(self, dt):
        self.t += dt
        for c in self.clouds:
            c[0] += c[2] * dt
            if c[0] > W + 40:
                c[0] = -c[3].get_width() - 20
        for m in self.motes:
            m[1] -= m[2] * dt * 6
            if m[1] < -10:
                m[1] = H + 10

    def draw(self, surface, hills=True):
        surface.blit(self.bg, (0, 0))
        # the sun with soft rays
        cx, cy = 1140, 90
        for i in range(12):
            a = self.t * 0.15 + i * math.pi / 6
            p1 = (cx + math.cos(a) * 62, cy + math.sin(a) * 62)
            p2 = (cx + math.cos(a) * 86, cy + math.sin(a) * 86)
            pygame.draw.line(surface, (255, 230, 120), p1, p2, 6)
        pygame.draw.circle(surface, (255, 236, 150), (cx, cy), 56)
        pygame.draw.circle(surface, SUN, (cx, cy), 48)
        for x, y, _, img in self.clouds:
            surface.blit(img, (x, y))
        for x, y, r, ph in self.motes:
            a = int(110 + 80 * math.sin(self.t * 2 + ph))
            s = pygame.Surface((int(r * 4), int(r * 4)), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, a), (int(r * 2), int(r * 2)), int(r))
            surface.blit(s, (x, y))
        if hills:
            surface.blit(self.hills, (0, 0))


class Confetti:
    def __init__(self):
        self.bits = []

    def burst(self, x, y, n=80, spread=1.0):
        for _ in range(n):
            a = random.uniform(0, 2 * math.pi)
            v = random.uniform(200, 620) * spread
            self.bits.append([x, y, math.cos(a) * v, math.sin(a) * v - 300, random.choice(PALETTE),
                              random.uniform(5, 11), random.uniform(0, 6.28), random.uniform(-9, 9), 2.6])

    def rain(self, n=120):
        for _ in range(n):
            self.bits.append([random.uniform(0, W), random.uniform(-400, -10), random.uniform(-60, 60),
                              random.uniform(60, 200), random.choice(PALETTE), random.uniform(6, 12),
                              random.uniform(0, 6.28), random.uniform(-6, 6), 6.0])

    def update(self, dt):
        for b in self.bits:
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            b[3] += 600 * dt
            b[2] *= (1 - 1.2 * dt)
            b[6] += b[7] * dt
            b[8] -= dt
        self.bits = [b for b in self.bits if b[8] > 0 and b[1] < H + 30]

    def draw(self, surface):
        for x, y, _, _, c, s, rot, _, _ in self.bits:
            w = abs(math.cos(rot)) * s + 2
            pygame.draw.ellipse(surface, c, (x - w / 2, y - s / 3, w, s * 0.66))


def star_shape(surface, center, r, color, filled=True, width=0):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((center[0] + math.cos(a) * rr, center[1] + math.sin(a) * rr))
    if filled:
        pygame.draw.polygon(surface, darken(color, 0.25), [(x, y + 3) for x, y in pts])
        pygame.draw.polygon(surface, color, pts)
    else:
        pygame.draw.polygon(surface, (210, 210, 225), pts)
        pygame.draw.polygon(surface, (180, 180, 200), pts, 3)


def bob(t, speed=2.0, amount=6.0, phase=0.0):
    return math.sin(t * speed + phase) * amount
