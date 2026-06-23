/**
 * skrpt learn — app.js
 *
 * Architecture:
 *   Api      — thin fetch wrapper
 *   Timer    — per-word stopwatch (client-side for accuracy)
 *   Screens  — show/hide the three screen divs
 *   Welcome  — language grid, start button
 *   Game     — drives the main game loop, mirrors server state
 *   Settings — wires up settings controls
 *   Tts      — Web Speech API wrapper
 */

'use strict';

/* ═══════════════════════════════════════════════════════════
   Tiny helpers
   ═══════════════════════════════════════════════════════════ */

const $ = id => document.getElementById(id);

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

const DIFF_LABELS = ['single chars', '2-char combos', 'short words', 'any word'];


// Strip the parenthetical prefix from a native title, e.g.
// "(ঋ) বাংলা লিপি"  →  "বাংলা লিপি"
function stripPrefix(title) {
  return title.replace(/^\([^)]+\)\s*/, '');
}

// Capitalise the first letter of a script id
function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }


/* ═══════════════════════════════════════════════════════════
   Api
   ═══════════════════════════════════════════════════════════ */

const Api = {
  async call(method, endpoint, body) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body !== undefined) opts.body = JSON.stringify(body);
    const res = await fetch(endpoint, opts);
    const json = await res.json();
    if (!res.ok) throw new Error(json.error || `HTTP ${res.status}`);
    return json;
  },
  get:  (ep)       => Api.call('GET',  ep),
  post: (ep, body) => Api.call('POST', ep, body ?? {}),
};


/* ═══════════════════════════════════════════════════════════
   Timer  —  per-word elapsed, drives the topbar display
   ═══════════════════════════════════════════════════════════ */

const Timer = {
  _start:    null,
  _interval: null,

  get elapsed() {
    return this._start === null ? 0 : (Date.now() - this._start) / 1000;
  },

  start() {
    this._start = Date.now();
    clearInterval(this._interval);
    this._interval = setInterval(() => {
      $('timer').textContent = this.elapsed.toFixed(3);
    }, 50);
    $('timer').classList.add('running');
  },

  reset() {
    this._start = null;
    clearInterval(this._interval);
    this._interval = null;
    $('timer').textContent = '0.000';
    $('timer').classList.remove('running');
  },

  stop() { clearInterval(this._interval); },
};


/* ═══════════════════════════════════════════════════════════
   Screens
   ═══════════════════════════════════════════════════════════ */

let _prevScreen = 'welcome';

function showScreen(name) {
  ['welcome', 'game', 'settings'].forEach(id => {
    $(`screen-${id}`).classList.toggle('active', id === name);
  });
}


/* ═══════════════════════════════════════════════════════════
   Tts  —  Web Speech API
   ═══════════════════════════════════════════════════════════ */

const Tts = {
  _enabled: false,
  _current: null,

  speak(word, script) {
    if (!this._enabled) return;
    if (this._current) {
      this._current.pause();
      this._current.src = '';
      this._current = null;
    }
    const url = `/api/tts?word=${encodeURIComponent(word)}&script=${encodeURIComponent(script)}`;
    const audio = new Audio(url);
    this._current = audio;
    audio.play().catch(err => {
      console.warn('TTS playback error:', err);
      Settings.showTtsError(err.message);
    });
    audio.addEventListener('ended', () => { this._current = null; });
  },

  set enabled(v) {
    this._enabled = !!v;
    localStorage.setItem('skrpt-speak', this._enabled ? '1' : '0');
    if (!v && this._current) {
      this._current.pause();
      this._current = null;
    }
  },
  get enabled() { return this._enabled; },
};


/* ═══════════════════════════════════════════════════════════
   Word animation helpers
   ═══════════════════════════════════════════════════════════ */

async function animateWordChange(newWord) {
  const el = $('script-word');

  // Exit
  el.classList.add('exiting');
  await sleep(140);
  el.classList.remove('exiting');

  // Swap content
  el.textContent = newWord;

  // Enter
  el.classList.add('entering');
  await sleep(200);
  el.classList.remove('entering');
}


/* ═══════════════════════════════════════════════════════════
   Welcome screen
   ═══════════════════════════════════════════════════════════ */

const Welcome = {
  _selected: null,
  _langs:    [],

  setLanguages(langs) {
    this._langs = langs;
    const grid = $('lang-grid');
    grid.innerHTML = '';

    langs.forEach(lang => {
      const btn = document.createElement('button');
      btn.className = 'lang-card';
      btn.dataset.script = lang.id;
      btn.setAttribute('role', 'option');
      btn.innerHTML = `
        <span class="lang-native">${stripPrefix(lang.title)}</span>
        <span class="lang-latin">${capitalize(lang.id)}</span>`;
      btn.addEventListener('click', () => this.selectScript(lang.id));
      grid.appendChild(btn);
    });

    // Auto-select if only one language
    if (langs.length === 1) this.selectScript(langs[0].id);

    // Populate the in-game language dropdown too
    const sel = $('lang-select');
    sel.innerHTML = '';
    langs.forEach(lang => {
      const opt = document.createElement('option');
      opt.value = lang.id;
      opt.textContent = capitalize(lang.id);
      sel.appendChild(opt);
    });
  },

  selectScript(id) {
    this._selected = id;
    document.querySelectorAll('.lang-card').forEach(el => {
      el.classList.toggle('selected', el.dataset.script === id);
    });
    const btn = $('btn-start');
    btn.disabled = false;
    btn.textContent = `Start :: ${capitalize(id)}`;
  },

  get selected() { return this._selected; },
};


/* ═══════════════════════════════════════════════════════════
   Game screen
   ═══════════════════════════════════════════════════════════ */

const Game = {
  data:           null,   // last server snapshot
  _timerStarted:  false,  // has the timer fired for the current word?

  // ── Apply a full server snapshot to the UI ──────────────────
  applyState(data) {
    this.data = data;

    // Progress / score
    $('progress').textContent = `${data.counter} / ${data.total}`;
    $('points').textContent   = `${data.points} pts`;

    // Mode
    const isLearning = data.mode === 'learning';
    $('mode-label').textContent = data.mode;
    $('mode-toggle').checked    = isLearning;
    $('stage-nav').classList.toggle('hidden', !isLearning);
    $('diff-control').classList.toggle('hidden', isLearning);

    // Stage / difficulty labels
    $('stage-label').textContent = data.learning_stage_label;
    $('diff-slider').value        = data.difficulty;
    $('diff-label').textContent   = DIFF_LABELS[data.difficulty] ?? '';

    // Language select
    $('lang-select').value = data.script;
  },

  // ── Switch to "round active" UI state ──────────────────────
  enterActiveState(word, animate = false) {
    // Show word element, hide result panel
    $('script-word').classList.remove('hidden');
    $('round-result').classList.add('hidden');

    // Answer area: remove "complete" class
    $('answer-area').classList.remove('complete');

    // Reset timer + input
    Timer.reset();
    this._timerStarted = false;
    $('answer-input').value = '';
    $('answer-input').disabled = false;
    $('feedback').textContent = '';
    $('feedback').className = 'feedback';

    // Show word (animated or instant)
    if (animate) {
      animateWordChange(word);
    } else {
      $('script-word').textContent = word;
    }

    $('btn-verify').textContent = 'Verify';
    $('answer-input').focus();
  },

  // ── Switch to "round complete" UI state ────────────────────
  enterCompleteState(data, result) {
    Timer.stop();
    $('timer').classList.remove('running');

    // Hide live word, show result panel
    $('script-word').classList.add('hidden');
    const rr = $('round-result');
    rr.classList.remove('hidden');

    const score = result.final_score ?? 0;
    $('result-score').textContent = `${score} pts`;

    const bestEl = $('result-best');
    if (data.mode === 'practice' && result.is_new_best) {
      bestEl.classList.remove('hidden');
    } else {
      bestEl.classList.add('hidden');
    }

    $('result-mode-note').textContent =
      data.mode === 'learning' ? 'learning — no score saved' : '';

    // Switch input area to "complete" layout
    $('answer-area').classList.add('complete');
    $('btn-verify').textContent = 'New Round';
    $('answer-input').disabled = true;
    $('feedback').textContent  = '';
    $('feedback').className    = 'feedback';
  },

  // ── Handle the server's outcome field ──────────────────────
  async handleOutcome(data, result) {
    switch (result.outcome) {

      case 'correct': {
        $('feedback').textContent = '✓';
        $('feedback').className   = 'feedback ok';
        // clear feedback briefly then animate new word in
        await sleep(400);
        $('feedback').textContent = '';
        $('feedback').className   = 'feedback';
        Timer.reset();
        this._timerStarted = false;
        $('answer-input').value = '';
        animateWordChange(data.word);
        $('progress').textContent = `${data.counter} / ${data.total}`;
        $('points').textContent   = `${data.points} pts`;
        Tts.speak(data.word, data.script);
        break;
      }

      case 'incorrect': {
        $('feedback').textContent = `× ${result.revealed_answer}`;
        $('feedback').className   = 'feedback err';
        $('answer-input').classList.add('shake');
        $('answer-input').addEventListener(
          'animationend',
          () => $('answer-input').classList.remove('shake'),
          { once: true }
        );
        $('points').textContent = `${data.points} pts`;
        $('answer-input').value = '';
        $('answer-input').focus();
        break;
      }

      case 'round_complete': {
        $('progress').textContent = `${data.total} / ${data.total}`;
        $('points').textContent   = `${data.points} pts`;
        this.enterCompleteState(data, result);
        break;
      }

      case 'reset': {
        // "New Round" was clicked — start fresh
        this.applyState(data);
        this.enterActiveState(data.word, true);
        Tts.speak(data.word, data.script);
        break;
      }
    }
  },

  // ── Submit the current answer ───────────────────────────────
  async submit() {
    const input   = $('answer-input');
    const answer  = input.value.trim();
    const elapsed = Timer._start ? Timer.elapsed : null;

    let data;
    try {
      data = await Api.post('/api/game/submit', {
        answer,
        elapsed_ms: elapsed !== null ? Math.round(elapsed * 1000) : null,
      });
    } catch (e) {
      console.error('submit error:', e);
      return;
    }

    await this.handleOutcome(data, data);
  },

  // ── Start a new game for the given script ──────────────────
  async start(script, numWords) {
    let data;
    try {
      data = await Api.post('/api/game/start', {
        script,
        num_words: numWords,
      });
    } catch (e) {
      alert(`Could not start game: ${e.message}`);
      return;
    }
    this.applyState(data);
    this.enterActiveState(data.word, false);
    Tts.speak(data.word, data.script);
    showScreen('game');
  },

  initEventListeners() {
    // Verify / New Round button
    $('btn-verify').addEventListener('click', async () => {
      if ($('answer-area').classList.contains('complete')) {
        // "New Round" — call submit to advance past total+1 branch
        let data;
        try {
          data = await Api.post('/api/game/submit', { answer: '' });
        } catch (e) { console.error(e); return; }
        await this.handleOutcome(data, data);
      } else {
        await this.submit();
      }
    });

    // Enter key in input
    $('answer-input').addEventListener('keydown', e => {
      if (e.key === 'Enter') this.submit();
    });

    // Space auto-submits (matching original behaviour)
    $('answer-input').addEventListener('input', e => {
      const val = e.target.value;
      if (val.includes(' ')) {
        e.target.value = val.replaceAll(' ', '');
        this.submit();
        return;
      }
      // Start timer on first keystroke
      if (!this._timerStarted && val.length >= 1) {
        this._timerStarted = true;
        Timer.start();
      }
    });

    // Language selector dropdown (in-game)
    $('lang-select').addEventListener('change', async e => {
      const script = e.target.value;
      try {
        const data = await Api.post('/api/game/change_script', { script });
        this.applyState(data);
        this.enterActiveState(data.word, true);
      } catch (err) { console.error(err); }
    });

    // Mode toggle
    $('mode-toggle').addEventListener('change', async () => {
      try {
        const data = await Api.post('/api/game/toggle_mode');
        this.applyState(data);
        this.enterActiveState(data.word, true);
      } catch (e) { console.error(e); }
    });

    // Stage navigation (learning mode)
    $('btn-prev-stage').addEventListener('click', async () => {
      try {
        const data = await Api.post('/api/game/advance_stage', { direction: 'prev' });
        this.applyState(data);
        this.enterActiveState(data.word, true);
      } catch (e) { console.error(e); }
    });
    $('btn-next-stage').addEventListener('click', async () => {
      try {
        const data = await Api.post('/api/game/advance_stage', { direction: 'next' });
        this.applyState(data);
        this.enterActiveState(data.word, true);
      } catch (e) { console.error(e); }
    });

    // Difficulty slider
    let diffTimeout;
    $('diff-slider').addEventListener('input', e => {
      const val = parseInt(e.target.value, 10);
      $('diff-label').textContent = DIFF_LABELS[val] ?? '';
      clearTimeout(diffTimeout);
      diffTimeout = setTimeout(async () => {
        try {
          const data = await Api.post('/api/game/set_difficulty', { difficulty: val });
          this.applyState(data);
          this.enterActiveState(data.word, true);
        } catch (err) { console.error(err); }
      }, 300);
    });

    // End round early
    $('btn-end-round').addEventListener('click', async () => {
      try {
        const data = await Api.post('/api/game/end_round');
        this.applyState(data);
        this.enterCompleteState(data, data);
      } catch (e) { console.error(e); }
    });

    // Back to home
    $('btn-back-home').addEventListener('click', () => {
      Timer.reset();
      showScreen('welcome');
    });
  },
};


/* ═══════════════════════════════════════════════════════════
   Settings screen
   ═══════════════════════════════════════════════════════════ */

const Settings = {
  _fromScreen: 'welcome',   // which screen to return to

  open(from) {
    this._fromScreen = from;
    showScreen('settings');
  },

  initEventListeners() {
    // Back button
    $('btn-settings-back').addEventListener('click', () => {
      showScreen(this._fromScreen);
    });

    // Open settings from welcome screen
    $('btn-settings-open').addEventListener('click', () => this.open('welcome'));

    // Words per round
    $('num-words-input').addEventListener('change', async e => {
      const n = Math.max(1, Math.min(50, parseInt(e.target.value, 10) || 3));
      e.target.value = n;
      // Apply immediately if a game is running
      try {
        await Api.post('/api/game/set_num_words', { num_words: n });
      } catch (_) { /* no active game yet — fine */ }
    });

    // Dark mode toggle
    $('dark-toggle').addEventListener('change', e => {
      const dark = e.target.checked;
      document.documentElement.dataset.theme = dark ? 'dark' : 'light';
      localStorage.setItem('skrpt-dark', dark ? '1' : '0');
    });

    // Speak words toggle
    $('speak-toggle').addEventListener('change', e => {
      Tts.enabled = e.target.checked;
      localStorage.setItem('skrpt-speak', e.target.checked ? '1' : '0');
      // Sync to server if game is running
      const script = Game.data?.script;
      if (script && e.target.checked && Game.data?.word) {
        Tts.speak(Game.data.word, script);
      }
    });
  },

  loadPreferences() {
    // Dark mode (default on)
    const dark = localStorage.getItem('skrpt-dark') !== '0';
    $('dark-toggle').checked = dark;
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';

    // Speak mode (default off)
    const speak = localStorage.getItem('skrpt-speak') === '1';
    $('speak-toggle').checked = speak;
    Tts.enabled = speak;
  },
};


/* ═══════════════════════════════════════════════════════════
   Boot
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', async () => {
  Settings.loadPreferences();
  Settings.initEventListeners();
  Game.initEventListeners();

  // Load language list
  let langs;
  try {
    langs = await Api.get('/api/languages');
  } catch (e) {
    $('lang-grid').textContent = 'Error loading languages — is the server running?';
    return;
  }
  Welcome.setLanguages(langs);

  // Start button
  $('btn-start').addEventListener('click', () => {
    const script   = Welcome.selected;
    const numWords = parseInt($('num-words-input').value, 10) || 3;
    if (script) Game.start(script, numWords);
  });

  // Attempt to recover an existing session (page reload)
  try {
    const data = await Api.get('/api/game/state');
    if (data.word) {
      Game.applyState(data);
      if (data.round_finished) {
        $('script-word').classList.add('hidden');
        $('round-result').classList.remove('hidden');
        $('result-score').textContent = `${data.points} pts`;
        $('answer-area').classList.add('complete');
        $('btn-verify').textContent = 'New Round';
      } else {
        Game.enterActiveState(data.word, false);
      }
      showScreen('game');
    }
  } catch (_) {
    /* No active session — stay on welcome screen */
  }
});
