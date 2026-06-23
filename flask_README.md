# skrpt learn — web

A browser-based script-learning tool, ported from the original Julia/Mousetrap desktop app.

---

## Quick start

```bash
# 1. Install the single dependency
pip install flask

# 2. Run (dev)
python app.py
# or: flask --app app run --debug

# 3. Open  http://localhost:5000
```

Set a real secret key before exposing publicly:

```bash
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex())')"
python app.py
```

---

## Project layout

```
.
├── app.py              Flask routes (thin HTTP layer only)
├── engine.py           Transliteration, word generation, scoring — pure functions
├── game.py             Per-session state machine (mirrors submit_transliteration())
├── requirements.txt
│
├── langs/
│   └── bengali/
│       ├── data.py     Script data (consonants, vowels, learning_path, title)
│       └── src.txt     Source text for practice-mode word sampling
│
├── data/               Shared best-score logs (auto-created)
│
├── templates/
│   └── index.html      Single-page shell (three screen divs)
│
└── static/
    ├── css/style.css
    └── js/app.js
```

---

## Adding a new language

1. **Create the folder:**
   ```
   langs/<name>/
   ├── __init__.py     (empty)
   ├── data.py
   └── src.txt
   ```

2. **Write `data.py`** — copy `langs/bengali/data.py` as a template. Required exports:
   - `TITLE` — native title string shown in the UI
   - `CONSONANTS` — `{glyph: "romanization_with_inherent_vowel"}`, e.g. `{"ক": "ko"}`
   - `VOWELS` — dependent vowel signs / matras (attach to consonant). Include the virama/halant with value `""` so consonant clusters work.
   - `VOWELS_SEP` — independent vowel letters (start a syllable on their own)
   - `LEARNING_PATH` — list of stage names; supported values: `"vow"`, `"cons"`, `"vow+cons"`, `"cons+cons"`

3. **Populate `src.txt`** — any prose or poetry in the script, one line per sentence. The practice mode samples random words from this file.

4. **Add a TTS code** (optional) — in `static/js/app.js`, add an entry to `SPEECH_LANGS`:
   ```js
   const SPEECH_LANGS = {
     bengali: 'bn-BD',
     // your_script: 'xx-XX',
   };
   ```

The language picker on the welcome screen and in-game dropdown populate automatically from whatever folders exist under `langs/`.

---

## Transliteration convention

`CONSONANTS` values carry an **inherent vowel** that gets **dropped** when a dependent vowel follows. For example, if `"ক": "ko"` and `"া": "A"` then `কা` → `k` + `A` = `kA` (the `o` is chopped). This matches the original Julia logic exactly.

The `VOWELS` dict should map every dependent vowel sign you want recognised, including the virama/halant (`্`, `্`, etc.) mapped to `""`.

---

## Scoring (practice mode)

Ported verbatim from the original:

```python
if elapsed < 0.75:
    points += 50
else:
    points += (len(correct_answer) / sqrt(elapsed)) * (1 - tanh(elapsed - 10))
```

Wrong answers deduct 3 points. The timer resets on each correct answer; the clock starts on first keystroke. Learning mode never saves scores.

---

## Differences from the desktop app

| Feature | Desktop (Julia) | Web |
|---|---|---|
| Learning progress | shared file on disk | per-browser session (cookie) |
| Best scores | shared file on disk | shared `data/<script>_scores.log` |
| Last word in round | shown but not scored (bug) | scored like all other words |
| TTS | gTTS + ffmpeg | Web Speech API (browser-native) |
| Theme | GNOME adwaita | CSS custom properties, toggleable |
