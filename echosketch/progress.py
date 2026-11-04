# EchoSketch - a sound matching game for young children
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Player profiles and the record of every answer, for the parents' area."""
import json
import os
import time
import uuid
from collections import Counter, defaultdict
from datetime import datetime

from .catalog import ITEMS, LEVELS
from .paths import data_dir

SAVE_VERSION = 1
HISTORY_LIMIT = 3000


class Progress:
    def __init__(self, path=None):
        self.path = path or data_dir() / "progress.json"
        self.data = {"version": SAVE_VERSION, "settings": {"music": True, "fullscreen": False},
                     "players": [], "last_player": None}
        self.load()

    # ---- persistence -----------------------------------------------------
    def load(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict) and isinstance(loaded.get("players"), list):
                self.data.update(loaded)
                self.data["settings"] = {"music": True, "fullscreen": False, **loaded.get("settings", {})}
        except FileNotFoundError:
            pass
        except (OSError, ValueError):
            # keep a copy of a damaged file instead of silently losing it
            try:
                os.replace(self.path, str(self.path) + ".broken")
            except OSError:
                pass

    def save(self):
        tmp = str(self.path) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=1)
        os.replace(tmp, self.path)

    # ---- settings --------------------------------------------------------
    @property
    def settings(self):
        return self.data["settings"]

    # ---- players ---------------------------------------------------------
    @property
    def players(self):
        return self.data["players"]

    def add_player(self, name, avatar):
        p = {"id": uuid.uuid4().hex[:12], "name": name.strip()[:14] or "Player", "avatar": avatar,
             "created": datetime.now().isoformat(timespec="seconds"), "levels": {}, "history": []}
        self.players.append(p)
        self.data["last_player"] = p["id"]
        self.save()
        return p

    def remove_player(self, pid):
        self.data["players"] = [p for p in self.players if p["id"] != pid]
        if self.data["last_player"] == pid:
            self.data["last_player"] = None
        self.save()

    def reset_player(self, pid):
        p = self.get(pid)
        if p:
            p["levels"], p["history"] = {}, []
            self.save()

    def get(self, pid):
        return next((p for p in self.players if p["id"] == pid), None)

    # ---- levels ----------------------------------------------------------
    @staticmethod
    def level_info(player, index):
        return player["levels"].get(str(index), {"stars": 0, "completed": False, "plays": 0})

    def unlocked(self, player, index):
        return index == 0 or self.level_info(player, index - 1)["completed"]

    def finish_level(self, player, index, stars):
        info = dict(self.level_info(player, index))
        info["completed"] = True
        info["plays"] = info.get("plays", 0) + 1
        info["stars"] = max(info.get("stars", 0), stars)
        info["last"] = datetime.now().isoformat(timespec="seconds")
        player["levels"][str(index)] = info
        self.save()

    # ---- answer records --------------------------------------------------
    def record(self, player, level, item, result, wrong_picks, seconds):
        """result is 'first_try', 'after_mistakes' or 'timeout'."""
        player["history"].append({
            "t": int(time.time()), "level": level, "item": item, "result": result,
            "wrong": list(wrong_picks), "secs": round(seconds, 1)})
        del player["history"][:-HISTORY_LIMIT]
        self.save()

    # ---- reporting for the parents' area ----------------------------------
    @staticmethod
    def summary(player):
        h = player["history"]
        total = len(h)
        first = sum(1 for r in h if r["result"] == "first_try")
        timeouts = sum(1 for r in h if r["result"] == "timeout")
        correct_times = [r["secs"] for r in h if r["result"] != "timeout"]
        return {
            "rounds": total,
            "first_try": first,
            "accuracy": (first / total * 100) if total else 0,
            "timeouts": timeouts,
            "avg_secs": (sum(correct_times) / len(correct_times)) if correct_times else 0,
            "stars": sum(Progress.level_info(player, i)["stars"] for i in range(len(LEVELS))),
            "levels_done": sum(1 for i in range(len(LEVELS)) if Progress.level_info(player, i)["completed"]),
            "sounds_known": len({r["item"] for r in h if r["result"] == "first_try"}),
        }

    @staticmethod
    def trouble(player):
        """Sounds the child struggled with, worst first.

        Each entry: item, misses, timeouts, attempts, mixed_up (Counter of the
        wrong pictures chosen), last (timestamp), mastered_since (bool: the
        child answered it first try after the last miss)."""
        stats = defaultdict(lambda: {"misses": 0, "timeouts": 0, "attempts": 0, "mixed_up": Counter(),
                                     "last": 0, "last_ok": 0})
        for r in player["history"]:
            s = stats[r["item"]]
            s["attempts"] += 1
            if r["result"] == "first_try":
                s["last_ok"] = r["t"]
                continue
            s["misses"] += 1
            s["last"] = r["t"]
            if r["result"] == "timeout":
                s["timeouts"] += 1
            s["mixed_up"].update(r["wrong"])
        out = []
        for item, s in stats.items():
            if s["misses"] and item in ITEMS:
                out.append({"item": item, **s, "mastered_since": s["last_ok"] > s["last"]})
        out.sort(key=lambda e: (e["mastered_since"], -e["misses"], -e["last"]))
        return out
