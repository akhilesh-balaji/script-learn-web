"""
app.py  –  Flask entry point for skrpt learn.

Routes
------
GET  /                       → serve index.html
GET  /api/languages          → available language packs
POST /api/game/start         → initialise session, deal first word
GET  /api/game/state         → current game snapshot (page-reload recovery)
POST /api/game/submit        → evaluate one answer
POST /api/game/change_script → switch language, restart round
POST /api/game/toggle_mode   → flip practice ↔ learning
POST /api/game/set_difficulty→ set practice difficulty 0-3
POST /api/game/set_num_words → set words-per-round 1-50
POST /api/game/advance_stage → move learning stage ◀ / ▶
POST /api/game/end_round     → end current round early
"""

import os

from flask import Flask, jsonify, render_template, request, send_file, session

import engine
import game as gm

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-change-me-please")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# ── helpers ───────────────────────────────────────────────────────────────────


def _session_game():
    return session.get("game"), session.get("learning_stages", {})


def _save(game_dict, stages):
    session["game"] = game_dict
    session["learning_stages"] = stages


def _ok(game_dict, stages, extra=None):
    return jsonify(gm.serialize(game_dict, stages, extra))


def _err(msg, code=400):
    return jsonify({"error": msg}), code


def _require():
    gd, stages = _session_game()
    if not gd:
        return None, None, _err("no active game — POST /api/game/start first", 404)
    return gd, stages, None


# ── pages ─────────────────────────────────────────────────────────────────────


@app.route("/")
def index():
    return render_template("index.html")


# ── data ──────────────────────────────────────────────────────────────────────


@app.route("/api/languages")
def api_languages():
    return jsonify(engine.list_languages())


# ── game lifecycle ────────────────────────────────────────────────────────────


@app.route("/api/game/start", methods=["POST"])
def api_start():
    data = request.get_json(silent=True) or {}
    langs = engine.list_languages()
    if not langs:
        return _err("no language packs found in langs/", 500)

    script = data.get("script", langs[0]["id"])
    try:
        engine.load_language(script)
    except engine.UnknownScriptError:
        return _err(f"unknown script: {script!r}")

    gd = gm.new_default_game(script)
    if data.get("mode") in ("practice", "learning"):
        gd["mode"] = data["mode"]
    if "difficulty" in data:
        gd["difficulty"] = max(0, min(3, int(data["difficulty"])))
    if "num_words" in data:
        gd["num_words_for_round"] = max(1, min(50, int(data["num_words"])))
    if "speak_mode" in data:
        gd["speak_mode"] = bool(data["speak_mode"])

    stages = session.get("learning_stages", {})
    gm.start_round(gd, stages)
    _save(gd, stages)
    return _ok(gd, stages)


@app.route("/api/game/state")
def api_state():
    gd, stages, err = _require()
    if err:
        return err
    return _ok(gd, stages)


@app.route("/api/game/submit", methods=["POST"])
def api_submit():
    gd, stages, err = _require()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    answer = data.get("answer", "")
    elapsed_ms = data.get("elapsed_ms")
    client_s = float(elapsed_ms) / 1000.0 if elapsed_ms is not None else None

    result = gm.submit(gd, stages, answer=answer, client_elapsed_s=client_s)
    _save(gd, stages)
    return _ok(gd, stages, result)


@app.route("/api/game/change_script", methods=["POST"])
def api_change_script():
    gd, stages, err = _require()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    script = data.get("script")
    if not script:
        return _err("'script' required")
    try:
        engine.load_language(script)
    except engine.UnknownScriptError:
        return _err(f"unknown script: {script!r}")

    same = gd["script"] == script
    gd["script"] = script
    result = gm.reset_round(gd, stages, nospeak=same)
    _save(gd, stages)
    return _ok(gd, stages, result)


@app.route("/api/game/toggle_mode", methods=["POST"])
def api_toggle_mode():
    gd, stages, err = _require()
    if err:
        return err

    gd["mode"] = "learning" if gd["mode"] == "practice" else "practice"
    result = gm.reset_round(gd, stages, nospeak=True)
    _save(gd, stages)
    return _ok(gd, stages, result)


@app.route("/api/game/set_difficulty", methods=["POST"])
def api_set_difficulty():
    gd, stages, err = _require()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    gd["difficulty"] = max(0, min(3, int(data.get("difficulty", 0))))
    result = gm.reset_round(gd, stages, nospeak=True)
    _save(gd, stages)
    return _ok(gd, stages, result)


@app.route("/api/game/set_num_words", methods=["POST"])
def api_set_num_words():
    gd, stages, err = _require()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    gd["num_words_for_round"] = max(1, min(50, int(data.get("num_words", 3))))
    result = gm.reset_round(gd, stages, nospeak=True)
    _save(gd, stages)
    return _ok(gd, stages, result)


@app.route("/api/game/advance_stage", methods=["POST"])
def api_advance_stage():
    gd, stages, err = _require()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    direction = data.get("direction", "next")
    if direction not in ("next", "prev"):
        return _err("direction must be 'next' or 'prev'")

    lang = engine.load_language(gd["script"])
    current = stages.get(gd["script"], 1.0)
    stages[gd["script"]] = engine.advance_stage(
        current, lang["learning_path"], direction
    )
    result = gm.reset_round(gd, stages, nospeak=True)
    _save(gd, stages)
    return _ok(gd, stages, result)


@app.route("/api/game/end_round", methods=["POST"])
def api_end_round():
    gd, stages, err = _require()
    if err:
        return err

    result = gm.end_round_early(gd, stages)
    _save(gd, stages)
    return _ok(gd, stages, result)


# ── TTS ───────────────────────────────────────────────────────────────────────
_GTTS_LANGS = {
    "bengali": "bn",
    "devanagiri": "hi",
    "hindi": "hi",
    "tamil": "ta",
    "telugu": "te",
    "malayalam": "ml",
    "kannada": "kn",
    "gujarati": "gu",
    "punjabi": "pa",
}

_tts_cache: dict[tuple[str, str], bytes] = {}
_TTS_CACHE_MAX = 300


@app.route("/api/tts")
def api_tts():
    word = request.args.get("word", "").strip()
    script = request.args.get("script", "").strip()
    if not word or not script:
        return _err("word and script are required")

    lang = _GTTS_LANGS.get(script)
    if not lang:
        try:
            from gtts.lang import tts_langs

            matches = [
                code
                for code, name in tts_langs().items()
                if name.lower() == script.lower()
            ]
            lang = matches[0] if matches else None
        except Exception:
            pass
    if not lang:
        return _err(f"no TTS language for script '{script}'", 404)

    cache_key = (word, lang)
    if cache_key not in _tts_cache:
        try:
            import io

            from gtts import gTTS

            buf = io.BytesIO()
            gTTS(text=word, lang=lang).write_to_fp(buf)
            buf.seek(0)
            audio_bytes = buf.read()
        except Exception as exc:
            return _err(f"gTTS error: {exc}", 502)
        if len(_tts_cache) >= _TTS_CACHE_MAX:
            _tts_cache.pop(next(iter(_tts_cache)))
        _tts_cache[cache_key] = audio_bytes

    import io

    return send_file(
        io.BytesIO(_tts_cache[cache_key]),
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name="tts.mp3",
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
