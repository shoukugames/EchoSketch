#!/usr/bin/env bash
# Build the Windows single-file .exe with PyInstaller running under Wine.
# Needs a Windows Python inside Wine with pygame and pyinstaller installed:
#   WINE_PYTHON='C:\py311\python.exe'   (default)
# Output: dist/EchoSketch-<version>-win64.exe
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VERSION="$(python3 -c 'import echosketch; print(echosketch.__version__)')"
WINE_PYTHON="${WINE_PYTHON:-C:\\py311\\python.exe}"
export WINEDEBUG=-all ONEFILE=1
wine "$WINE_PYTHON" -m PyInstaller --noconfirm --clean \
    --distpath "Z:${ROOT}/dist/windows" --workpath "Z:${ROOT}/build/pyinstaller-windows" \
    "Z:${ROOT}/packaging/echosketch.spec" 2>&1 | cat   # Wine Python needs a pipe, not a file, for stdio
mkdir -p dist
cp dist/windows/EchoSketch.exe "dist/EchoSketch-${VERSION}-win64.exe"
echo "Built dist/EchoSketch-${VERSION}-win64.exe"
