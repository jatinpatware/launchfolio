// LaunchFolio — frontend handler
// Sends resume + form data to backend, receives ZIP blob for download

const form = document.getElementById('upload-form');
const fileInput = document.getElementById('resume-file');
const fileNameLabel = document.getElementById('file-name');
const generateBtn = document.getElementById('generate-btn');
const outputSection = document.getElementById('output');
const downloadLink = document.getElementById('download-link');

fileInput.addEventListener('change', () => {
  if (fileInput.files.length) {
    fileNameLabel.textContent = fileInput.files[0].name;
    fileNameLabel.classList.add('selected');
  }
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  generateBtn.textContent = 'Generating…';
  generateBtn.disabled = true;

  const formData = new FormData();
  formData.append('resume', fileInput.files[0]);
  formData.append('name',     document.getElementById('name').value);
  formData.append('title',    document.getElementById('title').value);
  formData.append('email',    document.getElementById('email').value);
  formData.append('location', document.getElementById('location').value);
  formData.append('linkedin', document.getElementById('linkedin').value);
  formData.append('github',   document.getElementById('github').value);

  try {
    const res = await fetch('/api/generate', { method: 'POST', body: formData });
    if (!res.ok) throw new Error(await res.text());

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    downloadLink.href = url;
    outputSection.classList.remove('hidden');
    outputSection.scrollIntoView({ behavior: 'smooth' });
  } catch (err) {
    alert('Generation failed: ' + err.message);
  } finally {
    generateBtn.textContent = 'Generate Portfolio →';
    generateBtn.disabled = false;
  }
});
