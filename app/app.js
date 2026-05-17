// ── Tab switching ─────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
  });
});

document.getElementById('resume-file').addEventListener('change', (e) => {
  const label = document.getElementById('file-name');
  if (e.target.files.length) {
    label.textContent = e.target.files[0].name;
    label.classList.add('selected');
  }
});

// ── Generate ──────────────────────────────────────────────────
async function generate() {
  const btn = document.getElementById('generate-btn');
  btn.textContent = 'Generating…';
  btn.disabled = true;

  const activeTab = document.querySelector('.tab.active').dataset.tab;
  const formData = new FormData();

  // Input method
  if (activeTab === 'upload') {
    const file = document.getElementById('resume-file').files[0];
    if (!file) { alert('Please choose a PDF resume.'); btn.textContent = 'Generate Portfolio →'; btn.disabled = false; return; }
    formData.append('resume', file);
  } else if (activeTab === 'paste') {
    const raw = document.getElementById('raw-content').value.trim();
    if (!raw) { alert('Please paste some content.'); btn.textContent = 'Generate Portfolio →'; btn.disabled = false; return; }
    formData.append('raw_content', raw);
  }
  // 'scratch' — form fields only, no file or raw content

  // Form fields (override / supplement parsed values)
  ['name', 'title', 'email', 'location', 'linkedin', 'github', 'tagline1', 'tagline2', 'summary'].forEach(id => {
    formData.append(id, document.getElementById(id).value);
  });
  formData.append('hero_badges', document.getElementById('hero-badges').value);

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
    alert('Generation failed: ' + err.message + '\n\nMake sure the backend server is running (python backend/generate.py --serve)');
  } finally {
    btn.textContent = 'Generate Portfolio →';
    btn.disabled = false;
  }
}
