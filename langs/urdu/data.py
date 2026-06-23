"""
Language data for Urdu (اردو).

Structure (required for every language in langs/<name>/data.py):
  TITLE          - display title shown in the header bar
  CONSONANTS     - base consonant glyph -> romanization (carries an inherent
                   vowel sound, e.g. "ک" -> "ka"; the trailing vowel letter is
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

TITLE = "اُردُو حُرُوفِ تَہَجِّی‌"  # [cite: 4]

CONSONANTS = {
    # [cite: 1]
    "ب": "b",
    "پ": "p",
    "ت": "t",
    "ط": "T",
    "ٹ": "T",
    "د": "d",
    "ڈ": "D",
    "ج": "j",
    "چ": "c",
    "ک": "k",
    "گ": "g",
    "ق": "q",
    "بھ": "bh",
    "پھ": "ph",
    "تھ": "th",
    "ٹھ": "Th",
    # [cite: 2]
    "دھ": "dh",
    "ڈھ": "Dh",
    "جھ": "jh",
    "چھ": "ch",
    "کھ": "kh",
    "گھ": "gh",
    "م": "m",
    "ن": "n",
    "ں": "~Ng",
    "ڻ": "N",
    "ف": "f",
    "س": "s",
    "ص": "S",
    "ز": "z",
    "ذ": "z",
    "ظ": "z",
    "ض": "z",  # [cite: 2, 3]
    # [cite: 3]
    "ث": "s",
    "ش": "S",
    "خ": "x",
    "غ": "g",
    "ح": "h",
    "ع": "'",
    "ہ": "h",
    "ر": "r",
    "ڑ": "r.",
    "ل": "l",
    "ی": "y",
    "و": "v",
    "ء": ":",
}

VOWELS = {
    # [cite: 3]
    "َ": "a",
    "ُ": "u",
    "ِ": "i",
    # [cite: 4]
    "ً": "an",
    "ٌ": "un",
    "ٍ": "in",
    "ٰ": "A",
}

VOWELS_SEP = {
    # [cite: 4]
    "ا": "A",
    "آ": "A",
    "و": "U",
    "ؤ": "u",
    "ی": "I",
    "ئ": "i",
    "ے": "e",
}

LEARNING_PATH = ["vow", "cons", "vow+cons", "cons+cons"]  # [cite: 4]
