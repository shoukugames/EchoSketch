#!/usr/bin/env python3
# EchoSketch - asset pipeline
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Draw the application icon (assets/icon.png + packaging/echosketch.ico)."""
import math
import os
import subprocess
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
S = 512


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    grad = pygame.Surface((S, S))
    for y in range(S):
        t = y / S
        grad.fill((int(255 - 30 * t), int(170 - 60 * t), int(80 + 110 * t)), (0, y, S, 1))
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (16, 16, S - 32, S - 32), border_radius=110)
    grad = grad.convert_alpha()
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    shadow = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (40, 30, 80, 90), (16, 30, S - 32, S - 32), border_radius=110)
    surf.blit(shadow, (0, 0))
    surf.blit(grad, (0, 0))
    # sound waves
    cx, cy = 300, 256
    for i, r in enumerate((90, 150, 210)):
        rect = pygame.Rect(0, 0, r * 2, r * 2)
        rect.center = (cx - 150, cy)
        pygame.draw.arc(surf, (255, 255, 255, 230 - i * 50), rect, -math.pi / 4, math.pi / 4, 22)
    ear = pygame.image.load(str(ROOT / "assets" / "images" / "ui_ear.png")).convert_alpha()
    ear = pygame.transform.smoothscale(ear, (250, 250))
    surf.blit(ear, ear.get_rect(center=(190, 256)))
    out = ROOT / "assets" / "icon.png"
    pygame.image.save(pygame.transform.smoothscale(surf, (256, 256)), str(out))
    big = ROOT / "build" / "icon512.png"
    big.parent.mkdir(exist_ok=True)
    pygame.image.save(surf, str(big))
    subprocess.run(["convert", str(big), "-define", "icon:auto-resize=256,128,64,48,32,16",
                    str(ROOT / "packaging" / "echosketch.ico")], check=True)
    print("icon written")


if __name__ == "__main__":
    main()
