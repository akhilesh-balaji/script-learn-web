"""
Language data for Telugu (తెలుగు).

Structure (required for every language in langs/<name>/data.py):
  TITLE          - display title shown in the header bar
  CONSONANTS     - base consonant glyph -> romanization (carries an inherent
                   vowel sound, e.g. "క" -> "ka"; the trailing vowel letter is
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

TITLE = "(౷) తెలుగు లిపి"

CONSONANTS = {
    "క": "ka",
    "ఖ": "kha",
    "గ": "ga",
    "ఘ": "gha",
    "ఙ": "nga",  # "~Nga"
    "చ": "ca",
    "ఛ": "cha",
    "జ": "ja",
    "ఝ": "jha",
    "ఞ": "nya",  # "~na"
    "ట": "Ta",
    "ఠ": "Tha",
    "డ": "Da",
    "ఢ": "Dha",
    "ణ": "Na",
    "త": "ta",
    "థ": "tha",
    "ద": "da",
    "ధ": "dha",
    "న": "na",
    "ప": "pa",
    "ఫ": "pha",
    "బ": "ba",
    "భ": "bha",
    "మ": "ma",
    "య": "ya",
    "ర": "ra",
    "ల": "la",
    "వ": "va",
    "శ": "sha",  # "Sa"
    "ష": "sha",  # "S.a"
    "స": "sa",
    "హ": "ha",
}

VOWELS = {
    "ా": "A",
    "ి": "i",
    "ీ": "I",
    "ు": "u",
    "ూ": "U",
    "ె": "e",
    "ే": "E",
    "ై": "ai",
    "ొ": "o",
    "఑": "^O",
    "ో": "O",
    "ౌ": "au",
    "ృ": "r",  # "r."
    "ౄ": "R",  # "R."
    "ౢ": "l",  # "l."
    "ౣ": "L",  # "L."
    "ం": "m.",
    "ః": ":",
    "్": "",
    "ఁ": "m.",
}

VOWELS_SEP = {
    "అ": "a",
    "ఆ": "A",
    "ఇ": "i",
    "ఈ": "I",
    "ఉ": "u",
    "ఊ": "U",
    "ఎ": "e",
    "ఏ": "E",
    "ఐ": "ai",
    "ఒ": "o",
    "ఓ": "O",
    "ఔ": "au",
    "ఋ": "r",  # "r."
    "ౠ": "R",  # "R."
    "ఌ": "l",  # "l."
    "ౡ": "L",  # "L."
    "అం": "am.",
    "అః": "a:",
    "అఁ": "am.",
}

LEARNING_PATH = ["vow", "cons", "vow+cons", "cons+cons"]
