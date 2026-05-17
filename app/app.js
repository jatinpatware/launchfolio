// ── File upload — label + auto-parse ─────────────────────────────────────────
document.getElementById('resume-file').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const label = document.getElementById('file-name');
  label.textContent = file.name;
  label.classList.add('selected');

  // Auto-parse: send to backend and fill empty form fields
  label.textContent = file.name + '  — parsing…';
  try {
    const fd = new FormData();
    fd.append('resume', file);
    const res = await fetch('/api/parse', { method: 'POST', body: fd });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();

    // Fill a field only if it is currently empty
    const fillIf = (id, val) => {
      const el = document.getElementById(id);
      if (el && !el.value.trim() && val) {
        el.value = val;
        el.dispatchEvent(new Event('input')); // trigger validation refresh
      }
    };

    fillIf('name',     data.name);
    fillIf('title',    data.title);
    fillIf('email',    data.email);
    fillIf('location', data.location);
    fillIf('linkedin', data.linkedin);
    fillIf('github',   data.github);
    fillIf('tagline1', data.tagline1);
    fillIf('tagline2', data.tagline2);
    fillIf('summary',  data.summary);
    fillIf('phone',      data.phone);
    fillIf('twitter',    data.twitter);
    fillIf('leetcode',   data.leetcode);
    fillIf('hackerrank', data.hackerrank);
    fillIf('portfolio',  data.portfolio);
    fillIf('credly',     data.credly);

    if (!document.getElementById('hero-badges').value.trim() && data.heroBadges?.length) {
      document.getElementById('hero-badges').value = data.heroBadges.join(', ');
    }

    label.textContent = file.name + '  ✓ fields auto-filled';
    refreshButton();
  } catch (err) {
    label.textContent = file.name + '  (could not parse — fill fields manually)';
  }
});

// ── Validation helpers ────────────────────────────────────────────────────────

const REQUIRED = ['name', 'title', 'tagline1'];
const AI_REQUIRED = ['ai-api-key'];

const MODELS = {
  anthropic: [
    { value: 'claude-sonnet-4-6',        label: 'Claude Sonnet 4.6 — recommended' },
    { value: 'claude-opus-4-7',           label: 'Claude Opus 4.7 — most capable' },
    { value: 'claude-haiku-4-5-20251001', label: 'Claude Haiku 4.5 — fastest' },
  ],
  openai: [
    { value: 'gpt-4o',       label: 'GPT-4o — most capable' },
    { value: 'gpt-4o-mini',  label: 'GPT-4o Mini — faster, cheaper' },
    { value: 'gpt-4.1',      label: 'GPT-4.1' },
    { value: 'gpt-4.1-mini', label: 'GPT-4.1 Mini — faster, cheaper' },
  ],
};

function populateModels(provider) {
  const sel = document.getElementById('ai-model');
  sel.innerHTML = '';
  (MODELS[provider] || []).forEach(m => {
    const opt = document.createElement('option');
    opt.value = m.value;
    opt.textContent = m.label;
    sel.appendChild(opt);
  });
}

function isAiOn() {
  return document.getElementById('ai-enabled').checked;
}

function fieldVal(id) {
  return document.getElementById(id).value.trim();
}

function setError(id, msg) {
  const el = document.getElementById(id + '-error');
  if (!el) return;
  el.textContent = msg;
  el.classList.toggle('hidden', !msg);
  document.getElementById(id).classList.toggle('field-error', !!msg);
}

function clearErrors() {
  [...REQUIRED, ...AI_REQUIRED].forEach(id => setError(id, ''));
}

function validate() {
  let ok = true;
  REQUIRED.forEach(id => {
    if (!fieldVal(id)) {
      setError(id, 'This field is required.');
      ok = false;
    } else {
      setError(id, '');
    }
  });
  if (isAiOn()) {
    AI_REQUIRED.forEach(id => {
      if (!fieldVal(id)) {
        setError(id, 'Required when AI parsing is enabled.');
        ok = false;
      } else {
        setError(id, '');
      }
    });
  }
  return ok;
}

function refreshButton() {
  const btn = document.getElementById('generate-btn');
  const nameOk     = !!fieldVal('name');
  const titleOk    = !!fieldVal('title');
  const tagline1Ok = !!fieldVal('tagline1');
  const aiOk       = !isAiOn() || (!!fieldVal('ai-model') && !!fieldVal('ai-api-key'));
  btn.disabled = !(nameOk && titleOk && tagline1Ok && aiOk);
}

// ── Wire up live validation ───────────────────────────────────────────────────

[...REQUIRED, ...AI_REQUIRED].forEach(id => {
  const el = document.getElementById(id);
  if (el) {
    el.addEventListener('input', () => {
      if (el.classList.contains('field-error')) setError(id, '');
      refreshButton();
    });
  }
});

function toggleAI(enabled) {
  document.getElementById('ai-fields').classList.toggle('hidden', !enabled);
  document.getElementById('ai-label').textContent = enabled ? 'AI parsing enabled' : 'Use AI parsing';
  if (!enabled) AI_REQUIRED.forEach(id => setError(id, ''));
  refreshButton();
}

document.getElementById('ai-provider').addEventListener('change', e => {
  populateModels(e.target.value);
});

// Populate models on initial load
populateModels('anthropic');

// Disable button on load — name and title are empty
refreshButton();

// ── Theme picker ──────────────────────────────────────────────────────────────
const THEME_LABELS = {
  ocean: 'Ocean (default)', midnight: 'Midnight', forest: 'Forest',
  ember: 'Ember', rose: 'Rose',
};

let selectedTheme = 'ocean';

document.querySelectorAll('.theme-swatch').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.theme-swatch').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedTheme = btn.dataset.theme;
    document.getElementById('theme-name').textContent = THEME_LABELS[selectedTheme] || selectedTheme;
  });
});

// ── Generate ──────────────────────────────────────────────────────────────────

async function generate() {
  clearErrors();
  if (!validate()) {
    // Scroll to first error
    const firstErr = document.querySelector('.field-error');
    if (firstErr) firstErr.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }

  const btn = document.getElementById('generate-btn');
  const originalText = btn.textContent;
  btn.textContent = 'Generating…';
  btn.disabled = true;

  // Hide any previous output while re-generating
  const outputEl = document.getElementById('output');
  outputEl.classList.add('hidden');

  const formData = new FormData();

  const resumeFile = document.getElementById('resume-file').files[0];
  if (resumeFile) formData.append('resume', resumeFile);

  formData.append('enrichment', document.getElementById('enrichment').value);

  ['name', 'title', 'email', 'location', 'linkedin', 'github', 'tagline1', 'tagline2', 'summary',
   'phone', 'twitter', 'leetcode', 'hackerrank', 'credly', 'portfolio'].forEach(id => {
    formData.append(id, document.getElementById(id).value);
  });
  formData.append('hero_badges', document.getElementById('hero-badges').value);
  formData.append('theme', selectedTheme);

  if (isAiOn()) {
    formData.append('ai_provider', document.getElementById('ai-provider').value);
    formData.append('ai_model',    document.getElementById('ai-model').value);
    formData.append('ai_api_key',  document.getElementById('ai-api-key').value);
  }

  try {
    const res = await fetch('/api/generate', { method: 'POST', body: formData });
    if (!res.ok) throw new Error(await res.text());

    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);

    const link = document.getElementById('download-link');
    link.href = url;

    outputEl.classList.remove('hidden');
    outputEl.scrollIntoView({ behavior: 'smooth' });
  } catch (err) {
    alert('Generation failed: ' + err.message + '\n\nMake sure the backend is running:\n  cd backend && python3 generate.py --serve');
  } finally {
    btn.textContent = originalText;
    refreshButton(); // re-evaluate rather than force-enable
  }
}
