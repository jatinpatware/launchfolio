// ── Render from data.js ──────────────────────────────────────

function render() {
  const d = resumeData;

  // Hero
  document.getElementById('hero-name').textContent = d.name;
  document.getElementById('hero-title').textContent = d.title;
  document.getElementById('hero-tagline1').textContent = d.tagline1;
  document.getElementById('hero-tagline2').textContent = d.tagline2;
  document.getElementById('hero-sub').textContent = d.sub;
  document.getElementById('footer-text').textContent = `${d.name} · ${d.title} · ${d.location}`;

  document.getElementById('hero-badges').innerHTML = d.heroBadges
    .map(b => `<span class="badge">${b}</span>`).join('');

  document.getElementById('hero-links').innerHTML = `
    <a href="#about" class="btn-primary">See My Work</a>
    <a href="resume/Jatin_Patware_Senior_Data_Engineer.pdf" target="_blank" class="btn-secondary">Download Resume</a>
  `;

  // About
  document.getElementById('about-text').innerHTML = `
    <p>I design data systems that hold up at scale — 8+ years of doing it across petabyte-scale pipelines, real-time Kafka streams, and AI/LLM integration into data workflows.</p>
    <p>At <strong>Fanatics</strong>, one of the world's largest licensed sports merchandise platforms, I own the Kafka Streams pipeline and canonical data layer for real-time order processing. Before that, <strong>Fractal Analytics</strong> and <strong>MAQ Software</strong>.</p>
    <p>I'm equally comfortable whiteboarding a data mesh architecture, reviewing an engineer's design, or digging into a pipeline bottleneck.</p>
  `;

  document.getElementById('focus-list').innerHTML = d.focus
    .map(f => `<li>${f}</li>`).join('');

  // Experience
  document.getElementById('timeline').innerHTML = d.experience.map(exp => {
    const rolesHTML = exp.roles.map((role, i) => `
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-card">
          <div class="card-header">
            <div>
              <p class="card-company">${role.company || exp.company}${i === 0 && exp.companyDesc ? ' — ' + exp.companyDesc : ''}</p>
              <h3 class="card-title">${role.title}</h3>
            </div>
            <span class="card-date">${role.period}</span>
          </div>
          <div class="card-stack">${role.stack}</div>
          <ul class="card-bullets">
            ${role.bullets.map(b => `<li>${b}</li>`).join('')}
          </ul>
        </div>
      </div>
    `).join('');
    return rolesHTML;
  }).join('');

  // Skills
  document.getElementById('skills-grid').innerHTML = d.skills.map(sg => `
    <div class="skill-group">
      <h3>${sg.category}</h3>
      <div class="skill-tags">
        ${sg.items.map(item => `<span>${item}</span>`).join('')}
      </div>
    </div>
  `).join('');

  // Projects — professional group, then academic/open-source group
  const renderCard = p => `
    <div class="project-card">
      <div class="project-header">
        <h3 class="project-name">${p.name}</h3>
        ${p.status === 'coming-soon'
          ? '<span class="project-status">Coming Soon</span>'
          : `<a href="${p.github}" target="_blank" class="project-link">GitHub →</a>`
        }
      </div>
      <p class="project-desc">${p.desc}</p>
      <div class="project-stack">
        ${p.stack.map(s => `<span>${s}</span>`).join('')}
      </div>
    </div>
  `;

  const professional = d.projects.filter(p => !p.academic);
  const academic = d.projects.filter(p => p.academic);

  document.getElementById('projects-grid').innerHTML =
    professional.map(renderCard).join('') +
    (academic.length ? `<div class="projects-divider"><span>Academic &amp; Open Source</span></div>` : '') +
    academic.map(renderCard).join('');

  // Education
  document.getElementById('edu-list').innerHTML = d.education.map(e => `
    <div class="edu-item">
      <div class="edu-icon">🎓</div>
      <div>
        <h4>${e.degree}</h4>
        <p class="edu-school">${e.school}</p>
        <p class="edu-meta">${e.period} · CGPA ${e.cgpa}</p>
        ${e.notes && e.notes.length ? `<p class="edu-note">${e.notes.join(' · ')}</p>` : ''}
      </div>
    </div>
  `).join('');

  // Certifications — single flat list
  document.getElementById('cert-list').innerHTML =
    d.certifications.map(c => `
      <div class="cert-item ${c.featured ? 'featured' : ''}">
        <span class="cert-icon">${c.icon}</span>
        ${c.link
          ? `<a href="${c.link}" target="_blank" class="cert-name">${c.name} ↗</a>`
          : `<span>${c.name}</span>`
        }
      </div>
    `).join('') +
    `<a href="${d.credly}" target="_blank" class="cert-credly-link">View all badges on Credly →</a>`;

  // Contact
  document.getElementById('contact-links').innerHTML = `
    <a href="mailto:${d.email}" class="contact-card">
      <span class="contact-icon">✉️</span><span>${d.email}</span>
    </a>
    <a href="${d.linkedin}" target="_blank" class="contact-card">
      <span class="contact-icon">💼</span><span>LinkedIn</span>
    </a>
    <a href="${d.github}" target="_blank" class="contact-card">
      <span class="contact-icon">🐙</span><span>GitHub</span>
    </a>
    <a href="https://leetcode.com/u/j1p1" target="_blank" class="contact-card">
      <span class="contact-icon">💡</span><span>LeetCode</span>
    </a>
    <a href="https://hackerrank.com/profile/jatin_mits" target="_blank" class="contact-card">
      <span class="contact-icon">⭐</span><span>HackerRank</span>
    </a>
  `;
}

render();

// ── Navbar scroll ─────────────────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.style.boxShadow = window.scrollY > 50 ? '0 4px 30px rgba(0,0,0,0.4)' : 'none';
});

// ── Active nav highlight ──────────────────────────────────────
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-links a');
window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(s => { if (window.scrollY >= s.offsetTop - 100) current = s.id; });
  navLinks.forEach(l => { l.style.color = l.getAttribute('href') === `#${current}` ? 'var(--teal)' : ''; });
});

// ── Fade in on scroll ────────────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

setTimeout(() => {
  document.querySelectorAll('.timeline-card, .skill-group, .cert-item, .contact-card, .project-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });
}, 100);
