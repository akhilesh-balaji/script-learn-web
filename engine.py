"""
engine.py

Pure logic, ported from the original Julia utils.jl. No Flask, no session,
no file I/O for game state -- everything here is a stateless function of
(script name) and explicit arguments, which makes it easy to test and safe
to call from concurrent requests.

The only file I/O in this module is reading langs/<script>/{data.py,src.txt},
which are read-only content, not per-user state.
"""

import importlib
import math
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LANGS_DIR = os.path.join(BASE_DIR, "langs")

_lang_cache = {}


class UnknownScriptError(Exception):
    pass


def list_languages():
    """Return [{'id': 'bengali', 'title': '...'}, ...] for every langs/<id>/data.py found."""
    if not os.path.isdir(LANGS_DIR):
        return []
    out = []
    for name in sorted(os.listdir(LANGS_DIR)):
        folder = os.path.join(LANGS_DIR, name)
        if os.path.isfile(os.path.join(folder, "data.py")):
            lang = load_language(name)
            out.append({"id": name, "title": lang["title"]})
    return out


def load_language(script):
    """Import langs/<script>/data.py and cache its contents."""
    if script in _lang_cache:
        return _lang_cache[script]

    data_path = os.path.join(LANGS_DIR, script, "data.py")
    if not os.path.isfile(data_path):
        raise UnknownScriptError(script)

    mod = importlib.import_module(f"langs.{script}.data")
    lang = {
        "title": mod.TITLE,
        "consonants": mod.CONSONANTS,
        "vowels": mod.VOWELS,
        "vowels_sep": mod.VOWELS_SEP,
        "learning_path": mod.LEARNING_PATH,
    }
    _lang_cache[script] = lang
    return lang


def src_path(script):
    return os.path.join(LANGS_DIR, script, "src.txt")


# ---------------------------------------------------------------------------
# transliterate -- direct port of Julia's transliterate()
# ---------------------------------------------------------------------------
def transliterate(word, script):
    """
    Walk the word character by character. A consonant carries an inherent
    vowel sound (e.g. ক -> "ko"); if the *next* character is a dependent
    vowel sign (a matra, looked up in VOWELS), that inherent vowel is
    dropped (we chop the last character of the romanization, e.g. "ko" ->
    "k") because the matra supplies its own vowel instead.

    Note: like the original, this matches single characters against VOWELS
    and VOWELS_SEP, so multi-character VOWELS_SEP entries (e.g. compound
    anusvara letters) are intentionally not matched here -- they only come
    into play as whole tokens in generate_random_word/next_learning_word.
    """
    lang = load_language(script)
    consonants, vowels, vowels_sep = lang["consonants"], lang["vowels"], lang["vowels_sep"]

    out = []
    n = len(word)
    for i, ch in enumerate(word):
        if ch in consonants:
            nxt = word[i + 1] if i + 1 < n else None
            if nxt is not None and nxt in vowels:
                out.append(consonants[ch][:-1])
            else:
                out.append(consonants[ch])
        elif ch in vowels:
            out.append(vowels[ch])
        elif ch in vowels_sep:
            out.append(vowels_sep[ch])
        else:
            out.append("-")
    return "".join(out)


# ---------------------------------------------------------------------------
# generate_random_word -- direct port of Julia's generate_random_word()
# ---------------------------------------------------------------------------
def generate_random_word(length, script):
    """
    Build a `length`-unit nonsense word: a letter is either an independent
    vowel or a consonant; a consonant can never be followed by another
    consonant without a vowel in between (prev_vowel bookkeeping), and a
    vowel only has a 1-in-5 chance of following a consonant (most randomly
    generated letters are consonants, occasionally broken up by a vowel).
    """
    lang = load_language(script)
    cons_keys = list(lang["consonants"].keys())
    vow_keys = list(lang["vowels"].keys())
    vowsep_keys = list(lang["vowels_sep"].keys())

    out = []
    prev_vowel = False
    for k in range(length):
        if k == 0:
            if vowsep_keys and random.choice([True, False]):
                out.append(random.choice(vowsep_keys))
                prev_vowel = True
            else:
                out.append(random.choice(cons_keys))
                prev_vowel = False
        else:
            if prev_vowel:
                out.append(random.choice(cons_keys))
                prev_vowel = False
            else:
                if vow_keys and random.choice([True, False, False, False, False]):
                    out.append(random.choice(vow_keys))
                    prev_vowel = True
                else:
                    out.append(random.choice(cons_keys))
                    prev_vowel = False
    return "".join(out).lower()


# ---------------------------------------------------------------------------
# random_word_from_src -- ported from Julia's random_word_from_src(), with
# one deliberate fix. The original's while-loop condition compared the
# *function* `get_difficulty` (not a call, `get_difficulty()`) to 2, which
# in Julia is always false -- so the "skip words 5+ characters long at
# difficulty 2" behaviour the UI/comments clearly intend never actually
# ran. This port implements the evident intent instead of the typo.
# ---------------------------------------------------------------------------
_BAD_WORDS = {"", "-", ",", " - ", ", "}
_STRIP_TABLE = str.maketrans("", "", ",.?'\" \n\t")


def random_word_from_src(script, difficulty):
    """
    difficulty 0 -> a single random letter (generate_random_word(1))
    difficulty 1 -> a two-letter nonsense word (generate_random_word(2))
    difficulty 2 -> a real word pulled from src.txt, capped under 5 chars
    difficulty 3 -> a real word pulled from src.txt, any length
    """
    if difficulty <= 0:
        return generate_random_word(1, script)
    if difficulty == 1:
        return generate_random_word(2, script)

    path = src_path(script)
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        lines = []

    if not lines:
        # No source text shipped for this language yet -- fall back rather
        # than crash the round.
        return generate_random_word(2, script)

    for _ in range(500):  # safety cap, src.txt is trusted but finite
        line = random.choice(lines)
        words = [w for w in line.split(" ") if w.strip()]
        if not words:
            continue
        candidate = random.choice(words).strip()
        cleaned = candidate.translate(_STRIP_TABLE)
        if cleaned in _BAD_WORDS:
            continue
        if difficulty == 2 and len(cleaned) >= 5:
            continue
        return cleaned

    return generate_random_word(2, script)


# ---------------------------------------------------------------------------
# Learning-mode curriculum -- ported from Julia's next_learning_word() plus
# the prev_level/next_level button handlers (advance_stage below).
#
# Stage numbers are floats. The integer part selects which LEARNING_PATH
# entry is active; the fractional part selects a sub-difficulty within that
# stage (more vowels/consonants unlocked as the fraction climbs):
#
#   1.0 - 1.5   "vow"        first half of the independent vowels
#   1.5 - 2.0   "vow"        all independent vowels
#   2.0 - 2.25  "cons"       first quarter of consonants
#   2.25 - 2.5  "cons"       first half of consonants
#   2.5 - 2.75  "cons"       first three-quarters of consonants
#   2.75 - 3.0  "cons"       all consonants
#   3.0 - 4.0   "vow+cons"   consonant + dependent vowel
#   4.0 - 5.0   "cons+cons"  consonant + virama + consonant (a cluster)
#
# Note: the original Julia indexed LEARNING_PATH with
# `floor(Int, current_stage - 0.1)`, which for the initial stage (1.0)
# evaluates to index 0 -- out of bounds for Julia's 1-indexed arrays. This
# port uses a straightforward `int(stage) - 1` instead.
# ---------------------------------------------------------------------------
def get_stage_name(current_stage, learning_path):
    idx = int(current_stage) - 1
    idx = max(0, min(idx, len(learning_path) - 1))
    return learning_path[idx]


def stage_label(current_stage, learning_path):
    """Human-readable label for the current learning stage, e.g. 'cons (3/4)'."""
    name = get_stage_name(current_stage, learning_path)
    names = {
        "vow": "vowels",
        "cons": "consonants",
        "vow+cons": "consonant + vowel",
        "cons+cons": "consonant clusters",
    }
    return names.get(name, name)


def max_stage(learning_path):
    return len(learning_path) + 0.5


def advance_stage(current_stage, learning_path, direction):
    """direction: 'next' or 'prev'. Returns the new stage value (a float)."""
    path_len = len(learning_path)
    top = max_stage(learning_path)

    if direction == "next":
        if current_stage >= top:
            return top
        if 1 <= current_stage < 2:
            return current_stage + 0.5
        if 2 <= current_stage < 3:
            return current_stage + 0.25
        if 3 <= current_stage <= path_len:
            return min(current_stage + 1, top)
        return current_stage
    else:
        if current_stage <= 1:
            return 1.0
        if 1 < current_stage <= 2:
            return current_stage - 0.5
        if 2 < current_stage <= 3:
            return current_stage - 0.25
        if 3 < current_stage <= top:
            return current_stage - 1
        return current_stage


def next_learning_word(current_stage, script):
    lang = load_language(script)
    learning_path = lang["learning_path"]
    stage_name = get_stage_name(current_stage, learning_path)

    consonants, vowels, vowels_sep = lang["consonants"], lang["vowels"], lang["vowels_sep"]
    cons_keys = list(consonants.keys())
    vow_keys = list(vowels.keys())
    vowsep_keys = list(vowels_sep.keys())

    if stage_name == "vow" and vowsep_keys:
        if current_stage <= 1.5:
            pool = vowsep_keys[: max(1, len(vowsep_keys) // 2)]
        else:
            pool = vowsep_keys
        return random.choice(pool)

    if stage_name == "cons" and cons_keys:
        if current_stage < 2.25:
            pool = cons_keys[: max(1, len(cons_keys) // 4)]
        elif current_stage < 2.5:
            pool = cons_keys[: max(1, len(cons_keys) // 2)]
        elif current_stage < 2.75:
            pool = cons_keys[: max(1, 3 * len(cons_keys) // 4)]
        else:
            pool = cons_keys
        return random.choice(pool)

    if stage_name == "vow+cons" and cons_keys and vow_keys:
        return random.choice(cons_keys) + random.choice(vow_keys)

    if stage_name == "cons+cons" and cons_keys:
        virama_candidates = [k for k, v in vowels.items() if v == ""]
        virama = virama_candidates[0] if virama_candidates else ""
        return random.choice(cons_keys) + virama + random.choice(cons_keys)

    # Fallback if a language is missing a piece of data for this stage.
    return random.choice(cons_keys) if cons_keys else "?"


# ---------------------------------------------------------------------------
# Scoring -- direct port of the points formula in submit_transliteration()
# ---------------------------------------------------------------------------
def score_for_answer(correct_text, elapsed_seconds):
    if elapsed_seconds < 0.75:
        return 50.0
    return (len(correct_text) / math.sqrt(elapsed_seconds)) * (1 - math.tanh(elapsed_seconds - 10))


def normalize_answer(text):
    """Same three substitutions the Julia app applies before comparing."""
    text = text.replace("aa", "A")
    text = text.replace("ee", "I")
    text = text.replace("oo", "U")
    return text
