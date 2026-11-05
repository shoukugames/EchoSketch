# EchoSketch - a sound matching game for young children
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""Languages: English and Japanese.

Everything the game shows or says goes through here: interface text, the names of the
sounds, level titles, and how a name is spelled out (letters in English, kana in
Japanese). Child-facing Japanese is written in kana with spaces between phrases, as in
picture books; the grown-ups area uses ordinary Japanese.
"""
import locale
import os
import sys

LANGS = ("en", "ja")
_lang = "en"


def set_lang(code):
    global _lang
    _lang = code if code in LANGS else "en"


def lang():
    return _lang


def system_lang():
    """'ja' when the computer is set to Japanese, else 'en'."""
    if sys.platform == "win32":
        try:
            import ctypes
            if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0xFF == 0x11:
                return "ja"
        except Exception:  # noqa: BLE001
            pass
        return "en"
    for var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        if os.environ.get(var):
            return "ja" if os.environ[var].lower().startswith("ja") else "en"
    try:
        loc = locale.getlocale()[0] or ""
    except ValueError:
        loc = ""
    return "ja" if loc.lower().startswith("ja") else "en"


# ---------------------------------------------------------------------------
# Interface text
# ---------------------------------------------------------------------------
STRINGS = {
    "en": {
        "app_name": "EchoSketch",
        "tagline": "Listen  •  Look  •  Learn",
        "ages_badge": "Ages {ages}",
        "play": "Play!",
        "grownups": "Grown-ups",
        "credits": "Credits",
        "quit": "Quit",
        "lang_button": "日本語",
        "hold_hint": "Grown-ups: keep holding...",
        "who_plays": "Who is playing?",
        "new_player": "New player",
        "type_name": "Grown-ups: type the child's name",
        "name_placeholder": "Name",
        "pick_buddy": "Pick a buddy:",
        "lets_go": "Let's go!",
        "default_player": "Player {n}",
        "hi": "Hi, {name}!",
        "pick_level": "Pick a level",
        "practice_title": "Practice Time",
        "next": "Next",
        "hear_again": "Hear again",
        "tap_listen": "Tap to listen",
        "times_up": "Time's up! It was...",
        "found_it": "You found it!",
        "next_level": "Next level",
        "play_again": "Play again",
        "levels": "Levels",
        "level_complete": "Level complete!",
        "knew_n": "You knew {first} of {total} sounds right away!",
        "listen_again_soon": "Let's listen to these again soon:",
        # grown-ups area
        "tabs": ["Overview", "Needs practice", "Recent answers"],
        "practice_these": "Practice these",
        "reset": "Reset",
        "delete": "Delete",
        "yes": "Yes",
        "no": "No",
        "parents_title": "Grown-ups: Progress",
        "no_players": "No players yet.",
        "no_players_hint": "Press Play on the title screen to add one.",
        "tip": "Tip: point out these sounds in real life - a doorbell, a passing car, birds in the park.",
        "confirm_reset": ("Really reset all progress for", "{name}?"),
        "confirm_delete": ("Really delete the player", "{name}?"),
        "t_rounds": "Rounds played",
        "t_first": "Right first time",
        "t_known": "Sounds known",
        "t_avg": "Average answer",
        "t_timeouts": "Ran out of time",
        "t_stars": "Stars",
        "secs": "{s}s",
        "status_done": "Done",
        "status_ready": "Ready to play",
        "status_locked": "Locked",
        "played_n": "played {n}x",
        "player_since": "Player since {date}",
        "nothing_yet": "Nothing to practise yet - great listening!",
        "nothing_yet_1": "Sounds your child misses or runs out of time on will show here,",
        "nothing_yet_2": "together with the pictures they picked by mistake.",
        "h_sound": "Sound",
        "h_missed": "Missed",
        "h_mixed": "Mixed it up with",
        "m_of_a": "{m} of {a}",
        "timeouts_n": "time ran out {n}x",
        "times_n": "{name} x{n}",
        "no_answer": "(no answer given)",
        "now_ok": "now OK",
        "no_history": "No answers recorded yet.",
        "practice": "Practice",
        "chip_first": "Right first time",
        "chip_timeout": "Time ran out",
        "chip_after_1": "Got it after 1 miss",
        "chip_after_n": "Got it after {n} misses",
        # credits
        "credits_title": "Credits",
        "version_line": "Version {v}  -  released {date}",
        "created_by": "Created by",
        "rec_ages": "Recommended ages",
        "ages_big": "{ages}",
        "licence": "Licence",
        "gpl": ("EchoSketch is free software: you can redistribute it and/or modify it under the terms "
                "of the GNU General Public License as published by the Free Software Foundation, either "
                "version 3 of the License, or (at your option) any later version. It is distributed in "
                "the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied "
                "warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General "
                "Public License (GPL 3.0) for more details."),
        "pictures": "Pictures",
        "pictures_text": ("Cartoon pictures from Twemoji, Copyright 2019 Twitter, Inc and other contributors, "
                          "CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/)."),
        "fonts": "Fonts",
        "fonts_text": ("Andika by SIL International, Fredoka by Milena Brandao and M PLUS Rounded 1c by "
                       "Coji Morishita (M+ Fonts Project), SIL Open Font License 1.1"),
        "voice": "Voice",
        "voice_text": ("Spoken words made with the Kokoro-82M neural text-to-speech model (Apache-2.0), "
                       "voices af_heart (English) and jf_alpha (Japanese)."),
        "music_fx": "Music and effects",
        "music_fx_text": "Original ambient music and sound effects synthesised for EchoSketch (GPL 3.0).",
        "recordings": "Real-world sound recordings (Wikimedia Commons)",
        "recording_line": "{name}: \"{file}\" by {author} ({license})",
        "thanks": "Thank you for playing!",
        "credits_hint": "Scroll or click to pause  •  click a link to open it",
    },
    "ja": {
        "app_name": "エコースケッチ",
        "tagline": "きいて  •  みて  •  まなぼう",
        "ages_badge": "{ages}",
        "play": "あそぶ!",
        "grownups": "おうちの かた",
        "credits": "クレジット",
        "quit": "おわる",
        "lang_button": "English",
        "hold_hint": "おうちの かた: そのまま おしつづけてください…",
        "who_plays": "だれが あそぶ?",
        "new_player": "あたらしい ひと",
        "type_name": "おうちの かた: おこさまの なまえを いれてください",
        "name_placeholder": "なまえ",
        "pick_buddy": "なかまを えらんでね:",
        "lets_go": "はじめよう!",
        "default_player": "プレイヤー {n}",
        "hi": "こんにちは、{name}!",
        "pick_level": "レベルを えらんでね",
        "practice_title": "れんしゅう",
        "next": "つぎへ",
        "hear_again": "もういちど",
        "tap_listen": "タップして きいてね",
        "times_up": "じかんぎれ! こたえは…",
        "found_it": "せいかい!",
        "next_level": "つぎの レベル",
        "play_again": "もういちど",
        "levels": "レベル",
        "level_complete": "レベル クリア!",
        "knew_n": "{total}もんの うち {first}もん すぐに わかったね!",
        "listen_again_soon": "また こんど きいてみようね:",
        # grown-ups area (ordinary Japanese for adults)
        "tabs": ["概要", "練習が必要", "最近の回答"],
        "practice_these": "この音を練習",
        "reset": "リセット",
        "delete": "削除",
        "yes": "はい",
        "no": "いいえ",
        "parents_title": "保護者の方へ：がんばり記録",
        "no_players": "まだプレイヤーがいません。",
        "no_players_hint": "タイトル画面の「あそぶ!」から追加できます。",
        "tip": "ヒント：インターホンや通りすぎる車、公園の鳥など、身のまわりの音を一緒に探してみましょう。",
        "confirm_reset": ("{name} さんの記録を", "すべてリセットしますか?"),
        "confirm_delete": ("プレイヤー「{name}」を", "削除しますか?"),
        "t_rounds": "プレイした問題",
        "t_first": "1回目で正解",
        "t_known": "わかった音",
        "t_avg": "平均回答時間",
        "t_timeouts": "時間切れ",
        "t_stars": "星",
        "secs": "{s}秒",
        "status_done": "クリア",
        "status_ready": "プレイできます",
        "status_locked": "ロック中",
        "played_n": "{n}回プレイ",
        "player_since": "登録日：{date}",
        "nothing_yet": "練習が必要な音はまだありません。よく聞けていますね！",
        "nothing_yet_1": "まちがえた音や時間切れになった音が、ここに表示されます。",
        "nothing_yet_2": "まちがえて選んだ絵も一緒に表示されます。",
        "h_sound": "音",
        "h_missed": "まちがい",
        "h_mixed": "まちがえて選んだ絵",
        "m_of_a": "{a}回中{m}回",
        "timeouts_n": "時間切れ {n}回",
        "times_n": "{name} ×{n}",
        "no_answer": "（回答なし）",
        "now_ok": "克服",
        "no_history": "まだ回答の記録がありません。",
        "practice": "練習",
        "chip_first": "1回目で正解",
        "chip_timeout": "時間切れ",
        "chip_after_1": "1回まちがえて正解",
        "chip_after_n": "{n}回まちがえて正解",
        # credits
        "credits_title": "クレジット",
        "version_line": "バージョン {v}  ・  {date} 公開",
        "created_by": "制作",
        "rec_ages": "対象年齢",
        "ages_big": "{ages}",
        "licence": "ライセンス",
        "gpl": ("EchoSketch はフリーソフトウェアです。あなたはこれを、フリーソフトウェア財団によって発行された"
                "GNU 一般公衆利用許諾書（バージョン3か、希望によってはそれ以降のバージョンのうちどれか）の定める"
                "条件の下で再頒布または改変することができます。EchoSketch は有用であることを願って頒布されますが、"
                "全くの無保証です。商業可能性の保証や特定目的への適合性は、言外に示されたものも含め、全く存在"
                "しません。詳しくは GNU 一般公衆利用許諾書（GPL 3.0）をご覧ください。"),
        "pictures": "イラスト",
        "pictures_text": ("イラストは Twemoji（Copyright 2019 Twitter, Inc and other contributors）、"
                          "CC-BY 4.0（https://creativecommons.org/licenses/by/4.0/）を使用しています。"),
        "fonts": "フォント",
        "fonts_text": ("Andika（SIL International）、Fredoka（Milena Brandao）、M PLUS Rounded 1c"
                       "（森下浩司・M+ Fonts Project）、SIL Open Font License 1.1"),
        "voice": "音声",
        "voice_text": ("音声はニューラル音声合成モデル Kokoro-82M（Apache-2.0）で作成しました。"
                       "声：af_heart（英語）、jf_alpha（日本語）。"),
        "music_fx": "音楽と効果音",
        "music_fx_text": "環境音楽と効果音は EchoSketch のために作ったオリジナルです（GPL 3.0）。",
        "recordings": "実際の音の録音（ウィキメディア・コモンズ）",
        "recording_line": "{name}：「{file}」 録音：{author}（{license}）",
        "thanks": "あそんでくれて ありがとう!",
        "credits_hint": "スクロールかクリックで一時停止  ・  リンクをクリックすると開きます",
    },
}

RELEASE_DATE = {"en": "November 6, 2026", "ja": "2026年11月6日"}
AGES = {"en": "3+", "ja": "3さい から"}
AGES_FULL = {"en": "3+", "ja": "3歳以上"}


def tr(key, **kw):
    s = STRINGS[_lang].get(key, STRINGS["en"][key])
    if kw and isinstance(s, str):
        return s.format(**kw)
    if kw and isinstance(s, tuple):
        return tuple(p.format(**kw) for p in s)
    return s


def format_when(dt):
    """Short date and time for the answer timeline."""
    if _lang == "ja":
        return f"{dt.month}月{dt.day}日 {dt:%H:%M}"
    return dt.strftime("%b %d  %H:%M")


# ---------------------------------------------------------------------------
# Names of the sounds, categories and levels
# ---------------------------------------------------------------------------
ITEM_NAMES_JA = {
    "dog": "いぬ", "cat": "ねこ", "cow": "うし", "pig": "ぶた", "sheep": "ひつじ", "duck": "あひる",
    "horse": "うま", "rooster": "おんどり", "hen": "めんどり",
    "lion": "ライオン", "elephant": "ぞう", "chimp": "チンパンジー", "owl": "ふくろう",
    "wolf": "おおかみ", "bee": "はち", "frog": "かえる", "crow": "からす",
    "doorbell": "チャイム", "phone": "でんわ", "clock": "とけい", "alarm": "めざまし", "toilet": "トイレ",
    "knock": "ドア", "baby": "あかちゃん", "tap": "じゃぐち", "sneeze": "くしゃみ", "laugh": "わらいごえ",
    "brush": "はみがき",
    "car": "くるま", "train": "きしゃ", "plane": "ひこうき", "firetruck": "しょうぼうしゃ",
    "police": "パトカー", "helicopter": "ヘリコプター", "motorbike": "バイク", "bicycle": "じてんしゃ",
    "ship": "ふね",
    "rain": "あめ", "thunder": "かみなり", "waves": "なみ", "wind": "かぜ", "birds": "ことり",
    "cricket": "こおろぎ",
    "drum": "たいこ", "piano": "ピアノ", "guitar": "ギター", "trumpet": "トランペット",
    "violin": "バイオリン", "flute": "フルート", "maracas": "マラカス", "bell": "かね",
}
CATEGORY_NAMES_JA = {
    "farm": "ぼくじょう", "wild": "やせいの どうぶつ", "home": "おうちの おと", "go": "のりもの",
    "nature": "しぜんの おと", "music": "がっき",
}
LEVEL_TITLES_JA = ["ぼくじょうの なかま", "やせいの どうぶつ", "おうちの おと", "のりもの",
                   "しぜんの おと", "がっきの おと", "どうぶつ はかせ", "おとの めいじん"]


def item_name(key):
    from .catalog import ITEMS
    return ITEM_NAMES_JA[key] if _lang == "ja" else ITEMS[key]["name"]


def category_name(cat):
    from .catalog import CATEGORIES
    return CATEGORY_NAMES_JA[cat] if _lang == "ja" else CATEGORIES[cat]


def level_title(i):
    from .catalog import LEVELS
    return LEVEL_TITLES_JA[i] if _lang == "ja" else LEVELS[i]["title"]


# ---------------------------------------------------------------------------
# Spelling: letters in English, kana (morae) in Japanese
# ---------------------------------------------------------------------------
SMALL_KANA = set("ゃゅょぁぃぅぇぉゎャュョァィゥェォヮ")
KANA_SPOKEN = {"っ": "ちいさい つ", "ッ": "ちいさい つ", "ー": "のばしぼう"}


def spell_units(word):
    """Split a word into the pieces that are highlighted and spoken one by one.

    English: one letter each (spaces kept so the word lays out naturally).
    Japanese: one kana each, with small ゃ/ゅ/ょ... joined to the kana before them.
    """
    units = []
    for ch in word:
        if ch in SMALL_KANA and units and units[-1] != " ":
            units[-1] += ch
        else:
            units.append(ch)
    return units


def is_spoken(unit):
    return unit.strip() != "" and unit not in "-'"


def unit_file(unit):
    """Voice file (relative to assets/voice) that says this spelling unit."""
    if unit.isascii():
        return f"letter_{unit.lower()}.ogg"
    return "ja/kana_" + "-".join(f"{ord(c):04x}" for c in unit) + ".ogg"


def unit_speech(unit):
    return KANA_SPOKEN.get(unit, unit)
