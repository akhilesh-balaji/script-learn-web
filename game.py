"""
game.py  –  Stateful layer called by Flask routes.

Port notes vs. the original Julia:
  - submit() uses counter <= total (the original used < total, which never
    scored the last word; this port fixes that bug so all N words are checked).
  - Elapsed time for scoring is supplied by the client (client_elapsed_s) for
    accuracy across the network; server timestamps are the fallback.
  - Learning stage is per-visitor (flask.session) rather than a shared file.
  - Best scores ARE shared across all sessions, matching original points.log.
"""

import os
import time

import engine

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


# ── Score persistence ─────────────────────────────────────────────────────────

def _scores_path(script: str) -> str:
    return os.path.join(DATA_DIR, f"{script}_scores.log")


def get_best_score(script: str) -> float:
    path = _scores_path(script)
    if not os.path.isfile(path):
        return 0.0
    best = 0.0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            try:
                best = max(best, float(s))
            except ValueError:
                pass
    return best


def save_score(script: str, points: float) -> None:
    with open(_scores_path(script), "a", encoding="utf-8") as f:
        f.write(f"{points}\n")


# ── Factory ───────────────────────────────────────────────────────────────────

def new_default_game(script: str) -> dict:
    return {
        "script":            script,
        "mode":              "practice",   # 'practice' | 'learning'
        "difficulty":        0,            # 0-3
        "num_words_for_round": 3,
        "speak_mode":        False,
        "counter":           1,
        "points":            0.0,
        "current_word":      "",
        "correct":           "",
        "word_started_at":   None,
        "button_label":      "Verify",
    }


# ── Internal ──────────────────────────────────────────────────────────────────

def _deal_word(game: dict, learning_stage: dict, nospeak: bool = False) -> str:
    script = game["script"]
    if game["mode"] == "practice":
        word = engine.random_word_from_src(script, game["difficulty"])
    else:
        stage = learning_stage.get(script, 1.0)
        word = engine.next_learning_word(stage, script)
    game["current_word"]   = word
    game["correct"]        = engine.transliterate(word, script)
    game["word_started_at"] = time.time()
    game["speak_pending"]  = game.get("speak_mode", False) and not nospeak
    return word


# ── Public API ────────────────────────────────────────────────────────────────

def start_round(game: dict, learning_stage: dict, nospeak: bool = False) -> None:
    game["counter"]      = 1
    game["points"]       = 0.0
    game["button_label"] = "Verify"
    _deal_word(game, learning_stage, nospeak=nospeak)


def submit(
    game: dict,
    learning_stage: dict,
    answer: str = None,
    nospeak: bool = False,
    client_elapsed_s: float = None,
) -> dict:
    total   = game["num_words_for_round"]
    counter = game["counter"]
    result  = {"outcome": None, "revealed_answer": None,
               "final_score": None, "is_new_best": False}

    if counter <= total:
        if engine.normalize_answer(answer or "") == game["correct"]:
            if client_elapsed_s is not None:
                elapsed = max(0.0, min(float(client_elapsed_s), 300.0))
            else:
                elapsed = max(0.0, time.time() - (game["word_started_at"] or time.time()))

            game["points"]  += engine.score_for_answer(game["correct"], elapsed)
            game["counter"] += 1

            if game["counter"] > total:
                best_before          = get_best_score(game["script"])
                result["is_new_best"] = game["points"] > best_before
                if game["mode"] == "practice":
                    save_score(game["script"], game["points"])
                result["outcome"]     = "round_complete"
                result["final_score"] = round(game["points"], 2)
                game["button_label"]  = "New Round"
            else:
                result["outcome"] = "correct"
                _deal_word(game, learning_stage, nospeak=nospeak)
        else:
            game["points"]        -= 3.0
            result["outcome"]      = "incorrect"
            result["revealed_answer"] = game["correct"]

    elif counter == total + 1:           # "New Round" click
        game["counter"]      = 1
        game["points"]       = 0.0
        game["button_label"] = "Verify"
        result["outcome"]    = "reset"
        _deal_word(game, learning_stage, nospeak=nospeak)

    return result


def reset_round(game: dict, learning_stage: dict, nospeak: bool = True) -> dict:
    """Force restart (script switch, difficulty change, mode toggle)."""
    game["counter"]      = 1
    game["points"]       = 0.0
    game["button_label"] = "Verify"
    _deal_word(game, learning_stage, nospeak=nospeak)
    return {"outcome": "reset"}


def end_round_early(game: dict, learning_stage: dict) -> dict:
    best_before          = get_best_score(game["script"])
    is_new_best          = game["points"] > best_before
    if game["mode"] == "practice":
        save_score(game["script"], game["points"])
    final                = round(game["points"], 2)
    game["counter"]      = game["num_words_for_round"] + 1
    game["button_label"] = "New Round"
    return {"outcome": "round_complete", "final_score": final,
            "is_new_best": is_new_best, "revealed_answer": None}


def serialize(game: dict, learning_stage: dict, extra: dict = None) -> dict:
    lang  = engine.load_language(game["script"])
    stage = learning_stage.get(game["script"], 1.0)
    total = game["num_words_for_round"]
    payload = {
        "script":       game["script"],
        "title":        lang["title"],
        "mode":         game["mode"],
        "difficulty":   game["difficulty"],
        "num_words":    total,
        "speak_mode":   game.get("speak_mode", False),
        "word":         game["current_word"],
        "correct":      game["correct"],   # sent to client; harmless for a self-hosted tool
        "counter":      min(game["counter"], total),
        "total":        total,
        "round_finished": game["counter"] > total,
        "points":       round(game["points"], 2),
        "best_score":   round(get_best_score(game["script"]), 2),
        "button_label": game["button_label"],
        "learning_stage":       stage,
        "learning_stage_name":  engine.get_stage_name(stage, lang["learning_path"]),
        "learning_stage_label": engine.stage_label(stage, lang["learning_path"]),
        "learning_stage_max":   engine.max_stage(lang["learning_path"]),
        "speak_pending":        game.pop("speak_pending", False),
    }
    if extra:
        payload.update(extra)
    return payload
