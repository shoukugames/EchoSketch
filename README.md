# EchoSketch

**Listen • Look • Learn** — a sound matching game for young children.

| | |
|---|---|
| Version | **v0.1.0** (released November 5, 2026) |
| Recommended ages | **3+** |
| Created by | Shawn Rapaz & Claude Code |
| Website | <https://shoukugames.org/> |
| Contact | <info@shoukugames.org> |
| Licence | [GNU GPL v3.0](LICENSE) |

EchoSketch plays a **real-world sound** — a dog barking, a doorbell, a fire truck, rain —
and your child picks the matching cartoon picture from four choices. Every answer is
**spoken aloud and spelled letter by letter** while each letter lights up, so children
connect the sound, the picture, the spoken word and its spelling.

## How to play

1. Press **Play!** and choose (or create) a player.
2. Pick a level. Level 1 is open; finishing a level unlocks the next.
3. Listen to the sound. Tap the big orange **speaker** to hear it again.
4. Tap the picture that makes that sound.
   - **Right:** confetti! The word is said, spelled, and said again.
   - **Wrong:** the card is crossed out, the sound replays, and your child can try again.
   - **Out of time:** each round has **99 seconds**. When time runs out the answer is shown,
     spoken and spelled, and your child can move on.
5. Press **Next** for the next sound. At the end of a level you earn up to 3 stars.

Keyboard: `1`–`4` choose a card, `Space` replays the sound, `Enter` continues,
`Esc` goes back, `M` toggles music, `F11` toggles full screen, `L` (title screen) switches
language.

## English and Japanese / 日本語

EchoSketch is fully playable in **English** or **Japanese**. Press the **日本語 / English**
button at the top left of the title screen (or `L`) to switch. The choice is remembered;
on first start the game follows the computer's language. You can also start with
`echosketch --lang ja` or `--lang en`.

In Japanese, everything changes: the screens, the spoken voice, the names of the sounds
(いぬ, しょうぼうしゃ, ヘリコプター…), and the spelling, which is shown and spoken kana by
kana (small ゃ/ゅ/ょ stay with their kana, ッ is read ちいさい つ and ー is read のばしぼう).
Child-facing text is written in kana with spaces between phrases, like a picture book; the
grown-ups area uses ordinary Japanese. Player names can be typed with a Japanese input
method. People's names, web addresses and the original titles of the sound recordings in
the credits stay as written.

## Levels

Difficulty grows in three ways: the sounds get less familiar, the wrong answers get more
similar (from "a cow vs. a drum" up to "a cow vs. a sheep"), and the words under the
pictures are hidden on the last two levels.

| # | Level | Sounds | Look-alike choices | Words shown |
|---|---|---|---|---|
| 1 | Farm Friends | farm animals | none | yes |
| 2 | Wild Animals | wild animals | none | yes |
| 3 | Around the House | doorbell, phone, toilet… | 1 of 3 | yes |
| 4 | Things That Go | car, train, helicopter… | 1 of 3 | yes |
| 5 | Nature Sounds | rain, thunder, waves… | 2 of 3 | yes |
| 6 | Music Makers | drum, piano, violin… | 2 of 3 | yes |
| 7 | Animal Expert | all animals | 3 of 3 | no |
| 8 | Sound Master | all 51 sounds | 3 of 3 | no |

Sounds your child has found tricky come up more often in later games.

## For grown-ups: progress reports

On the title screen, **press and hold "Grown-ups" for 2 seconds** (this keeps little
fingers out). For each player you can see:

- **Overview:** rounds played, % right first time, sounds known, average answer time,
  times the timer ran out, and stars for every level.
- **Needs practice:** every sound your child missed, how often, **which pictures they
  chose instead** (e.g. heard *Sheep*, picked *Cow*), and how often time ran out.
  Press ▶ to hear the sound with its name and spelling. **Practice these** starts a
  game made only of those sounds. A sound gets a "now OK" tag once it is answered
  right first time after a miss.
- **Recent answers:** a timeline of every answer.

You can also reset a player's progress or delete a player. Progress is saved to:

- Linux: `~/.local/share/EchoSketch/progress.json`
- Windows: `%APPDATA%\EchoSketch\progress.json`

**Tip:** the game works best when you take it outside. When you hear a real doorbell,
a passing motorbike or birds in the park, ask "What's that sound?"

## Install

### Linux (Debian, Ubuntu, Mint and similar, 64-bit)

```sh
sudo apt install ./echosketch_0.1.0_amd64.deb
echosketch            # or find "EchoSketch" in your applications menu
```

Uninstall with `sudo apt remove echosketch`.

### Windows (64-bit)

Download `EchoSketch-0.1.0-win64.exe` and double-click it. No installation needed.
Windows SmartScreen may warn about an unsigned app. Choose *More info → Run anyway*.

### From source

```sh
python3 -m pip install pygame
python3 -m echosketch
```

## Building

The game needs only Python 3.9+ and pygame 2. The asset pipeline and packaging need more:

| Step | Command | Needs |
|---|---|---|
| Real sounds | `tools/fetch_sounds.py` | internet, ffmpeg, numpy |
| Pictures & fonts | `tools/fetch_images_fonts.py` | internet, rsvg-convert |
| Spoken words | `tools/make_voice.py --lang en\|ja --model kokoro-v1.0.onnx --voices voices-v1.0.bin` | kokoro-onnx, soundfile, ffmpeg; misaki[ja] + unidic-lite for Japanese |
| Music & effects | `tools/make_music.py` | numpy, ffmpeg |
| Icon | `tools/make_icon.py` | pygame, ImageMagick |
| Credits file | `tools/make_credits.py` | — |
| `.deb` | `packaging/build_deb.sh` | PyInstaller, dpkg-deb |
| `.exe` | `packaging/build_exe.sh` | Wine + Windows Python with pygame & PyInstaller |

All generated assets are committed, so you only need the last two steps to package.
Build output goes to `build/` and `dist/` (both git-ignored).

## Project layout

```
echosketch/      game code (catalog.py lists every sound and level, i18n.py all text in both languages)
assets/          sounds, voice (Japanese in voice/ja), pictures, music, fonts, icon
tools/           scripts that produce the assets
packaging/       PyInstaller spec, .deb and .exe build scripts
```

## Credits and licence

EchoSketch is free software under the **GNU General Public License v3.0**. See [LICENSE](LICENSE).
Real-world sound recordings come from Wikimedia Commons, pictures from Twemoji
(CC-BY 4.0), fonts (Andika, Fredoka, and M PLUS Rounded 1c for Japanese) are under the
SIL OFL, and the voice is the Kokoro-82M neural text-to-speech model (Apache-2.0), voices
`af_heart` (English) and `jf_alpha` (Japanese). Full per-file attribution is in [CREDITS.md](CREDITS.md) and in the
in-game Credits screen.

Found a problem? See [BUGREPORT.md](BUGREPORT.md).
