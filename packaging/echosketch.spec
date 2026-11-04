# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for EchoSketch.  ONEFILE=1 builds a single executable
# (used for the Windows .exe); otherwise a folder build (used for the .deb).
import os
import sys

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
ONEFILE = os.environ.get("ONEFILE") == "1"
WINDOWS = sys.platform.startswith("win")

a = Analysis(
    [os.path.join(SPECPATH, "run_echosketch.py")],
    pathex=[ROOT],
    datas=[(os.path.join(ROOT, "assets"), "assets"), (os.path.join(ROOT, "LICENSE"), ".")],
    hiddenimports=[],
    excludes=["tkinter", "numpy", "unittest", "pydoc", "test"],
    noarchive=False,
)
pyz = PYZ(a.pure)
icon = os.path.join(SPECPATH, "echosketch.ico") if WINDOWS else None
version = os.path.join(SPECPATH, "windows", "version_info.txt") if WINDOWS else None

if ONEFILE:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="EchoSketch", console=False, icon=icon,
              version=version, upx=False, runtime_tmpdir=None)
else:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="echosketch", console=False, icon=icon,
              version=version, upx=False)
    coll = COLLECT(exe, a.binaries, a.datas, name="echosketch", upx=False)
