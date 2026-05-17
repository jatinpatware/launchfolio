// Generates README.md from data.js — runs via GitHub Actions on push to main
const fs = require('fs');
const path = require('path');

// Load resumeData by evaluating data.js (avoids module boilerplate in data.js)
const dataPath = path.join(__dirname, '..', 'data.js');
eval(fs.readFileSync(dataPath, 'utf8'));
const d = resumeData;

const lines = [];

lines.push(`# ${d.name} — ${d.title}`);
lines.push('');
lines.push(`> ${d.tagline1} ${d.tagline2}`);
lines.push('');
lines.push(`**${d.sub}**`);
lines.push('');
lines.push(`📍 ${d.location} · [LinkedIn](${d.linkedin}) · [GitHub](${d.github}) · [Portfolio](${d.portfolio}) · [Email](mailto:${d.email})`);
lines.push('');

// Summary
lines.push('## Summary');
lines.push('');
lines.push(d.summary.replace(/\n\s+/g, ' ').trim());
lines.push('');

// Focus
lines.push('## What I Focus On');
lines.push('');
d.focus.forEach(f => lines.push(`- ${f}`));
lines.push('');

// Skills
lines.push('## Technical Skills');
lines.push('');
lines.push('| Category | Skills |');
lines.push('|----------|--------|');
d.skills.forEach(sg => {
  lines.push(`| **${sg.category}** | ${sg.items.join(' · ')} |`);
});
lines.push('');

// Experience
lines.push('## Experience');
lines.push('');
d.experience.forEach(exp => {
  const companyLabel = exp.companyDesc ? `${exp.company} — ${exp.companyDesc}` : exp.company;
  lines.push(`### ${companyLabel}`);
  lines.push('');
  exp.roles.forEach(role => {
    lines.push(`**${role.title}** · ${role.period}`);
    lines.push('');
    lines.push(`*Stack: ${role.stack}*`);
    lines.push('');
    role.bullets.forEach(b => lines.push(`- ${b.replace(/<strong>(.*?)<\/strong>/g, '**$1**')}`));
    lines.push('');
  });
});

// Projects
lines.push('## Projects');
lines.push('');
d.projects.forEach(p => {
  const statusLabel = p.status === 'coming-soon' ? ' *(coming soon)*' : '';
  const link = p.github ? ` · [GitHub](${p.github})` : '';
  lines.push(`### ${p.name}${statusLabel}${link}`);
  lines.push('');
  lines.push(p.desc);
  lines.push('');
  lines.push(`**Stack:** ${p.stack.join(' · ')}`);
  lines.push('');
});

// Education
lines.push('## Education');
lines.push('');
d.education.forEach(e => {
  lines.push(`### ${e.degree}`);
  lines.push(`${e.school} · CGPA ${e.cgpa} · ${e.period}`);
  if (e.notes && e.notes.length) {
    lines.push('');
    e.notes.forEach(n => lines.push(`- ${n}`));
  }
  lines.push('');
});

// Certifications
lines.push('## Certifications');
lines.push('');
d.certifications.forEach(c => {
  const entry = c.link ? `[${c.name}](${c.link})` : c.name;
  lines.push(`- ${c.icon} ${entry}${c.featured ? ' ⭐' : ''}`);
});
lines.push('');

// Footer
lines.push('---');
lines.push('');
lines.push(`*Generated from [data.js](data.js) — single source of truth for portfolio, resume, and README.*`);

const readme = lines.join('\n');
fs.writeFileSync(path.join(__dirname, '..', 'README.md'), readme);
fs.writeFileSync(path.join(__dirname, '..', 'resume', 'README.md'), readme);
console.log('README.md and resume/README.md generated successfully.');
