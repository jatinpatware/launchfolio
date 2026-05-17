document.getElementById('resume-file').addEventListener('change', (e) => {
  const label = document.getElementById('file-name');
  if (e.target.files.length) {
    label.textContent = e.target.files[0].name;
    label.classList.add('selected');
  }
});

function toggleAI(enabled) {
  document.getElementById('ai-fields').classList.toggle('hidden', !enabled);
  document.getElementById('ai-label').textContent = enabled ? 'AI parsing enabled' : 'Use AI parsing';
}

async function generate() {
  const btn = document.getElementById('generate-btn');
  btn.textContent = 'Generating…';
  btn.disabled = true;

  const formData = new FormData();

  const resumeFile = document.getElementById('resume-file').files[0];
  if (resumeFile) formData.append('resume', resumeFile);

  formData.append('enrichment', document.getElementById('enrichment').value);

  ['name', 'title', 'email', 'location', 'linkedin', 'github', 'tagline1', 'tagline2', 'summary'].forEach(id => {
    formData.append(id, document.getElementById(id).value);
  });
  formData.append('hero_badges', document.getElementById('hero-badges').value);

  // AI fields — only sent if toggle is on
  if (document.getElementById('ai-enabled').checked) {
    formData.append('ai_provider', document.getElementById('ai-provider').value);
    formData.append('ai_model',    document.getElementById('ai-model').value);
    formData.append('ai_api_key',  document.getElementById('ai-api-key').value);
  }

  try {
    const res = await fetch('/api/generate', { method: 'POST', body: formData });
    if (!res.ok) throw new Error(await res.text());

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const link = document.getElementById('download-link');
    link.href = url;
    document.getElementById('output').classList.remove('hidden');
    document.getElementById('output').scrollIntoView({ behavior: 'smooth' });
  } catch (err) {
    alert('Generation failed: ' + err.message + '\n\nMake sure the backend is running:\n  python backend/generate.py --serve');
  } finally {
    btn.textContent = 'Generate Portfolio →';
    btn.disabled = false;
  }
}
