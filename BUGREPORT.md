# Reporting a Bug in EchoSketch

Thank you for helping make EchoSketch better for kids!

**Email:** <info@shoukugames.org>  
**Website:** <https://shoukugames.org/>

Please use the subject line **`[EchoSketch v0.1.0] short description`**, and copy the
template below into your message.

## Before you report

- Check you have the latest version (the version is shown at the bottom left of the
  title screen, or run `echosketch --version`).
- If there is no sound, check that the computer volume is up and that music is not
  switched off with the 🎵 button. (The music button affects only background music.)
- If the game will not start after a crash, try starting it in a window with
  `echosketch --windowed`.

## Bug report template

```
EchoSketch version:      (e.g. v0.1.0)
Operating system:        (e.g. Windows 11, Ubuntu 24.04, Debian 12)
Installed from:          (.deb / .exe / source)
Screen / full screen?:   (e.g. 1920x1080, full screen)
Language:                (English / 日本語)

What happened:
(Describe the problem.)

What I expected:
(What should have happened?)

Steps to make it happen again:
1.
2.
3.

How often:               (every time / sometimes / once)
Level and sound (if it is about a sound or picture):
(e.g. Level 3 "Around the House", the Doorbell sound)

Screenshot or video:     (attach if you can)
```

## Wrong or unclear sounds

EchoSketch uses real-world recordings. If a sound is confusing, too quiet, too loud, or
does not match its picture, please tell us the **level** and the **word shown** (for
example *"Things That Go - Ship"* or *"のりもの - ふね"*). The same goes for a spoken word,
letter or kana that sounds wrong in either language. These reports are especially helpful.

日本語での不具合報告も歓迎です。上のテンプレートを日本語で書いていただいてかまいません。

## Helpful files

If the problem involves saving or progress, please attach your progress file (it holds
only player names, chosen buddies and answers):

- Linux: `~/.local/share/EchoSketch/progress.json`
- Windows: `%APPDATA%\EchoSketch\progress.json`

If you start the game from a terminal (`echosketch` on Linux), copy any error text it
prints into your report.

## Security or privacy issues

EchoSketch works fully offline and does not collect or send data. If you find a
security or privacy problem, email <info@shoukugames.org> with **SECURITY** in the
subject and please do not post it publicly.
