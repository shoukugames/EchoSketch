# EchoSketch - a sound matching game for young children
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""All the screens of the game."""
import json
import math
import random
import webbrowser
from datetime import datetime

import pygame

from . import CREATORS, EMAIL, WEBSITE, __version__, i18n
from .audio import spelling_steps
from .catalog import CATEGORIES, CHOICES, ITEMS, LEVELS, ROUND_SECONDS
from .i18n import category_name, item_name, level_title, tr
from .paths import ASSETS
from .progress import Progress
from .ui import (BAD, CREAM, GOOD, H, INK, INK_SOFT, PALETTE, SUN, WHITE, W, Button, Confetti,
                 HoldButton, bob, darken, font, image, lighten, panel, star_shape, text, wrap)

AVATARS = ["dog", "cat", "lion", "owl", "frog", "elephant", "chimp", "bee", "duck", "pig", "horse", "wolf"]


def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1 = 1.70158
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


class Scene:
    sky_tint = None

    def __init__(self, app):
        self.app = app
        self.buttons = []
        self.t = 0.0
        self.sky = app.sky(self.sky_tint)

    def back(self):
        pass

    def handle(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.back()
            return
        for b in reversed(self.buttons):
            if b.handle(e, self.app):
                return

    def update(self, dt):
        self.t += dt
        self.sky.update(dt)
        for b in self.buttons:
            b.update(dt)

    def draw(self, s):
        self.sky.draw(s)

    def draw_buttons(self, s):
        for b in self.buttons:
            b.draw(s)

    def corner_buttons(self, back=True):
        """Back, music and fullscreen buttons shared by most screens."""
        if back:
            bb = Button((24, 20, 76, 70), "", PALETTE[6], on_click=self.back)
            bb.tag = "back"
            self.buttons.append(bb)
        self.music_btn = Button((W - 184, 20, 76, 70), "", PALETTE[4], on_click=self.app.toggle_music)
        self.full_btn = Button((W - 100, 20, 76, 70), "", PALETTE[5], on_click=self.app.toggle_fullscreen)
        self.buttons += [self.music_btn, self.full_btn]

    def draw_corner_icons(self, s):
        # simple vector icons for back / music / fullscreen
        for b in self.buttons:
            if getattr(b, "tag", None) == "back":
                c = b.rect.move(0, -int(b.hover * 4)).center
                pygame.draw.polygon(s, WHITE, [(c[0] - 18, c[1]), (c[0] + 4, c[1] - 20), (c[0] + 4, c[1] - 8),
                                               (c[0] + 20, c[1] - 8), (c[0] + 20, c[1] + 8), (c[0] + 4, c[1] + 8),
                                               (c[0] + 4, c[1] + 20)])
        if hasattr(self, "music_btn"):
            c = self.music_btn.rect.move(0, -int(self.music_btn.hover * 4)).center
            pygame.draw.circle(s, WHITE, (c[0] - 9, c[1] + 12), 8)
            pygame.draw.circle(s, WHITE, (c[0] + 13, c[1] + 8), 8)
            pygame.draw.line(s, WHITE, (c[0] - 2, c[1] + 12), (c[0] - 2, c[1] - 16), 4)
            pygame.draw.line(s, WHITE, (c[0] + 20, c[1] + 8), (c[0] + 20, c[1] - 20), 4)
            pygame.draw.line(s, WHITE, (c[0] - 2, c[1] - 16), (c[0] + 20, c[1] - 20), 6)
            if not self.app.audio.music_on:
                pygame.draw.line(s, BAD, (c[0] - 24, c[1] - 24), (c[0] + 24, c[1] + 24), 7)
        if hasattr(self, "full_btn"):
            c = self.full_btn.rect.move(0, -int(self.full_btn.hover * 4)).center
            for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                x, y = c[0] + dx * 18, c[1] + dy * 16
                pygame.draw.line(s, WHITE, (x, y), (x - dx * 12, y), 5)
                pygame.draw.line(s, WHITE, (x, y), (x, y - dy * 12), 5)


# ===========================================================================
# Title screen
# ===========================================================================
class TitleScene(Scene):
    greeted = False

    def __init__(self, app):
        super().__init__(app)
        self.buttons = [
            Button((W // 2 - 170, 368, 340, 104), tr("play"), GOOD, icon="ui_star", size=54, on_click=self.play,
                   radius=52),
            HoldButton((W // 2 - 300, 500, 280, 74), tr("grownups"), PALETTE[6], icon="ui_parent", size=30,
                       on_click=lambda: self.app.go(ParentsScene(self.app))),
            Button((W // 2 + 20, 500, 280, 74), tr("credits"), PALETTE[1], icon="ui_book", size=30,
                   on_click=lambda: self.app.go(CreditsScene(self.app))),
            Button((W // 2 - 90, 600, 180, 60), tr("quit"), (150, 150, 175), size=28, on_click=self.app.quit),
            # shows the *other* language, written in that language
            Button((24, 20, 170, 70), tr("lang_button"), PALETTE[3], size=30, on_click=self.app.toggle_lang,
                   label_lang="en" if i18n.lang() == "ja" else "ja"),
        ]
        self.corner_buttons(back=False)
        rnd = random.Random(3)
        spots = [(120, 220), (250, 560), (110, 450), (1150, 270), (1040, 520), (1170, 440), (300, 300),
                 (980, 330), (420, 640), (860, 640)]
        names = ["dog", "lion", "train", "owl", "drum", "cat", "bee", "frog", "duck", "guitar"]
        self.floaters = [(n, x, y, rnd.uniform(0, 6), rnd.randint(78, 108)) for n, (x, y) in zip(names, spots)]
        self.hint = 0.0
        if not TitleScene.greeted:
            TitleScene.greeted = True
            app.audio.sequence([("wait", 0.7), ("voice", app.audio.say("welcome"))])

    def play(self):
        if self.app.progress.players:
            self.app.go(PlayerScene(self.app))
        else:
            self.app.go(NewPlayerScene(self.app))

    def back(self):
        self.app.quit()

    def handle(self, e):
        super().handle(e)
        if e.type == pygame.MOUSEBUTTONDOWN:
            for n, x, y, ph, sz in self.floaters:
                if math.hypot(e.pos[0] - x, e.pos[1] - (y + bob(self.t, 1.6, 10, ph))) < sz / 2:
                    self.app.audio.play_clue(n)
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.play()
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_l:
            self.app.toggle_lang()

    def update(self, dt):
        super().update(dt)
        gate = self.buttons[1]
        self.hint = 1.0 if gate.pressed else max(0.0, self.hint - dt * 0.5)

    def draw(self, s):
        super().draw(s)
        for n, x, y, ph, sz in self.floaters:
            img = image(n, sz)
            ang = math.sin(self.t * 1.1 + ph) * 6
            rot = pygame.transform.rotozoom(img, ang, 1.0)
            s.blit(rot, rot.get_rect(center=(x, y + bob(self.t, 1.6, 10, ph))))
        # logo: each letter bounces in its own colour
        title = tr("app_name")
        f = font(124, "title")
        widths = [f.size(c)[0] for c in title]
        x = W // 2 - sum(widths) // 2
        for i, c in enumerate(title):
            y = 165 + bob(self.t, 2.4, 9, i * 0.55)
            col = PALETTE[i % len(PALETTE)]
            text(s, c, 124, col, center=(x + widths[i] // 2, y), kind="title", outline=WHITE, outline_w=7,
                 shadow=True)
            x += widths[i]
        text(s, tr("tagline"), 36, INK, center=(W // 2, 272), outline=WHITE, outline_w=3)
        # age badge
        bx, by = W // 2, 328
        panel(s, (bx - 92, by - 22, 184, 44), SUN, radius=22, shadow=4)
        text(s, tr("ages_badge", ages=i18n.AGES[i18n.lang()]), 26, INK, center=(bx, by + 1), max_w=168)
        self.draw_buttons(s)
        self.draw_corner_icons(s)
        if self.hint > 0:
            text(s, tr("hold_hint"), 22, INK, center=(W // 2 - 160, 590), alpha=int(255 * self.hint), max_w=560)
        text(s, f"v{__version__}", 20, INK_SOFT, topleft=(16, H - 32))
        text(s, "shoukugames.org", 20, INK_SOFT, topleft=(W - 175, H - 32))


# ===========================================================================
# Who is playing?
# ===========================================================================
class PlayerScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.corner_buttons()
        players = app.progress.players
        self.cards = []
        cols = 4
        cw, ch, gap = 230, 230, 34
        n = len(players) + 1
        rows = max(1, math.ceil(n / cols))
        top = 200 if rows == 1 else 150
        for i in range(min(n, 8)):
            r, c = divmod(i, cols)
            in_row = min(cols, n - r * cols)
            x0 = W // 2 - (in_row * cw + (in_row - 1) * gap) // 2
            rect = pygame.Rect(x0 + c * (cw + gap), top + r * (ch + 36), cw, ch)
            self.cards.append((rect, players[i] if i < len(players) else None))
        app.audio.sequence([("voice", app.audio.say("whoplays"))])

    def back(self):
        self.app.go(TitleScene(self.app))

    def handle(self, e):
        super().handle(e)
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            for rect, p in self.cards:
                if rect.collidepoint(e.pos):
                    self.app.audio.sfx("pop", 0.6)
                    if p is None:
                        self.app.go(NewPlayerScene(self.app))
                    else:
                        self.app.select_player(p)
                        self.app.go(LevelScene(self.app))

    def draw(self, s):
        super().draw(s)
        text(s, tr("who_plays"), 64, INK, center=(W // 2, 80), kind="title", outline=WHITE, outline_w=5)
        mouse = pygame.mouse.get_pos()
        for i, (rect, p) in enumerate(self.cards):
            hov = rect.collidepoint(mouse)
            r = rect.move(0, -6 if hov else 0)
            col = PALETTE[i % len(PALETTE)]
            panel(s, r, CREAM, radius=30, border=col, border_w=6)
            if p is None:
                pygame.draw.circle(s, lighten(col, 0.5), (r.centerx, r.y + 95), 62)
                pygame.draw.line(s, col, (r.centerx - 30, r.y + 95), (r.centerx + 30, r.y + 95), 12)
                pygame.draw.line(s, col, (r.centerx, r.y + 65), (r.centerx, r.y + 125), 12)
                text(s, tr("new_player"), 30, INK, center=(r.centerx, r.bottom - 42), max_w=r.w - 24)
            else:
                img = image(p.get("avatar", "dog"), 130)
                s.blit(img, img.get_rect(center=(r.centerx, r.y + 92 + (bob(self.t, 3, 4) if hov else 0))))
                text(s, p["name"], 32, INK, center=(r.centerx, r.bottom - 52), max_w=r.w - 24)
                stars = Progress.summary(p)["stars"]
                star_shape(s, (r.centerx - 22, r.bottom - 20), 12, SUN)
                text(s, f"{stars}", 22, INK_SOFT, midleft=(r.centerx - 4, r.bottom - 20))
        self.draw_buttons(s)
        self.draw_corner_icons(s)


class NewPlayerScene(Scene):
    wants_text = True

    def __init__(self, app):
        super().__init__(app)
        self.corner_buttons()
        self.name = ""
        self.composing = ""      # text still being typed with an input method (e.g. Japanese IME)
        self.avatar = AVATARS[len(app.progress.players) % len(AVATARS)]
        self.go_btn = Button((W // 2 - 160, 590, 320, 90), tr("lets_go"), GOOD, icon="ui_star", size=42,
                             on_click=self.create)
        self.buttons.append(self.go_btn)
        self.av_rects = []
        size, gap = 96, 18
        per = 6
        for i, a in enumerate(AVATARS):
            r, c = divmod(i, per)
            x0 = W // 2 - (per * size + (per - 1) * gap) // 2
            self.av_rects.append((pygame.Rect(x0 + c * (size + gap), 330 + r * (size + gap), size, size), a))
        self.box = pygame.Rect(W // 2 - 300, 180, 600, 90)
        pygame.key.start_text_input()
        pygame.key.set_text_input_rect(self.box)     # where the IME candidate window goes

    def create(self):
        p = self.app.progress.add_player(self.name or tr("default_player", n=len(self.app.progress.players) + 1),
                                         self.avatar)
        pygame.key.stop_text_input()
        self.app.select_player(p)
        self.app.go(LevelScene(self.app))

    def back(self):
        pygame.key.stop_text_input()
        self.app.go(PlayerScene(self.app) if self.app.progress.players else TitleScene(self.app))

    def handle(self, e):
        super().handle(e)
        if e.type == pygame.TEXTINPUT:
            self.composing = ""
            for ch in e.text:
                if (ch.isalnum() or ch in " -'ー・々") and len(self.name) < 14:
                    self.name += ch
        elif e.type == pygame.TEXTEDITING:
            self.composing = e.text
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_BACKSPACE and not self.composing:
                self.name = self.name[:-1]
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.create()
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            for r, a in self.av_rects:
                if r.collidepoint(e.pos):
                    self.avatar = a
                    self.app.audio.play_clue(a)

    def draw(self, s):
        super().draw(s)
        panel(s, (W // 2 - 430, 110, 860, 460), CREAM, radius=36)
        text(s, tr("new_player"), 56, INK, center=(W // 2, 70), kind="title", outline=WHITE, outline_w=5)
        text(s, tr("type_name"), 26, INK_SOFT, center=(W // 2, 150), max_w=820)
        box = self.box
        pygame.draw.rect(s, WHITE, box, border_radius=24)
        pygame.draw.rect(s, PALETTE[5], box, 5, border_radius=24)
        shown = self.name + self.composing
        r = text(s, shown or tr("name_placeholder"), 52, INK if shown else (190, 190, 205), center=box.center,
                 max_w=box.w - 40)
        if self.composing:      # underline the part the IME has not committed yet
            cw = font(52).size(self.composing)[0] * r.w // max(1, font(52).size(shown)[0])
            pygame.draw.line(s, PALETTE[5], (r.right - cw, r.bottom - 6), (r.right, r.bottom - 6), 3)
        if int(self.t * 2) % 2 == 0:
            x = r.right + 4 if shown else box.centerx + r.w // 2 + 6
            pygame.draw.line(s, INK, (x, box.y + 22), (x, box.bottom - 22), 4)
        text(s, tr("pick_buddy"), 30, INK, center=(W // 2, 305))
        for rect, a in self.av_rects:
            sel = a == self.avatar
            if sel:
                pygame.draw.circle(s, SUN, rect.center, rect.w // 2 + 10)
            pygame.draw.circle(s, WHITE, rect.center, rect.w // 2 + 2)
            img = image(a, rect.w - 18 if not sel else rect.w - 8)
            s.blit(img, img.get_rect(center=(rect.centerx, rect.centery + (bob(self.t, 4, 3) if sel else 0))))
        self.draw_buttons(s)
        self.draw_corner_icons(s)


# ===========================================================================
# Level map
# ===========================================================================
class LevelScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.corner_buttons()
        self.tiles = []
        tw, th, gx, gy = 270, 236, 26, 28
        for i, lv in enumerate(LEVELS):
            r, c = divmod(i, 4)
            x0 = W // 2 - (4 * tw + 3 * gx) // 2
            self.tiles.append(pygame.Rect(x0 + c * (tw + gx), 140 + r * (th + gy), tw, th))
        self.shake = {}
        app.audio.sequence([("voice", app.audio.say("pick"))])

    def back(self):
        self.app.go(PlayerScene(self.app))

    def handle(self, e):
        super().handle(e)
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            for i, r in enumerate(self.tiles):
                if r.collidepoint(e.pos):
                    if self.app.progress.unlocked(self.app.player, i):
                        self.app.audio.sfx("pop", 0.6)
                        self.app.go(GameScene(self.app, i))
                    else:
                        self.shake[i] = 0.5
                        self.app.audio.sfx("wrong", 0.5)

    def update(self, dt):
        super().update(dt)
        for k in list(self.shake):
            self.shake[k] -= dt
            if self.shake[k] <= 0:
                del self.shake[k]

    def draw(self, s):
        super().draw(s)
        p = self.app.player
        img = image(p.get("avatar", "dog"), 72)
        s.blit(img, (130, 18))
        text(s, tr("hi", name=p["name"]), 48, INK, midleft=(214, 56), kind="title", outline=WHITE, outline_w=4,
             max_w=W - 214 - 200)
        text(s, tr("pick_level"), 30, INK_SOFT, center=(W // 2 + 120, 104))
        mouse = pygame.mouse.get_pos()
        for i, (r, lv) in enumerate(zip(self.tiles, LEVELS)):
            info = Progress.level_info(p, i)
            unlocked = self.app.progress.unlocked(p, i)
            hov = r.collidepoint(mouse) and unlocked
            dx = math.sin(self.shake.get(i, 0) * 40) * 10 if i in self.shake else 0
            rr = r.move(dx, -8 if hov else 0)
            col = lv["color"] if unlocked else (196, 196, 210)
            panel(s, rr, col, radius=30)
            inner = rr.inflate(-16, -16)
            pygame.draw.rect(s, lighten(col, 0.55), inner, border_radius=24)
            # number bubble
            pygame.draw.circle(s, darken(col, 0.1), (rr.x + 40, rr.y + 40), 26)
            text(s, str(i + 1), 34, WHITE, center=(rr.x + 40, rr.y + 41), kind="title")
            # sample pictures from the level
            cat_items = [k for k, v in ITEMS.items() if v["category"] in lv["pool"]]
            samples = cat_items[:3] if len(lv["pool"]) == 1 else [cat_items[j] for j in (0, len(cat_items) // 2, -1)]
            for j, item in enumerate(samples):
                im = image(item, 74)
                if not unlocked:
                    im = im.copy()
                    im.fill((255, 255, 255, 110), special_flags=pygame.BLEND_RGBA_MULT)
                s.blit(im, im.get_rect(center=(rr.centerx - 78 + j * 78,
                                               rr.y + 92 + (bob(self.t, 3, 4, j) if hov else 0))))
            text(s, level_title(i), 28, INK if unlocked else INK_SOFT, center=(rr.centerx, rr.y + 152),
                 max_w=rr.w - 28)
            if unlocked:
                for k in range(3):
                    star_shape(s, (rr.centerx - 44 + k * 44, rr.bottom - 36), 17, SUN, filled=k < info["stars"])
            else:
                lock = image("ui_lock", 42)
                s.blit(lock, lock.get_rect(center=(rr.centerx, rr.bottom - 34)))
        self.draw_buttons(s)
        self.draw_corner_icons(s)


# ===========================================================================
# Playing a level
# ===========================================================================
class Card:
    W, H = 250, 286

    def __init__(self, item, rect, delay, key_hint):
        self.item = item
        self.rect = pygame.Rect(rect)
        self.t = -delay
        self.state = "idle"     # idle / wrong / right / dim
        self.shake = 0.0
        self.hover = 0.0
        self.key_hint = key_hint
        self.pop = 0.0

    @property
    def landed(self):
        return self.t > 0.45

    def update(self, dt, mouse):
        self.t += dt
        over = self.rect.collidepoint(mouse) and self.state == "idle" and self.landed
        self.hover += ((1.0 if over else 0.0) - self.hover) * min(1, dt * 12)
        self.shake = max(0.0, self.shake - dt)
        self.pop = max(0.0, self.pop - dt)

    def draw(self, s, labels, color, t):
        k = ease_out_back(self.t / 0.55)
        if self.t < 0:
            return
        r = self.rect.copy()
        r.y += int((1 - k) * 420) - int(self.hover * 10)
        if self.shake > 0:
            r.x += int(math.sin(self.shake * 50) * 12 * self.shake / 0.5)
        if self.pop > 0:
            r = r.inflate(int(self.pop * 40), int(self.pop * 40))
        border = color
        if self.state == "wrong":
            border = BAD
        elif self.state == "right":
            border = GOOD
        panel(s, r, WHITE, radius=32, border=border, border_w=7 if self.state != "idle" or self.hover > .5 else 5)
        size = 190 if labels else 210
        img = image(self.item, size)
        cy = r.y + (r.h // 2 - 20 if labels else r.h // 2)
        wiggle = math.sin(t * 6) * 4 * self.hover
        if self.state in ("wrong", "dim"):
            img = img.copy()
            img.fill((255, 255, 255, 90), special_flags=pygame.BLEND_RGBA_MULT)
        img = pygame.transform.rotozoom(img, wiggle, 1.0) if wiggle else img
        s.blit(img, img.get_rect(center=(r.centerx, cy)))
        if labels:
            name = item_name(self.item)
            text(s, name, 36, INK if self.state not in ("wrong", "dim") else (190, 190, 205),
                 center=(r.centerx, r.bottom - 40), max_w=r.w - 28)
        if self.state == "wrong":
            c = (r.right - 34, r.y + 34)
            pygame.draw.circle(s, BAD, c, 24)
            pygame.draw.line(s, WHITE, (c[0] - 10, c[1] - 10), (c[0] + 10, c[1] + 10), 6)
            pygame.draw.line(s, WHITE, (c[0] - 10, c[1] + 10), (c[0] + 10, c[1] - 10), 6)
        elif self.state == "right":
            c = (r.right - 34, r.y + 34)
            pygame.draw.circle(s, GOOD, c, 26)
            pygame.draw.lines(s, WHITE, False, [(c[0] - 12, c[1]), (c[0] - 3, c[1] + 10), (c[0] + 13, c[1] - 10)], 6)
        if self.state == "idle" and self.hover < 0.5:
            text(s, self.key_hint, 18, (200, 200, 215), center=(r.x + 22, r.y + 20))


class GameScene(Scene):
    PRAISE = ["great", "awesome", "yay", "superstar"]

    def __init__(self, app, level_index, practice_items=None):
        super().__init__(app)
        self.level_index = level_index
        if practice_items:
            self.level = dict(title=tr("practice_title"), pool=[], rounds=min(8, len(practice_items)), similar=1,
                              labels=True, color=PALETTE[7])
        else:
            self.level = dict(LEVELS[level_index], title=level_title(level_index))
        self.rng = random.Random()
        self.rounds = self._pick_rounds(practice_items)
        self.round_i = -1
        self.results = []
        self.confetti = Confetti()
        self.home_btn = Button((24, 20, 76, 70), "", PALETTE[6], on_click=self.back)
        self.home_btn.tag = "back"
        self.speaker = pygame.Rect(0, 0, 160, 160)
        self.speaker.center = (W // 2, 196)
        self.next_btn = Button((W // 2 + 30, 556, 300, 88), tr("next"), GOOD, size=42, on_click=self.next_round)
        self.again_btn = Button((W // 2 - 330, 556, 300, 88), tr("hear_again"), PALETTE[5], icon="ui_speaker",
                                size=34, on_click=self.replay_reveal)
        self.buttons = [self.home_btn]
        self.corner_buttons(back=False)
        self.reveal_buttons = [self.again_btn, self.next_btn]
        self.ring = 0.0
        self.last_tick = None
        self.start_round()

    # ---- round set-up ----------------------------------------------------
    def _pick_rounds(self, practice_items):
        if practice_items:
            pool = list(practice_items)
            self.rng.shuffle(pool)
            return pool[:self.level["rounds"]]
        pool = [k for k, v in ITEMS.items() if v["category"] in self.level["pool"]]
        # sounds this child has been finding hard come up more often
        hard = {e["item"] for e in Progress.trouble(self.app.player) if not e["mastered_since"]}
        chosen = []
        candidates = pool[:]
        for _ in range(min(self.level["rounds"], len(pool))):
            weights = [3.0 if c in hard else 1.0 for c in candidates]
            pick = self.rng.choices(candidates, weights)[0]
            candidates.remove(pick)
            chosen.append(pick)
        return chosen

    def _choices(self, item):
        cat = ITEMS[item]["category"]
        same = [k for k, v in ITEMS.items() if v["category"] == cat and k != item]
        n_same = min(self.level["similar"], len(same))
        picks = self.rng.sample(same, n_same)
        others = [c for c in CATEGORIES if c != cat]
        for c in self.rng.sample(others, CHOICES - 1 - n_same):
            picks.append(self.rng.choice([k for k, v in ITEMS.items() if v["category"] == c]))
        picks.append(item)
        self.rng.shuffle(picks)
        return picks

    def start_round(self):
        self.round_i += 1
        self.item = self.rounds[self.round_i]
        gap = 36
        total = CHOICES * Card.W + (CHOICES - 1) * gap
        x0 = W // 2 - total // 2
        self.cards = [Card(it, (x0 + i * (Card.W + gap), 318, Card.W, Card.H), 0.08 * i, str(i + 1))
                      for i, it in enumerate(self._choices(self.item))]
        self.state = "play"
        self.time_left = float(ROUND_SECONDS)
        self.timer_on = False
        self.wrong = []
        self.elapsed = 0.0
        self.reveal_t = 0.0
        self.letter_on = -1
        self.timed_out = False
        self.app.audio.sfx("whoosh", 0.5)
        steps = [("wait", 0.6)]
        if self.round_i == 0:
            steps += [("voice", self.app.audio.say("listen")), ("wait", 0.2)]
        steps += [("clue", self.item), ("call", self._start_timer)]
        self.app.audio.sequence(steps)

    def _start_timer(self):
        self.timer_on = True

    # ---- actions ---------------------------------------------------------
    def back(self):
        self.app.audio.stop_voice()
        if self.level_index is None:
            self.app.go(ParentsScene(self.app))
        else:
            self.app.go(LevelScene(self.app))

    def replay_clue(self):
        if self.state == "play":
            self.app.audio.stop_voice()
            self.app.audio.sequence([("clue", self.item), ("call", self._start_timer)])

    def choose(self, card):
        if self.state != "play" or card.state != "idle" or not card.landed:
            return
        if card.item == self.item:
            card.state = "right"
            card.pop = 0.3
            for c in self.cards:
                if c is not card and c.state == "idle":
                    c.state = "dim"
            result = "first_try" if not self.wrong else "after_mistakes"
            self.finish(result)
            self.confetti.burst(card.rect.centerx, card.rect.centery, 70)
            self.app.audio.sfx("correct", 0.8)
        else:
            card.state = "wrong"
            card.shake = 0.5
            self.wrong.append(card.item)
            self.app.audio.sfx("wrong", 0.7)
            phrase = "tryagain" if len(self.wrong) == 1 else "notquite"
            self.app.audio.sequence([("wait", 0.35), ("voice", self.app.audio.say(phrase)), ("wait", 0.25),
                                     ("clue", self.item)])

    def finish(self, result):
        self.state = "reveal_wait"
        self.reveal_t = 0.0
        self.results.append({"item": self.item, "result": result, "wrong": list(self.wrong)})
        level_key = "practice" if self.level_index is None else self.level_index
        self.app.progress.record(self.app.player, level_key, self.item, result, self.wrong, self.elapsed)
        a = self.app.audio
        if result == "timeout":
            self.timed_out = True
            for c in self.cards:
                if c.item == self.item:
                    c.state = "right"
                elif c.state == "idle":
                    c.state = "dim"
            steps = [("wait", 0.3), ("voice", a.say("timeup")), ("wait", 0.15)]
        else:
            steps = [("wait", 0.8), ("voice", a.say(self.rng.choice(self.PRAISE))), ("wait", 0.2)]
        steps += [("call", self._show_reveal)]
        steps += [("clue", self.item), ("wait", 0.2)] if result == "timeout" else []
        steps += spelling_steps(a, self.item, self._set_letter)
        a.sequence(steps)

    def _show_reveal(self):
        self.state = "reveal"
        self.reveal_t = 0.0

    def _set_letter(self, i):
        self.letter_on = i

    def replay_reveal(self):
        a = self.app.audio
        a.sequence([("clue", self.item), ("wait", 0.3)] + spelling_steps(a, self.item, self._set_letter))

    def next_round(self):
        self.app.audio.stop_voice()
        if self.round_i + 1 < len(self.rounds):
            self.start_round()
        else:
            self.app.go(LevelCompleteScene(self.app, self.level_index, self.level, self.results,
                                           self.rounds))

    # ---- loop ------------------------------------------------------------
    def handle(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.back()
            return
        if self.state == "reveal":
            for b in self.reveal_buttons:
                if b.handle(e, self.app):
                    return
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT):
                self.next_round()
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self._reveal_pic_rect().collidepoint(e.pos):
                self.replay_reveal()
            return
        for b in (self.home_btn, self.music_btn, self.full_btn):
            if b.handle(e, self.app):
                return
        if self.state != "play":
            return
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if math.hypot(e.pos[0] - self.speaker.centerx, e.pos[1] - self.speaker.centery) < 80:
                self.app.audio.sfx("pop", 0.5)
                self.replay_clue()
                return
            for c in self.cards:
                if c.rect.collidepoint(e.pos):
                    self.choose(c)
                    return
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_SPACE, pygame.K_r):
                self.replay_clue()
            idx = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
                   pygame.K_KP1: 0, pygame.K_KP2: 1, pygame.K_KP3: 2, pygame.K_KP4: 3}.get(e.key)
            if idx is not None and idx < len(self.cards):
                self.choose(self.cards[idx])

    def update(self, dt):
        super().update(dt)
        self.home_btn.update(dt)
        mouse = pygame.mouse.get_pos()
        for c in self.cards:
            c.update(dt, mouse)
        self.confetti.update(dt)
        self.ring = (self.ring + dt) % 1.2
        if self.state == "play":
            self.elapsed += dt
            if self.timer_on:
                self.time_left -= dt
                sec = math.ceil(self.time_left)
                if sec <= 5 and sec != self.last_tick and sec > 0:
                    self.last_tick = sec
                    self.app.audio.sfx("tick", 0.35)
                if self.time_left <= 0:
                    self.time_left = 0
                    self.finish("timeout")
        if self.state == "reveal":
            self.reveal_t += dt
            for b in self.reveal_buttons:
                b.update(dt)

    def _reveal_pic_rect(self):
        r = pygame.Rect(0, 0, 250, 250)
        r.center = (W // 2, 262)
        return r

    def draw(self, s):
        super().draw(s)
        lv = self.level
        # top bar
        text(s, lv["title"], 40, INK, center=(W // 2, 46), kind="title", outline=WHITE, outline_w=4, max_w=640)
        n = len(self.rounds)
        for i in range(n):
            x = W // 2 - (n - 1) * 15 + i * 30
            done = i < len(self.results)
            col = (GOOD if self.results[i]["result"] == "first_try" else SUN) if done else \
                (WHITE if i != self.round_i else lv["color"])
            pygame.draw.circle(s, darken(col, 0.2), (x, 88), 11)
            pygame.draw.circle(s, col, (x, 87), 9)
        self.home_btn.draw(s)
        self.music_btn.draw(s)
        self.full_btn.draw(s)
        self.draw_corner_icons(s)
        self.draw_timer(s)
        self.draw_speaker(s)
        for c in self.cards:
            c.draw(s, lv["labels"], lv["color"], self.t)
        self.confetti.draw(s)
        if self.state == "reveal":
            self.draw_reveal(s)

    def draw_timer(self, s):
        cx, cy, r = W - 262, 58, 44
        frac = max(0.0, self.time_left / ROUND_SECONDS)
        col = GOOD if self.time_left > 30 else (SUN if self.time_left > 10 else BAD)
        pulse = 1 + (0.06 * math.sin(self.t * 10) if self.time_left <= 10 and self.state == "play" else 0)
        rr = int(r * pulse)
        pygame.draw.circle(s, darken(col, 0.3), (cx, cy + 5), rr)
        pygame.draw.circle(s, WHITE, (cx, cy), rr)
        if frac > 0:
            rect = pygame.Rect(0, 0, rr * 2 - 10, rr * 2 - 10)
            rect.center = (cx, cy)
            pygame.draw.arc(s, col, rect, math.pi / 2, math.pi / 2 + 2 * math.pi * frac, 10)
        text(s, str(max(0, math.ceil(self.time_left))), 36, INK, center=(cx, cy + 1), kind="title")
        clock = image("ui_clock", 30)
        s.blit(clock, clock.get_rect(center=(cx - 68, cy)))

    def draw_speaker(self, s):
        cx, cy = self.speaker.center
        playing = self.app.audio.clue_ch is not None and self.app.audio.clue_ch.get_busy()
        if playing:
            for k in range(3):
                ph = (self.ring + k * 0.4) % 1.2 / 1.2
                rad = int(80 + ph * 70)
                ring = pygame.Surface((rad * 2 + 8, rad * 2 + 8), pygame.SRCALPHA)
                pygame.draw.circle(ring, (*WHITE, int(200 * (1 - ph))), (rad + 4, rad + 4), rad, 6)
                s.blit(ring, (cx - rad - 4, cy - rad - 4))
        hov = math.hypot(pygame.mouse.get_pos()[0] - cx, pygame.mouse.get_pos()[1] - cy) < 80
        bounce = bob(self.t, 6, 4) if playing else (bob(self.t, 2, 3) if hov else 0)
        col = PALETTE[1]
        pygame.draw.circle(s, darken(col, 0.3), (cx, cy + 8 + bounce), 76)
        pygame.draw.circle(s, col, (cx, cy + bounce), 76)
        pygame.draw.circle(s, lighten(col, 0.3), (cx, cy + bounce), 64)
        img = image("ui_speaker", 96)
        s.blit(img, img.get_rect(center=(cx, cy + bounce)))
        if self.state == "play" and not playing:
            text(s, tr("tap_listen"), 22, INK, center=(cx, cy + 96), outline=WHITE, outline_w=2)

    def draw_reveal(self, s):
        k = ease_out_back(self.reveal_t / 0.45)
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((40, 40, 80, int(120 * min(1, self.reveal_t * 3))))
        s.blit(dim, (0, 0))
        r = pygame.Rect(0, 0, int(860 * k), int(600 * k))
        r.center = (W // 2, H // 2 + 10)
        if k < 0.2:
            return
        panel(s, r, CREAM, radius=40, border=SUN if not self.timed_out else PALETTE[5], border_w=8)
        if k < 0.95:
            return
        head = tr("times_up") if self.timed_out else tr("found_it")
        text(s, head, 40, INK_SOFT if self.timed_out else GOOD, center=(W // 2, 106), kind="title")
        if not self.timed_out:
            for i in range(5):
                a = self.t * 0.8 + i * 2 * math.pi / 5
                star_shape(s, (int(W // 2 + math.cos(a) * 170), int(262 + math.sin(a) * 120)), 14, PALETTE[i])
        pr = self._reveal_pic_rect()
        img = image(self.item, 230)
        scale = 1 + 0.04 * math.sin(self.t * 4)
        img = pygame.transform.rotozoom(img, math.sin(self.t * 2) * 4, scale)
        s.blit(img, img.get_rect(center=pr.center))
        # the word, letter by letter (kana by kana in Japanese), highlighting the one being spoken
        units = i18n.spell_units(item_name(self.item))
        size = 92 if len(units) <= 8 else 76
        while True:
            f = font(size, "body")
            widths = [f.size(c)[0] + (6 if c != " " else 10) for c in units]
            if sum(widths) <= 780 or size <= 40:
                break
            size -= 6
        x = W // 2 - sum(widths) // 2
        for i, c in enumerate(units):
            on = i == self.letter_on
            col = PALETTE[i % len(PALETTE)] if on else INK
            y = 452 - (12 if on else 0)
            if on:
                big = font(int(size * 1.2), "body").render(c, True, col)
                pygame.draw.circle(s, lighten(col, 0.7), (x + widths[i] // 2, y + 4), int(size * 0.62))
                s.blit(big, big.get_rect(center=(x + widths[i] // 2, y)))
            else:
                text(s, c, size, col, center=(x + widths[i] // 2, y))
            x += widths[i]
        text(s, category_name(ITEMS[self.item]["category"]), 24, INK_SOFT, center=(W // 2, 516))
        for b in self.reveal_buttons:
            b.draw(s)
        # arrow on the Next button
        nb = self.next_btn.rect.move(0, -int(self.next_btn.hover * 4))
        ax, ay = nb.right - 50, nb.centery
        pygame.draw.polygon(s, WHITE, [(ax - 14, ay - 18), (ax + 10, ay), (ax - 14, ay + 18)])


class LevelCompleteScene(Scene):
    def __init__(self, app, level_index, level, results, rounds):
        super().__init__(app)
        self.level_index = level_index
        self.level = level
        self.results = results
        first = sum(1 for r in results if r["result"] == "first_try")
        ratio = first / max(1, len(results))
        self.stars = 3 if ratio >= 0.8 else (2 if ratio >= 0.5 else 1)
        self.first = first
        self.missed = [r["item"] for r in results if r["result"] != "first_try"]
        if level_index is not None:
            app.progress.finish_level(app.player, level_index, self.stars)
        self.confetti = Confetti()
        self.confetti.rain(160)
        self.shown = 0
        self.star_t = 0.0
        app.audio.sfx("levelup", 0.8)
        app.audio.sequence([("wait", 0.6), ("voice", app.audio.say("levelup"))])
        bw = 280
        has_next = level_index is not None and level_index + 1 < len(LEVELS)
        btns = []
        if has_next:
            btns.append((tr("next_level"), GOOD, lambda: self.app.go(GameScene(self.app, level_index + 1))))
        btns.append((tr("play_again"), PALETTE[1], self.again))
        btns.append((tr("levels") if level_index is not None else tr("grownups"), PALETTE[5], self.back))
        total = len(btns) * bw + (len(btns) - 1) * 24
        x = W // 2 - total // 2
        for label, col, fn in btns:
            self.buttons.append(Button((x, 580, bw, 84), label, col, size=34, on_click=fn))
            x += bw + 24

    def again(self):
        if self.level_index is None:
            self.app.go(GameScene(self.app, None, practice_items=list({r["item"] for r in self.results})))
        else:
            self.app.go(GameScene(self.app, self.level_index))

    def back(self):
        self.app.go(LevelScene(self.app) if self.level_index is not None else ParentsScene(self.app))

    def update(self, dt):
        super().update(dt)
        self.confetti.update(dt)
        self.star_t += dt
        if self.shown < self.stars and self.star_t > 0.8 + self.shown * 0.45:
            self.shown += 1
            self.app.audio.sfx("star", 0.7)

    def draw(self, s):
        super().draw(s)
        panel(s, (W // 2 - 420, 60, 840, 490), CREAM, radius=40, border=SUN, border_w=8)
        trophy = image("ui_trophy", 110)
        s.blit(trophy, trophy.get_rect(center=(W // 2, 130 + bob(self.t, 3, 5))))
        text(s, tr("level_complete"), 56, INK, center=(W // 2, 232), kind="title")
        text(s, self.level["title"], 28, INK_SOFT, center=(W // 2, 280))
        for k in range(3):
            filled = k < self.shown
            grow = ease_out_back((self.star_t - 0.8 - k * 0.45) / 0.4) if filled else 1
            star_shape(s, (W // 2 - 110 + k * 110, 352), int(44 * grow), SUN, filled=filled)
        text(s, tr("knew_n", first=self.first, total=len(self.results)), 30, INK, center=(W // 2, 428),
             max_w=800)
        if self.missed:
            text(s, tr("listen_again_soon"), 22, INK_SOFT, center=(W // 2, 470))
            uniq = list(dict.fromkeys(self.missed))[:8]
            x = W // 2 - (len(uniq) * 62) // 2 + 31
            for it in uniq:
                im = image(it, 52)
                s.blit(im, im.get_rect(center=(x, 512)))
                x += 62
        self.confetti.draw(s)
        self.draw_buttons(s)


# ===========================================================================
# Grown-ups area: progress reports
# ===========================================================================
class ParentsScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.TABS = tr("tabs")
        self.corner_buttons()
        self.players = app.progress.players
        sel = app.player["id"] if app.player else (self.players[0]["id"] if self.players else None)
        self.sel = sel
        self.tab = 0
        self.scroll = 0
        self.confirm = None          # ("reset"|"delete", pid)
        self.tab_rects = [pygame.Rect(330 + i * 250, 112, 236, 56) for i in range(len(self.TABS))]
        self.area = pygame.Rect(330, 180, 920, 430)
        self.practice_btn = Button((330, 626, 320, 74), tr("practice_these"), GOOD, icon="ui_ear", size=28,
                                   on_click=self.practice)
        self.reset_btn = Button((870, 626, 180, 74), tr("reset"), PALETTE[1], size=26, on_click=lambda: self.ask("reset"))
        self.delete_btn = Button((1066, 626, 184, 74), tr("delete"), BAD, size=26, on_click=lambda: self.ask("delete"))
        self.buttons += [self.practice_btn, self.reset_btn, self.delete_btn]
        self.yes_btn = Button((W // 2 - 230, 420, 210, 76), tr("yes"), BAD, size=32, on_click=self.do_confirm)
        self.no_btn = Button((W // 2 + 20, 420, 210, 76), tr("no"), PALETTE[5], size=32, on_click=self.cancel)
        self.row_play = []

    # ---- helpers ---------------------------------------------------------
    @property
    def player(self):
        return self.app.progress.get(self.sel) if self.sel else None

    def back(self):
        self.app.go(TitleScene(self.app))

    def ask(self, what):
        if self.player:
            self.confirm = (what, self.sel)

    def cancel(self):
        self.confirm = None

    def do_confirm(self):
        what, pid = self.confirm
        if what == "reset":
            self.app.progress.reset_player(pid)
        else:
            self.app.progress.remove_player(pid)
            if self.app.player and self.app.player["id"] == pid:
                self.app.player = None
            self.players = self.app.progress.players
            self.sel = self.players[0]["id"] if self.players else None
        self.confirm = None

    def practice(self):
        p = self.player
        if not p:
            return
        items = [e["item"] for e in Progress.trouble(p) if not e["mastered_since"]]
        if not items:
            items = [e["item"] for e in Progress.trouble(p)]
        if not items:
            return
        self.app.select_player(p)
        self.app.go(GameScene(self.app, None, practice_items=items))

    def player_rects(self):
        return [(pygame.Rect(30, 112 + i * 84, 270, 74), p) for i, p in enumerate(self.players[:7])]

    # ---- events ----------------------------------------------------------
    def handle(self, e):
        if self.confirm:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.cancel()
                return
            self.yes_btn.handle(e, self.app) or self.no_btn.handle(e, self.app)
            return
        super().handle(e)
        if e.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, self.scroll - e.y * 40)
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            for r, p in self.player_rects():
                if r.collidepoint(e.pos):
                    self.sel, self.scroll = p["id"], 0
                    self.app.audio.sfx("pop", 0.5)
            for i, r in enumerate(self.tab_rects):
                if r.collidepoint(e.pos):
                    self.tab, self.scroll = i, 0
                    self.app.audio.sfx("pop", 0.5)
            if self.area.collidepoint(e.pos):
                for r, item in self.row_play:
                    if r.collidepoint(e.pos):
                        a = self.app.audio
                        a.sequence([("clue", item), ("wait", 0.3)] + spelling_steps(a, item))
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_DOWN:
                self.scroll += 40
            elif e.key == pygame.K_UP:
                self.scroll = max(0, self.scroll - 40)

    def update(self, dt):
        super().update(dt)
        p = self.player
        has_trouble = bool(p and Progress.trouble(p))
        self.practice_btn.visible = self.tab == 1 and has_trouble
        self.reset_btn.visible = self.delete_btn.visible = p is not None
        if self.confirm:
            self.yes_btn.update(dt)
            self.no_btn.update(dt)

    # ---- drawing ---------------------------------------------------------
    def draw(self, s):
        self.sky.draw(s, hills=False)
        text(s, tr("parents_title"), 52, INK, center=(W // 2, 56), kind="title", outline=WHITE, outline_w=4,
             max_w=W - 440)
        for r, p in self.player_rects():
            on = p["id"] == self.sel
            panel(s, r, WHITE if on else CREAM, radius=22, border=PALETTE[5] if on else None, shadow=6)
            s.blit(image(p.get("avatar", "dog"), 56), (r.x + 10, r.y + 9))
            text(s, p["name"], 28, INK, midleft=(r.x + 78, r.centery), max_w=r.w - 90)
        if not self.players:
            panel(s, (330, 180, 920, 430), CREAM, radius=26)
            text(s, tr("no_players"), 40, INK, center=(790, 330))
            text(s, tr("no_players_hint"), 28, INK_SOFT, center=(790, 390), max_w=880)
            self.draw_buttons(s)
            self.draw_corner_icons(s)
            return
        for i, (r, name) in enumerate(zip(self.tab_rects, self.TABS)):
            on = i == self.tab
            col = PALETTE[[5, 1, 6][i]]
            pygame.draw.rect(s, col if on else lighten(col, 0.6), r, border_radius=18)
            text(s, name, 26, WHITE if on else INK, center=r.center, max_w=r.w - 20)
        panel(s, self.area.inflate(16, 16), CREAM, radius=24, shadow=6)
        content = pygame.Surface(self.area.size, pygame.SRCALPHA)
        self.row_play = []
        height = [self.draw_overview, self.draw_trouble, self.draw_recent][self.tab](content)
        self.scroll = max(0, min(self.scroll, max(0, height - self.area.h)))
        s.blit(content, self.area.topleft)
        if height > self.area.h:
            frac = self.area.h / height
            bar_h = max(40, int(self.area.h * frac))
            y = self.area.y + int((self.area.h - bar_h) * self.scroll / max(1, height - self.area.h))
            pygame.draw.rect(s, (200, 200, 220), (self.area.right - 4, y, 8, bar_h), border_radius=4)
        if self.tab != 1 or not self.practice_btn.visible:
            for i, ln in enumerate(wrap(tr("tip"), 19, 510)):
                text(s, ln, 19, INK, midleft=(330, 650 + i * 26), kind="plain")
        self.draw_buttons(s)
        self.draw_corner_icons(s)
        if self.confirm:
            dim = pygame.Surface((W, H), pygame.SRCALPHA)
            dim.fill((30, 30, 60, 150))
            s.blit(dim, (0, 0))
            panel(s, (W // 2 - 300, 220, 600, 300), CREAM, radius=30)
            line1, line2 = tr("confirm_" + self.confirm[0], name=self.player["name"])
            text(s, line1, 32, INK, center=(W // 2, 290), max_w=560)
            text(s, line2, 40, INK, center=(W // 2, 345), kind="title", max_w=560)
            self.yes_btn.draw(s)
            self.no_btn.draw(s)

    def draw_overview(self, c):
        p = self.player
        sm = Progress.summary(p)
        y0 = -self.scroll
        tiles = [(tr("t_rounds"), str(sm["rounds"])), (tr("t_first"), f"{sm['accuracy']:.0f}%"),
                 (tr("t_known"), f"{sm['sounds_known']} / {len(ITEMS)}"),
                 (tr("t_avg"), tr("secs", s=f"{sm['avg_secs']:.1f}")), (tr("t_timeouts"), str(sm["timeouts"])),
                 (tr("t_stars"), f"{sm['stars']} / {len(LEVELS) * 3}")]
        for i, (label, val) in enumerate(tiles):
            r = pygame.Rect(16 + (i % 3) * 300, y0 + 14 + (i // 3) * 112, 284, 100)
            col = PALETTE[i + 2 if i + 2 < len(PALETTE) else i]
            pygame.draw.rect(c, lighten(col, 0.72), r, border_radius=18)
            text(c, val, 40, darken(col, 0.4), center=(r.centerx, r.y + 40), kind="title")
            text(c, label, 22, INK, center=(r.centerx, r.y + 78), max_w=r.w - 16)
        y = y0 + 260
        text(c, tr("levels"), 30, INK, topleft=(18, y))
        y += 44
        for i, lv in enumerate(LEVELS):
            info = Progress.level_info(p, i)
            r = pygame.Rect(16, y, 888, 52)
            pygame.draw.rect(c, WHITE if i % 2 == 0 else (248, 245, 235), r, border_radius=12)
            pygame.draw.circle(c, lv["color"], (44, r.centery), 18)
            text(c, str(i + 1), 22, WHITE, center=(44, r.centery + 1))
            text(c, level_title(i), 26, INK, midleft=(76, r.centery), max_w=330)
            for k in range(3):
                star_shape(c, (430 + k * 38, r.centery), 14, SUN, filled=k < info["stars"])
            status = (tr("status_done") if info["completed"] else
                      (tr("status_ready") if i == 0 or Progress.level_info(p, i - 1)["completed"]
                       else tr("status_locked")))
            text(c, status, 22, INK_SOFT, midleft=(560, r.centery), max_w=170)
            text(c, tr("played_n", n=info.get("plays", 0)), 22, INK_SOFT, midleft=(740, r.centery), max_w=150)
            y += 58
        created = p.get("created", "")[:10]
        text(c, tr("player_since", date=created), 20, INK_SOFT, topleft=(18, y + 10), kind="plain")
        return y + 50 - y0

    def draw_trouble(self, c):
        p = self.player
        rows = Progress.trouble(p)
        y0 = -self.scroll
        if not rows:
            text(c, tr("nothing_yet"), 30, INK, center=(self.area.w // 2, 120), max_w=self.area.w - 40)
            text(c, tr("nothing_yet_1"), 22, INK_SOFT, center=(self.area.w // 2, 180), kind="plain",
                 max_w=self.area.w - 40)
            text(c, tr("nothing_yet_2"), 22, INK_SOFT, center=(self.area.w // 2, 210), kind="plain",
                 max_w=self.area.w - 40)
            return 260
        text(c, tr("h_sound"), 20, INK_SOFT, topleft=(96, y0 + 6))
        text(c, tr("h_missed"), 20, INK_SOFT, topleft=(330, y0 + 6))
        text(c, tr("h_mixed"), 20, INK_SOFT, topleft=(470, y0 + 6))
        y = y0 + 34
        for i, e in enumerate(rows):
            r = pygame.Rect(10, y, 900, 84)
            pygame.draw.rect(c, WHITE if i % 2 == 0 else (248, 245, 235), r, border_radius=14)
            c.blit(image(e["item"], 64), (22, y + 10))
            text(c, item_name(e["item"]), 28, INK, midleft=(96, y + 30), max_w=226)
            text(c, category_name(ITEMS[e["item"]]["category"]), 18, INK_SOFT, midleft=(96, y + 60), kind="plain",
                 max_w=226)
            text(c, tr("m_of_a", m=e["misses"], a=e["attempts"]), 26, BAD if not e["mastered_since"] else INK_SOFT,
                 midleft=(330, y + 30), max_w=134)
            if e["timeouts"]:
                text(c, tr("timeouts_n", n=e["timeouts"]), 18, INK_SOFT, midleft=(330, y + 60), kind="plain",
                     max_w=134)
            x = 470
            for other, cnt in e["mixed_up"].most_common(4):
                if other in ITEMS:
                    c.blit(image(other, 50), (x, y + 8))
                    label = tr("times_n", name=item_name(other), n=cnt) if cnt > 1 else item_name(other)
                    text(c, label, 15, INK, center=(x + 25, y + 70), kind="plain", max_w=74)
                    x += 76
            if not e["mixed_up"]:
                text(c, tr("no_answer"), 20, INK_SOFT, midleft=(470, y + 42), kind="plain")
            if e["mastered_since"]:
                pygame.draw.rect(c, lighten(GOOD, 0.6), (774, y + 12, 50, 26), border_radius=10)
                text(c, tr("now_ok"), 14, darken(GOOD, 0.4), center=(799, y + 25), max_w=46)
            pr = pygame.Rect(840, y + 14, 56, 56)
            pygame.draw.circle(c, PALETTE[1], pr.center, 28)
            pygame.draw.polygon(c, WHITE, [(pr.centerx - 8, pr.centery - 13), (pr.centerx + 14, pr.centery),
                                           (pr.centerx - 8, pr.centery + 13)])
            self.row_play.append((pr.move(self.area.topleft), e["item"]))
            y += 92
        return y + 10 - y0

    def draw_recent(self, c):
        p = self.player
        hist = list(reversed(p["history"]))[:60]
        y0 = -self.scroll
        if not hist:
            text(c, tr("no_history"), 30, INK, center=(self.area.w // 2, 120))
            return 200
        y = y0 + 8
        for i, r in enumerate(hist):
            row = pygame.Rect(10, y, 900, 58)
            pygame.draw.rect(c, WHITE if i % 2 == 0 else (248, 245, 235), row, border_radius=12)
            when = i18n.format_when(datetime.fromtimestamp(r["t"]))
            text(c, when, 18, INK_SOFT, midleft=(22, row.centery), kind="plain")
            lvl = tr("practice") if r["level"] == "practice" else level_title(int(r["level"]))
            text(c, lvl, 18, INK_SOFT, midleft=(150, row.centery), kind="plain", max_w=160)
            if r["item"] in ITEMS:
                c.blit(image(r["item"], 44), (318, y + 7))
                text(c, item_name(r["item"]), 22, INK, midleft=(370, row.centery), max_w=164)
            res = r["result"]
            if res == "first_try":
                chip, col = tr("chip_first"), GOOD
            elif res == "timeout":
                chip, col = tr("chip_timeout"), BAD
            else:
                n = len(r["wrong"])
                chip, col = (tr("chip_after_1") if n == 1 else tr("chip_after_n", n=n)), SUN
            cr = pygame.Rect(540, y + 13, 200, 32)
            pygame.draw.rect(c, lighten(col, 0.6), cr, border_radius=14)
            text(c, chip, 17, darken(col, 0.45), center=cr.center, max_w=cr.w - 12)
            x = 754
            for w in r["wrong"][:3]:
                if w in ITEMS:
                    c.blit(image(w, 34), (x, y + 12))
                    x += 38
            text(c, tr("secs", s=f"{r['secs']:.0f}"), 18, INK_SOFT, midleft=(872, row.centery), kind="plain")
            y += 64
        return y + 10 - y0


# ===========================================================================
# Credits
# ===========================================================================
class CreditsScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.corner_buttons()
        self.scroll = 0.0
        self.auto = True
        self.links = []
        try:
            self.sound_credits = json.loads((ASSETS / "sounds" / "credits.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.sound_credits = {}
        self.area = pygame.Rect(W // 2 - 470, 108, 940, 568)
        self.content, self.links = self.build()

    def back(self):
        self.app.go(TitleScene(self.app))

    def build(self):
        lines = []   # (kind, text, size, color, link)
        add = lambda *a: lines.append(a)  # noqa: E731
        lang = i18n.lang()
        add("title", tr("app_name"), 72, PALETTE[5], None)
        add("text", tr("version_line", v=__version__, date=i18n.RELEASE_DATE[lang]), 26, INK_SOFT, None)
        add("gap", "", 18, None, None)
        add("head", tr("created_by"), 30, PALETTE[1], None)
        for c in CREATORS:
            add("big", c, 44, INK, None)
        add("gap", "", 14, None, None)
        add("link", WEBSITE, 32, PALETTE[5], WEBSITE)
        add("link", EMAIL, 32, PALETTE[5], "mailto:" + EMAIL)
        add("gap", "", 14, None, None)
        add("head", tr("rec_ages"), 30, PALETTE[1], None)
        add("big", i18n.AGES_FULL[lang], 44, INK, None)
        add("gap", "", 14, None, None)
        add("head", tr("licence"), 30, PALETTE[1], None)
        for ln in wrap(tr("gpl"), 22, 820):
            add("text", ln, 22, INK, None)
        add("link", "https://www.gnu.org/licenses/gpl-3.0.html", 24, PALETTE[5],
            "https://www.gnu.org/licenses/gpl-3.0.html")
        add("gap", "", 14, None, None)
        for head, body in (("pictures", "pictures_text"), ("fonts", "fonts_text"), ("voice", "voice_text"),
                           ("music_fx", "music_fx_text")):
            add("head", tr(head), 30, PALETTE[1], None)
            for ln in wrap(tr(body), 22, 820):
                add("text", ln, 22, INK, None)
        add("gap", "", 10, None, None)
        add("head", tr("recordings"), 30, PALETTE[1], None)
        for key, srcs in self.sound_credits.items():
            name = item_name(key) if key in ITEMS else key
            for src in srcs:
                ln = tr("recording_line", name=name, file=src["file"], author=src["author"], license=src["license"])
                for i, part in enumerate(wrap(ln, 19, 860)):
                    add("small", part, 19, INK, src["page"] if i == 0 else None)
        add("gap", "", 20, None, None)
        add("big", tr("thanks"), 40, PALETTE[3], None)
        # lay out
        y = 10
        laid, links = [], []
        for kind, msg, size, color, link in lines:
            if kind == "gap":
                y += size
                continue
            k = "title" if kind == "title" else ("plain" if kind in ("text", "small") else "body")
            h = font(size, k).get_linesize()
            laid.append((msg, size, color, k, y + h // 2, link))
            if link:
                links.append((pygame.Rect(0, y, self.area.w, h), link))
            y += h + (6 if kind == "head" else 2)
        return (laid, y + 20), links

    def handle(self, e):
        super().handle(e)
        if e.type == pygame.MOUSEWHEEL:
            self.scroll -= e.y * 50
            self.auto = False
        elif e.type == pygame.KEYDOWN and e.key in (pygame.K_DOWN, pygame.K_UP):
            self.scroll += 50 if e.key == pygame.K_DOWN else -50
            self.auto = False
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self.area.collidepoint(e.pos):
            ly = e.pos[1] - self.area.y + self.scroll
            for r, link in self.links:
                if r.y <= ly <= r.bottom:
                    try:
                        webbrowser.open(link)
                    except Exception:  # noqa: BLE001 - never crash the game over a browser
                        pass
                    return
            self.auto = not self.auto

    def update(self, dt):
        super().update(dt)
        total = self.content[1]
        if self.auto:
            self.scroll += dt * 32
            if self.scroll > total - self.area.h + 60:
                self.scroll = -40
        self.scroll = max(-60, min(self.scroll, max(0, total - self.area.h + 60)))

    def draw(self, s):
        super().draw(s)
        text(s, tr("credits_title"), 56, INK, center=(W // 2, 56), kind="title", outline=WHITE, outline_w=5)
        panel(s, self.area.inflate(20, 10), CREAM, radius=30, alpha=238)
        s.set_clip(self.area)
        laid, _ = self.content
        mouse = pygame.mouse.get_pos()
        for msg, size, color, kind, cy, link in laid:
            y = self.area.y + cy - self.scroll
            if y < self.area.y - 60 or y > self.area.bottom + 60:
                continue
            r = text(s, msg, size, color, center=(W // 2, y), kind=kind)
            if link and r.collidepoint(mouse):
                pygame.draw.line(s, color, (r.x, r.bottom - 4), (r.right, r.bottom - 4), 2)
        s.set_clip(None)
        text(s, tr("credits_hint"), 18, INK_SOFT, center=(W // 2, H - 14),
             kind="plain")
        self.draw_buttons(s)
        self.draw_corner_icons(s)
