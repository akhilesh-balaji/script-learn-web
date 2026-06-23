"""
Language data for Tamil (தமிழ்).

Structure (required for every language in langs/<name>/data.py):
  TITLE          - display title shown in the header bar
  CONSONANTS     - base consonant glyph -> romanization (carries an inherent
                   vowel sound, e.g. "க" -> "ka"; the trailing vowel letter is
                   chopped off when a dependent vowel sign follows the
                   consonant in transliterate())
  VOWELS         - dependent vowel signs / matras (attach to a consonant) ->
                   romanization. Include the virama/pulli with value "" --
                   it's used to build consonant clusters in learning mode.
  VOWELS_SEP     - independent vowel letters (stand alone, start a word) ->
                   romanization
  LEARNING_PATH  - ordered curriculum stages, e.g.
                   ["vow", "cons", "vow+cons", "cons+cons"]
"""

TITLE = "(ஃ) தமிழ் எழுத்து"

CONSONANTS = {
    "க": "ka",
    "ங": "nga",  # "~Na"
    "ச": "ca",
    "ஞ": "nya",  # "~na"
    "ட": "Ta",
    "ண": "Na",
    "த": "ta",
    "ந": "na",
    "ப": "pa",
    "ம": "ma",
    "ய": "ya",
    "ர": "ra",
    "ல": "la",
    "வ": "va",
    "ழ": "zha",
    "ள": "La",
    "ற": "ra",  # "Ra"
    "ன": "na",  # ^na
    "ஜ": "ja",
    "ஶ": "sha",  # "Sa"
    "ஷ": "sha",  # "S.a"
    "ஸ": "sa",
    "ஹ": "ha",
    "க்ஷ": "ksha",  # "kS.a"
    "ஸ்ரீ": "SrI",
    ":": ":",
}

VOWELS = {
    "்": "",
    "ா": "A",
    "ி": "i",
    "ீ": "I",
    "ு": "u",
    "ூ": "U",
    "ெ": "e",
    "ே": "E",
    "ை": "ai",
    "ொ": "o",
    "ோ": "O",
    "ௌ": "au",
}

VOWELS_SEP = {
    "அ": "a",
    "ஆ": "A",
    "இ": "i",
    "ஈ": "I",
    "உ": "u",
    "ஊ": "U",
    "எ": "e",
    "ஏ": "E",
    "ஐ": "ai",
    "ஒ": "o",
    "ஓ": "O",
    "ஔ": "au",
    "ஃ": "::",
}

LEARNING_PATH = ["vow", "cons", "vow+cons"]
