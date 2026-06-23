"""
Language data for Bengali (বাংলা).

Structure (required for every language in langs/<name>/data.py):
  TITLE          - display title shown in the header bar
  CONSONANTS     - base consonant glyph -> romanization (carries an inherent
                   vowel sound, e.g. "ক" -> "ko"; the trailing vowel letter is
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

TITLE = "(ঋ) বাংলা লিপি"

CONSONANTS = {
    "ক": "ko",
    "খ": "kho",
    "গ": "go",
    "ঘ": "gho",
    "ঙ": "ngo",
    "চ": "co",
    "ছ": "cho",
    "জ": "jo",
    "ঝ": "jho",
    "ঞ": "nyo",
    "ট": "To",
    "ঠ": "Tho",
    "ড": "Do",
    "ঢ": "Dho",
    "ণ": "No",
    "ত": "to",
    "ৎ": "t",
    "থ": "tho",
    "দ": "do",
    "ধ": "dho",
    "ন": "no",
    "প": "po",
    "ফ": "pho",
    "ব": "bo",
    "ভ": "bho",
    "ম": "mo",
    "য": "yo",
    "য়": "Yo",
    "র": "ro",
    "ল": "lo",
    "ৱ": "vo",
    "শ": "sho",
    "ষ": "sho",
    "স": "so",
    "হ": "ho",
}

VOWELS = {
    "া": "A",
    "ি": "i",
    "ী": "I",
    "ু": "u",
    "ূ": "U",
    "ে": "E",
    "ৈ": "ai",
    "ো": "O",
    "ৌ": "au",
    "ৃ": "r",
    "ৄ": "R",
    "ৢ": "l",
    "ৣ": "L",
    "ং": "m.",
    "ঃ": ":",
    "্": "",
    "ँ": "m.",
    "ঁ": "m.",
}

VOWELS_SEP = {
    "অ": "o",
    "আ": "A",
    "ই": "i",
    "ঈ": "I",
    "উ": "u",
    "ঊ": "U",
    "এ": "E",
    "ঐ": "ai",
    "ও": "O",
    "ঔ": "au",
    "ঋ": "r",
    "ৠ": "R",
    "ঌ": "l",
    "ৡ": "L",
    "অঁ": "om.",
    "অং": "om.",
    "অঃ": "o:",
}

LEARNING_PATH = ["vow", "cons", "vow+cons", "cons+cons"]
