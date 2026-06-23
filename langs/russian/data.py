"""
Language data for Russian (Русский).

Structure (required for every language in langs/<name>/data.py):
  TITLE          - display title shown in the header bar
  CONSONANTS     - base consonant glyph -> romanization
  VOWELS         - dependent vowel signs / matras (attach to a consonant) ->
                   romanization
  VOWELS_SEP     - independent vowel letters (stand alone, start a word) ->
                   romanization
  LEARNING_PATH  - ordered curriculum stages, e.g.
                   ["vow", "cons"]
"""

TITLE = "(Ѯ) ру́сский алфави́т"

CONSONANTS = {
    "б": "b",
    "Б": "b",
    "в": "v",
    "В": "v",
    "г": "g",
    "Г": "g",
    "д": "d",
    "Д": "d",
    "ж": "zh",
    "Ж": "zh",
    "з": "z",
    "З": "z",
    "й": "j",
    "Й": "j",
    "к": "k",
    "К": "k",
    "л": "l",
    "Л": "l",
    "м": "m",
    "М": "m",
    "н": "n",
    "Н": "n",
    "п": "p",
    "П": "p",
    "р": "r",
    "Р": "r",
    "с": "s",
    "С": "s",
    "т": "t",
    "Т": "t",
    "ф": "f",
    "Ф": "f",
    "х": "kh",
    "Х": "kh",
    "ц": "ts",
    "Ц": "ts",
    "ч": "ch",
    "Ч": "ch",
    "ш": "sh",
    "Ш": "sh",
    "щ": "shch",
    "Щ": "shch",
    "ъ": "",
    "Ъ": "",
    "ь": "",
    "Ь": "",
}

VOWELS = {}

VOWELS_SEP = {
    "а": "a",
    "А": "a",
    "е": "e",
    "Е": "e",
    "ё": "e",
    "Ё": "e",
    "и": "i",
    "И": "i",
    "о": "o",
    "О": "o",
    "у": "u",
    "У": "u",
    "ы": "y",
    "Ы": "y",
    "э": "e",
    "Э": "e",
    "ю": "yu",
    "Ю": "yu",
    "я": "ya",
    "Я": "ya",
}

LEARNING_PATH = ["vow", "cons"]
