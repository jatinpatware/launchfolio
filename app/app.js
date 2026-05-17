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
  google: [
    { value: 'gemini-2.5-pro',   label: 'Gemini 2.5 Pro — most capable' },
    { value: 'gemini-2.0-flash', label: 'Gemini 2.0 Flash — recommended' },
    { value: 'gemini-1.5-pro',   label: 'Gemini 1.5 Pro' },
    { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash — fast' },
  ],
  deepseek: [
    { value: 'deepseek-chat',     label: 'DeepSeek V3 — recommended' },
    { value: 'deepseek-reasoner', label: 'DeepSeek R1 — reasoning' },
  ],
  groq: [
    { value: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B — recommended' },
    { value: 'llama-3.1-8b-instant',    label: 'Llama 3.1 8B — fastest' },
    { value: 'mixtral-8x7b-32768',      label: 'Mixtral 8x7B' },
    { value: 'gemma2-9b-it',            label: 'Gemma 2 9B' },
  ],
  ollama: [
    { value: 'llama3.2',    label: 'Llama 3.2 (3B) — lightweight' },
    { value: 'llama3.1',    label: 'Llama 3.1 (8B)' },
    { value: 'llama3',      label: 'Llama 3 (8B)' },
    { value: 'mistral',     label: 'Mistral 7B' },
    { value: 'phi4',        label: 'Phi-4' },
    { value: 'qwen2.5',     label: 'Qwen 2.5' },
    { value: 'deepseek-r1', label: 'DeepSeek R1 (local)' },
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
  const el = document.getElementById(id);
  return el ? el.value.trim() : '';
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
  if (isAiOn() && apiKeyRequired()) {
    if (!fieldVal('ai-api-key')) {
      setError('ai-api-key', 'Required when AI parsing is enabled.');
      ok = false;
    } else {
      setError('ai-api-key', '');
    }
  }
  return ok;
}

function currentProvider() {
  const el = document.getElementById('ai-provider');
  return el ? el.value : 'anthropic';
}

function apiKeyRequired() {
  return isAiOn() && currentProvider() !== 'ollama';
}

function refreshButton() {
  try {
    const btn = document.getElementById('generate-btn');
    if (!btn) return;
    const nameOk     = !!fieldVal('name');
    const titleOk    = !!fieldVal('title');
    const tagline1Ok = !!fieldVal('tagline1');
    const keyOk      = !apiKeyRequired() || !!fieldVal('ai-api-key');
    btn.disabled = !(nameOk && titleOk && tagline1Ok && keyOk);
  } catch (e) {
    console.error('refreshButton:', e);
  }
}

// ── Wire up live validation ───────────────────────────────────────────────────

[...REQUIRED, ...AI_REQUIRED].forEach(id => {
  const el = document.getElementById(id);
  if (el) {
    ['input', 'change', 'keyup'].forEach(evt => {
      el.addEventListener(evt, () => {
        if (el.classList.contains('field-error')) setError(id, '');
        refreshButton();
      });
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
  const provider = e.target.value;
  populateModels(provider);
  const isOllama = provider === 'ollama';
  const keyField  = document.getElementById('ai-api-key');
  const keyLabel  = document.querySelector('label[for="ai-api-key"]');
  keyField.placeholder  = isOllama ? 'not required — Ollama runs locally' : 'sk-ant-…';
  keyField.style.opacity = isOllama ? '0.4' : '1';
  if (keyLabel) {
    keyLabel.querySelector('.required-star').style.display = isOllama ? 'none' : '';
  }
  if (isOllama) setError('ai-api-key', '');
  refreshButton();
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

// ── AI output panel helpers ───────────────────────────────────────────────────

function showAiPanel() {
  const panel = document.getElementById('ai-output-panel');
  panel.classList.remove('hidden');
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function setAiStatus(msg, isError) {
  const el = document.getElementById('ai-output-status');
  el.textContent = msg;
  el.className = 'ai-status' + (isError ? ' ai-status-error' : '');
}

function showAiJson(data) {
  const pre = document.getElementById('ai-output-json');
  pre.textContent = JSON.stringify(data, null, 2);
  document.getElementById('ai-output-actions').classList.remove('hidden');
}

function copyAiJson() {
  const text = document.getElementById('ai-output-json').textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById('ai-copy-btn');
    const orig = btn.textContent;
    btn.textContent = 'Copied!';
    setTimeout(() => { btn.textContent = orig; }, 1500);
  });
}

// ── Generate ──────────────────────────────────────────────────────────────────

async function generate() {
  clearErrors();
  if (!validate()) {
    const firstErr = document.querySelector('.field-error');
    if (firstErr) firstErr.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }

  const btn = document.getElementById('generate-btn');
  const originalText = btn.textContent;
  btn.disabled = true;

  const outputEl = document.getElementById('output');
  outputEl.classList.add('hidden');

  // Reset AI panel
  document.getElementById('ai-output-panel').classList.add('hidden');
  document.getElementById('ai-output-json').textContent = '';
  document.getElementById('ai-output-actions').classList.add('hidden');

  // Build shared form data
  const baseForm = new FormData();
  const resumeFile = document.getElementById('resume-file').files[0];
  if (resumeFile) baseForm.append('resume', resumeFile);
  baseForm.append('enrichment', document.getElementById('enrichment').value);
  ['name', 'title', 'email', 'location', 'linkedin', 'github', 'tagline1', 'tagline2', 'summary',
   'phone', 'twitter', 'leetcode', 'hackerrank', 'credly', 'portfolio'].forEach(id => {
    baseForm.append(id, document.getElementById(id).value);
  });
  baseForm.append('hero_badges', document.getElementById('hero-badges').value);
  baseForm.append('theme', selectedTheme);

  let preparsedJson = null;

  try {
    if (isAiOn()) {
      const provider = document.getElementById('ai-provider').value;
      const model    = document.getElementById('ai-model').value;
      const apiKey   = document.getElementById('ai-api-key').value;

      // Phase 1: call AI parse, show output
      showAiPanel();
      setAiStatus(`Contacting ${provider} (${model}) — this may take a moment...`);
      btn.textContent = 'Asking AI...';

      const aiForm = new FormData();
      if (resumeFile) aiForm.append('resume', resumeFile);
      aiForm.append('enrichment', document.getElementById('enrichment').value);
      aiForm.append('ai_provider', provider);
      aiForm.append('ai_model',    model);
      aiForm.append('ai_api_key',  apiKey);

      const aiRes = await fetch('/api/ai-parse', { method: 'POST', body: aiForm });
      if (!aiRes.ok) throw new Error('AI error: ' + await aiRes.text());
      preparsedJson = await aiRes.json();

      showAiJson(preparsedJson);
      setAiStatus('AI parsing complete. Building portfolio ZIP...');
      btn.textContent = 'Building ZIP...';
    } else {
      btn.textContent = 'Generating...';
    }

    // Phase 2: generate ZIP
    const genForm = new FormData();
    for (const [k, v] of baseForm.entries()) genForm.append(k, v);
    if (preparsedJson) {
      genForm.append('preparsed_json', JSON.stringify(preparsedJson));
    } else {
      // No AI — add provider fields so backend skips AI path
    }

    const res = await fetch('/api/generate', { method: 'POST', body: genForm });
    if (!res.ok) throw new Error(await res.text());

    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    document.getElementById('download-link').href = url;

    if (isAiOn()) setAiStatus('Done. Review the AI output above, then download your portfolio.');
    outputEl.classList.remove('hidden');
    outputEl.scrollIntoView({ behavior: 'smooth' });

  } catch (err) {
    if (isAiOn()) {
      setAiStatus(err.message, true);
    } else {
      alert('Generation failed: ' + err.message + '\n\nMake sure the backend is running:\n  cd backend && python3 generate.py --serve');
    }
  } finally {
    btn.textContent = originalText;
    refreshButton();
  }
}
