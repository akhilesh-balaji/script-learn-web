"""
Language data for Devanagari (देवनागरी).

Structure (required for every language in langs/<name>/data.py):
  TITLE          - display title shown in the header bar
  CONSONANTS     - base consonant glyph -> romanization (carries an inherent
                   vowel sound, e.g. "क" -> "ka"; the trailing vowel letter is
                   chopped off when a dependent vowel sign follows the
                   consonant in transliterate())
  VOWELS         - dependent vowel signs / matras (attach to a consonant) ->
                   romanization. Include the virama/halant with value "" --
                   it's used to build consonant clusters in learning mode.
  VOWELS_SEP     - independent vowel letters (stand alone, start a word) ->
                   romanization
  LEARNING_PATH  - ordered curriculum stages, e.g.
                   ["vow", "cons", "vow+cons", "cons+cons"]
"""

TITLE = "(ꣷ) देवनागरी लिपि"

CONSONANTS = {
    "क": "ka",
    "ख": "kha",
    "ग": "ga",
    "घ": "gha",
    "ङ": "nga",  # "~Nga"
    "च": "ca",
    "छ": "cha",
    "ज": "ja",
    "झ": "jha",
    "ञ": "nya",  # "~na"
    "ट": "Ta",
    "ठ": "Tha",
    "ड": "Da",
    "ढ": "Dha",
    "ण": "Na",
    "त": "ta",
    "थ": "tha",
    "द": "da",
    "ध": "dha",
    "न": "na",
    "प": "pa",
    "फ": "pha",
    "ब": "ba",
    "भ": "bha",
    "म": "ma",
    "य": "ya",
    "र": "ra",
    "ल": "la",
    "व": "va",
    "श": "sha",  # "Sa"
    "ष": "sha",  # "S.a"
    "स": "sa",
    "ह": "ha",
}

VOWELS = {
    "ा": "A",
    "ि": "i",
    "ी": "I",
    "ु": "u",
    "ू": "U",
    "ॆ": "e",
    "े": "E",
    "ै": "ai",
    "ॊ": "o",
    "ॉ": "^O",
    "ो": "O",
    "ौ": "au",
    "ृ": "r",  # "r."
    "ॄ": "R",  # "R."
    "ॢ": "l",  # "l."
    "ॣ": "L",  # "L."
    "ं": "m.",
    "ः": ":",
    "्": "",
    "ँ": "m.",
}

VOWELS_SEP = {
    "अ": "a",
    "आ": "A",
    "ऑ": "^O",
    "इ": "i",
    "ई": "I",
    "उ": "u",
    "ऊ": "U",
    "ऎ": "e",
    "ए": "E",
    "ऐ": "ai",
    "ऒ": "o",
    "ओ": "O",
    "औ": "au",
    "ऋ": "r",  # "r."
    "ॠ": "R",  # "R."
    "ऌ": "l",  # "l."
    "ॡ": "L",  # "L."
    "अं": "am.",
    "अः": "a:",
    "अँ": "am.",
}

LEARNING_PATH = ["vow", "cons", "vow+cons", "cons+cons"]
