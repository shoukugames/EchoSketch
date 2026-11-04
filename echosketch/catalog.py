# EchoSketch - a sound matching game for young children
# Copyright (C) 2026 Shawn Rapaz
# SPDX-License-Identifier: GPL-3.0-or-later
"""The catalog of every sound in the game and how the levels are built.

Each item maps an id to:
  name      - the word shown, spelled and spoken
  category  - used to build levels and to choose look-alike distractors
  emoji     - Twemoji code point(s) for the cartoon picture
  source    - Wikimedia Commons file the real recording comes from
  clip      - (optional) length in seconds kept from the loudest part
"""

CATEGORIES = {
    "farm": "Farm Friends",
    "wild": "Wild Animals",
    "home": "Around the House",
    "go": "Things That Go",
    "nature": "Nature Sounds",
    "music": "Music Makers",
}

ITEMS = {
    # ---- farm -------------------------------------------------------------
    "dog":      dict(name="Dog",      category="farm", emoji="1f415", source="Barking of a dog 2.ogg"),
    "cat":      dict(name="Cat",      category="farm", emoji="1f408", source="Meow of a pleading cat.oga"),
    "cow":      dict(name="Cow",      category="farm", emoji="1f404", source="Single Cow Moo.ogg"),
    "pig":      dict(name="Pig",      category="farm", emoji="1f416", source=["Mudchute pig 1.ogg", "Mudchute pig 2.ogg", "Mudchute pig 3.ogg", "Pig grunt - Erdie.ogg"]),
    "sheep":    dict(name="Sheep",    category="farm", emoji="1f411", source="Sheep bleating.ogg"),
    "duck":     dict(name="Duck",     category="farm", emoji="1f986", source=["Mudchute duck 1.ogg", "Mudchute duck 2.ogg"]),
    "horse":    dict(name="Horse",    category="farm", emoji="1f40e", source="Wiehern.ogg"),
    "rooster":  dict(name="Rooster",  category="farm", emoji="1f413", source="Medium rooster crowing.ogg"),
    "hen":      dict(name="Hen",      category="farm", emoji="1f414", source="Hen announcing shes lain an egg.ogg"),
    # ---- wild -------------------------------------------------------------
    "lion":     dict(name="Lion",     category="wild", emoji="1f981", source="Lion raring-sound1TamilNadu178.ogg"),
    "elephant": dict(name="Elephant", category="wild", emoji="1f418", source="Elephant voice - trumpeting.ogg"),
    "chimp":    dict(name="Chimp",    category="wild", emoji="1f412", source="Pant-hoot call made by a male chimpanzee.ogg"),
    "owl":      dict(name="Owl",      category="wild", emoji="1f989", source="Strix aluco - Tawny Owl XC500920.mp3"),
    "wolf":     dict(name="Wolf",     category="wild", emoji="1f43a", source="Wolf howls.ogg", clip=7),
    "bee":      dict(name="Bee",      category="wild", emoji="1f41d", source="Bee buzzing sound (animal noises).opus"),
    "frog":     dict(name="Frog",     category="wild", emoji="1f438", source="Single Frog Croak.oga"),
    "crow":     dict(name="Crow",     category="wild", emoji="1f426-200d-2b1b", source="Corvus corone - Carrion Crow XC509838.mp3"),
    # ---- home -------------------------------------------------------------
    "doorbell": dict(name="Doorbell",  category="home", emoji="1f514", source="Doorbell-cheap-dingdong.ogg"),
    "phone":    dict(name="Telephone", category="home", emoji="260e", source="Model 500 Telephone British ring.ogg"),
    "clock":    dict(name="Clock",     category="home", emoji="1f570", source="Clock ticking.ogg"),
    "alarm":    dict(name="Alarm Clock", category="home", emoji="23f0", source="Mechanical Clock Ring (Directory.Audio).mp3"),
    "toilet":   dict(name="Toilet",    category="home", emoji="1f6bd", source="Toilet flush.flac", clip=7),
    "knock":    dict(name="Door",      category="home", emoji="1f6aa", source="Knocking on wood or door.ogg"),
    "baby":     dict(name="Baby",      category="home", emoji="1f476", source="Baby long wanting cry.ogg"),
    "tap":      dict(name="Water Tap", category="home", emoji="1f6b0", source="Faucet water into sink.ogg"),
    "sneeze":   dict(name="Sneeze",    category="home", emoji="1f927", source="Sneezing.ogg"),
    "laugh":    dict(name="Laugh",     category="home", emoji="1f606", source="Four Years Old child laughing.ogg"),
    "brush":    dict(name="Toothbrush", category="home", emoji="1faa5", source="Brushing teeth.ogg"),
    # ---- go ---------------------------------------------------------------
    "car":      dict(name="Car",        category="go", emoji="1f697", source="Car Horn.wav"),
    "train":    dict(name="Train",      category="go", emoji="1f682", source="WWS SteamWhistle.ogg"),
    "plane":    dict(name="Airplane",   category="go", emoji="2708", source="428086 inspectorj airplane-boeing-flyby-right-to-left-a.wav", clip=7),
    "firetruck": dict(name="Fire Truck", category="go", emoji="1f692", source="WWS Fireenginesiren.ogg"),
    "police":   dict(name="Police Car", category="go", emoji="1f693", source="American police siren i.ogg"),
    "helicopter": dict(name="Helicopter", category="go", emoji="1f681", source="Helicopter over a lake.ogg"),
    "motorbike": dict(name="Motorbike", category="go", emoji="1f3cd", source="Motorbike 2.ogg"),
    "bicycle":  dict(name="Bicycle",    category="go", emoji="1f6b2", source="Bicycle-bell-1.wav"),
    "ship":     dict(name="Ship",       category="go", emoji="1f6a2", source="Cruise ship Albatros ship horn.ogg", clip=7),
    # ---- nature -----------------------------------------------------------
    "rain":     dict(name="Rain",     category="nature", emoji="1f327", source="Rain against the window.ogg"),
    "thunder":  dict(name="Thunder",  category="nature", emoji="1f329", source="Thunder 01.ogg", clip=7),
    "waves":    dict(name="Waves",    category="nature", emoji="1f30a", source="Sea waves.wav", clip=7),
    "wind":     dict(name="Wind",     category="nature", emoji="1f32c", source="Wind in Swedish pine forest at 25 mps.ogg"),
    "birds":    dict(name="Birds",    category="nature", emoji="1f426", source="Birds chirping in a garden.ogg"),
    "cricket":  dict(name="Cricket",  category="nature", emoji="1f997", source="Field cricket Gryllus pennsylvanicus.ogg"),
    # ---- music ------------------------------------------------------------
    "drum":     dict(name="Drum",     category="music", emoji="1f941", source="Drum beat.ogg"),
    "piano":    dict(name="Piano",    category="music", emoji="1f3b9", source="Beethoven Piano Sonata Op 22, 2nd movement, bars 30-32.wav", clip=7),
    "guitar":   dict(name="Guitar",   category="music", emoji="1f3b8", source="Audio files of spanish guitar chords 18.wav"),
    "trumpet":  dict(name="Trumpet",  category="music", emoji="1f3ba", source="Trumpet playing short excerpt for comparison with flugelhorn.ogg"),
    "violin":   dict(name="Violin",   category="music", emoji="1f3bb", source="Violin chords.ogg"),
    "flute":    dict(name="Flute",    category="music", emoji="1fa88", source="Flute 2.ogg"),
    "maracas":  dict(name="Maracas",  category="music", emoji="1fa87", source="Maracas.ogg"),
    "bell":     dict(name="Church Bell", category="music", emoji="26ea", source="Samariter Church Bell II (g).ogg"),
}

# Level design.  Difficulty rises three ways:
#   * the sounds themselves get less familiar,
#   * distractors move from "obviously different" (other categories) to
#     "sounds alike" (same category),
#   * the written word is hidden under the pictures on the hardest levels.
# "similar" = how many of the 3 wrong answers come from the same category.
LEVELS = [
    dict(title="Farm Friends",     pool=["farm"],   rounds=6, similar=0, labels=True,  color=(255, 179, 71)),
    dict(title="Wild Animals",     pool=["wild"],   rounds=6, similar=0, labels=True,  color=(129, 199, 132)),
    dict(title="Around the House", pool=["home"],   rounds=7, similar=1, labels=True,  color=(100, 181, 246)),
    dict(title="Things That Go",   pool=["go"],     rounds=7, similar=1, labels=True,  color=(239, 83, 80)),
    dict(title="Nature Sounds",    pool=["nature"], rounds=6, similar=2, labels=True,  color=(77, 182, 172)),
    dict(title="Music Makers",     pool=["music"],  rounds=7, similar=2, labels=True,  color=(186, 104, 200)),
    dict(title="Animal Expert",    pool=["farm", "wild"], rounds=8, similar=3, labels=False, color=(255, 138, 101)),
    dict(title="Sound Master",     pool=list(CATEGORIES), rounds=10, similar=3, labels=False, color=(255, 213, 79)),
]

ROUND_SECONDS = 99
CHOICES = 4
