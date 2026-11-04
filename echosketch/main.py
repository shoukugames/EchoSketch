# EchoSketch - a sound matching game for young children
# Copyright (C) 2026 Shawn Rapaz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Application entry point and main loop."""
import argparse
import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame  # noqa: E402

from . import __app_name__, __version__  # noqa: E402
from .audio import Audio  # noqa: E402
from .paths import ASSETS  # noqa: E402
from .progress import Progress  # noqa: E402
from .ui import H, W, Sky  # noqa: E402


class App:
    def __init__(self, windowed=False):
        pygame.init()
        pygame.display.set_caption(f"{__app_name__} v{__version__}")
        try:
            pygame.display.set_icon(pygame.image.load(str(ASSETS / "icon.png")))
        except (pygame.error, FileNotFoundError):
            pass
        self.progress = Progress()
        flags = pygame.SCALED | pygame.RESIZABLE
        self.screen = pygame.display.set_mode((W, H), flags, vsync=1)
        if self.progress.settings.get("fullscreen") and not windowed:
            pygame.display.toggle_fullscreen()
        pygame.key.stop_text_input()     # only the name screen needs typing
        self.audio = Audio(self.progress.settings.get("music", True))
        self.clock = pygame.time.Clock()
        self.player = self.progress.get(self.progress.data.get("last_player"))
        self._skies = {}
        self.running = True
        from .scenes import TitleScene
        self.scene = TitleScene(self)
        self.next_scene = None

    def sky(self, tint=None):
        if tint not in self._skies:
            self._skies[tint] = Sky(tint)
        return self._skies[tint]

    def go(self, scene):
        self.next_scene = scene

    def select_player(self, p):
        self.player = p
        self.progress.data["last_player"] = p["id"]
        self.progress.save()

    def toggle_music(self):
        self.audio.music_on = not self.audio.music_on
        self.progress.settings["music"] = self.audio.music_on
        self.progress.save()

    def toggle_fullscreen(self):
        pygame.display.toggle_fullscreen()
        self.progress.settings["fullscreen"] = not self.progress.settings.get("fullscreen", False)
        self.progress.save()

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.05)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_m and \
                        e.mod & (pygame.KMOD_CTRL | pygame.KMOD_ALT) == 0 and \
                        not getattr(self.scene, "wants_text", False):
                    self.toggle_music()
                else:
                    self.scene.handle(e)
            self.audio.update(dt)
            self.scene.update(dt)
            if self.next_scene is not None:
                self.scene, self.next_scene = self.next_scene, None
                continue
            self.scene.draw(self.screen)
            pygame.display.flip()
        pygame.quit()


def main(argv=None):
    ap = argparse.ArgumentParser(prog="echosketch", description="EchoSketch - listen, look and learn.")
    ap.add_argument("--version", action="version", version=f"{__app_name__} {__version__}")
    ap.add_argument("--windowed", action="store_true", help="start in a window even if fullscreen was saved")
    args = ap.parse_args(argv)
    App(windowed=args.windowed).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
