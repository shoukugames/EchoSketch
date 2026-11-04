# EchoSketch - a sound matching game for young children
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Locations of bundled assets and of the per-user save data."""
import os
import sys
from pathlib import Path

from . import __app_name__


def _resource_root() -> Path:
    if getattr(sys, "frozen", False):          # PyInstaller bundle
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


ASSETS = _resource_root() / "assets"


def data_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    path = base / __app_name__
    path.mkdir(parents=True, exist_ok=True)
    return path
