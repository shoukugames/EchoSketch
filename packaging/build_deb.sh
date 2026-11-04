#!/usr/bin/env bash
# Build the Linux binary with PyInstaller and wrap it in a .deb package.
# Output: dist/echosketch_<version>_amd64.deb
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VERSION="$(python3 -c 'import echosketch; print(echosketch.__version__)')"
PKG="echosketch_${VERSION}_amd64"
STAGE="build/deb/$PKG"

python3 -m PyInstaller --noconfirm --clean --distpath dist/linux --workpath build/pyinstaller-linux \
    packaging/echosketch.spec

rm -rf "$STAGE"
mkdir -p "$STAGE/DEBIAN" "$STAGE/opt" "$STAGE/usr/bin" "$STAGE/usr/share/applications" \
         "$STAGE/usr/share/icons/hicolor/256x256/apps" "$STAGE/usr/share/doc/echosketch"
cp -a dist/linux/echosketch "$STAGE/opt/echosketch"
ln -s /opt/echosketch/echosketch "$STAGE/usr/bin/echosketch"
install -m644 packaging/linux/echosketch.desktop "$STAGE/usr/share/applications/"
install -m644 assets/icon.png "$STAGE/usr/share/icons/hicolor/256x256/apps/echosketch.png"
install -m644 README.md "$STAGE/usr/share/doc/echosketch/README.md"
install -m644 CREDITS.md "$STAGE/usr/share/doc/echosketch/CREDITS.md"
cat > "$STAGE/usr/share/doc/echosketch/copyright" <<COPY
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: EchoSketch
Upstream-Contact: info@shoukugames.org
Source: https://shoukugames.org/

Files: *
Copyright: 2026 Shawn Rapaz
License: GPL-3+
 On Debian systems the full text of the GNU General Public License
 version 3 can be found in /usr/share/common-licenses/GPL-3.
 Third-party assets (sounds, pictures, fonts, voice) are listed with
 their licences in /usr/share/doc/echosketch/CREDITS.md.
COPY
printf 'echosketch (%s) stable; urgency=low\n\n  * First release.\n\n -- Shawn Rapaz <info@shoukugames.org>  %s\n' \
    "$VERSION" "$(date -R)" | gzip -9n > "$STAGE/usr/share/doc/echosketch/changelog.gz"
SIZE="$(du -sk "$STAGE" | cut -f1)"
sed -e "s/@VERSION@/$VERSION/" -e "s/@SIZE@/$SIZE/" packaging/linux/control.in > "$STAGE/DEBIAN/control"
find "$STAGE" -type d -exec chmod 755 {} +
mkdir -p dist
dpkg-deb --root-owner-group --build "$STAGE" "dist/$PKG.deb"
echo "Built dist/$PKG.deb"
