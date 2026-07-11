/* ═══════════════════════════════════════════════
   SecureVault – Main JavaScript
   ═══════════════════════════════════════════════ */

// ── Custom Cursor ─────────────────────────────────────────────
(function initCursor() {
  const dot  = document.getElementById('cursorDot');
  const ring = document.getElementById('cursorRing');
  if (!dot || !ring) return;

  let mouseX = -100, mouseY = -100;
  let ringX  = -100, ringY  = -100;
  let rafId;

  // Move dot instantly, ring follows with lerp
  document.addEventListener('mousemove', e => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.left = mouseX + 'px';
    dot.style.top  = mouseY + 'px';
  });

  // Smooth ring follow
  function animateRing() {
    ringX += (mouseX - ringX) * 0.14;
    ringY += (mouseY - ringY) * 0.14;
    ring.style.left = ringX + 'px';
    ring.style.top  = ringY + 'px';
    rafId = requestAnimationFrame(animateRing);
  }
  animateRing();

  // Hover state — buttons, links, interactive elements
  const hoverTargets = 'a, button, [role="button"], .action-btn, .quick-action-btn, .sidebar-link, .nav-link, .theme-toggle, .hamburger, .modal-close, .toggle-pw, .upload-area, label, select, .btn';
  document.addEventListener('mouseover', e => {
    if (e.target.closest(hoverTargets)) {
      document.body.classList.add('cursor-hover');
    }
  });
  document.addEventListener('mouseout', e => {
    if (e.target.closest(hoverTargets)) {
      document.body.classList.remove('cursor-hover');
    }
  });

  // Text input state
  const textTargets = 'input[type="text"], input[type="email"], input[type="password"], textarea, [contenteditable]';
  document.addEventListener('mouseover', e => {
    if (e.target.closest(textTargets)) {
      document.body.classList.add('cursor-text');
      document.body.classList.remove('cursor-hover');
    }
  });
  document.addEventListener('mouseout', e => {
    if (e.target.closest(textTargets)) {
      document.body.classList.remove('cursor-text');
    }
  });

  // Click ripple state
  document.addEventListener('mousedown', () => {
    document.body.classList.add('cursor-click');
  });
  document.addEventListener('mouseup', () => {
    document.body.classList.remove('cursor-click');
  });

  // Hide when mouse leaves window
  document.addEventListener('mouseleave', () => {
    dot.style.opacity  = '0';
    ring.style.opacity = '0';
  });
  document.addEventListener('mouseenter', () => {
    dot.style.opacity  = '1';
    ring.style.opacity = '1';
  });
})();

// ── Dark / Light Theme ────────────────────────────────────────
function toggleTheme() {
  const html  = document.documentElement;
  const curr  = html.getAttribute('data-theme');
  const next  = curr === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('sv-theme', next);
  document.querySelector('.theme-icon').textContent = next === 'dark' ? '☀️' : '🌙';
}

(function applyTheme() {
  const saved = localStorage.getItem('sv-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  document.addEventListener('DOMContentLoaded', () => {
    const icon = document.querySelector('.theme-icon');
    if (icon) icon.textContent = saved === 'dark' ? '☀️' : '🌙';
  });
})();

// ── Sidebar Toggle ────────────────────────────────────────────
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (!sidebar) return;
  sidebar.classList.toggle('open');
  overlay.classList.toggle('open');
  document.body.style.overflow = sidebar.classList.contains('open') ? 'hidden' : '';
}

// ── Password Toggle ───────────────────────────────────────────
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.type = input.type === 'password' ? 'text' : 'password';
}

// ── Password Strength Meter ───────────────────────────────────
function checkPasswordStrength(password) {
  let score = 0;
  if (password.length >= 8)  score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  return score;
}

function updateStrengthMeter(inputId, fillId, labelId) {
  const input = document.getElementById(inputId);
  const fill  = document.getElementById(fillId);
  const label = document.getElementById(labelId);
  if (!input || !fill || !label) return;

  input.addEventListener('input', () => {
    const score = checkPasswordStrength(input.value);
    const pct   = (score / 5) * 100;
    const labels = ['', 'Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
    const colors = ['', '#ef5350', '#ff9800', '#fdd835', '#66bb6a', '#2e7d32'];

    fill.style.width      = pct + '%';
    fill.style.background = colors[score] || '#e0e0e0';
    label.textContent     = input.value ? labels[score] || '' : '';
    label.style.color     = colors[score] || 'var(--muted)';
  });
}

// ── File Upload Preview & Drag-Drop ──────────────────────────
function showFileName(input) {
  const label = document.getElementById('selectedFile');
  const btn   = document.getElementById('uploadBtn');
  const area  = document.getElementById('uploadArea');
  if (!input.files || !input.files[0]) return;

  const name = input.files[0].name;
  const size = (input.files[0].size / 1024).toFixed(1);
  if (label) label.textContent = `✅ ${name} (${size} KB)`;
  if (btn)   btn.disabled = false;
  if (area)  { area.style.borderColor = '#1565c0'; area.style.background = 'var(--primary-light)'; }
}

document.addEventListener('DOMContentLoaded', () => {
  const area = document.getElementById('uploadArea');
  if (area) {
    area.addEventListener('dragover', e => {
      e.preventDefault();
      area.style.borderColor = '#1565c0';
      area.style.background  = 'var(--primary-light)';
    });
    area.addEventListener('dragleave', () => {
      area.style.borderColor = '';
      area.style.background  = '';
    });
    area.addEventListener('drop', e => {
      e.preventDefault();
      const fi = document.getElementById('fileInput');
      if (fi && e.dataTransfer.files.length) {
        // DataTransfer trick for drop
        const dt = new DataTransfer();
        dt.items.add(e.dataTransfer.files[0]);
        fi.files = dt.files;
        showFileName(fi);
      }
    });
  }

  // Password strength on register page
  updateStrengthMeter('password', 'pwStrengthFill', 'pwStrengthLabel');
  // Password strength on encrypt modal
  updateStrengthMeter('encryptPw', 'encPwFill', 'encPwLabel');

  // Auto-dismiss flash messages after 5s
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity .4s';
      alert.style.opacity    = '0';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });

  // Draw doughnut chart if on dashboard
  drawSecurityChart();
});

// ── Modal Controls ────────────────────────────────────────────
function openModal(modalId, filename) {
  const modal   = document.getElementById(modalId);
  if (!modal) return;
  const nameEl  = document.getElementById(modalId.replace('Modal', 'FileName'));
  const inputEl = document.getElementById(modalId.replace('Modal', 'FileInput'));
  if (nameEl)  nameEl.textContent = filename;
  if (inputEl) inputEl.value      = filename;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function openRenameModal(filename) {
  const modal = document.getElementById('renameModal');
  if (!modal) return;
  document.getElementById('renameOldName').textContent = filename;
  document.getElementById('renameOldInput').value      = filename;
  const newInput = document.getElementById('renameNewInput');
  // Pre-fill with current name (strip .enc if encrypted)
  newInput.value = filename;
  newInput.focus();
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function openKeyModal() {
  const modal = document.getElementById('keyModal');
  if (!modal) return;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeModal(event, modalId) {
  if (event.target.id === modalId) closeModalById(modalId);
}

function closeModalById(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.active').forEach(m => {
      m.classList.remove('active');
      document.body.style.overflow = '';
    });
  }
});

// ── File Search / Filter ──────────────────────────────────────
function filterFiles(query) {
  const rows = document.querySelectorAll('#fileTable .file-row');
  const q    = query.toLowerCase().trim();
  rows.forEach(row => {
    const name = row.querySelector('.file-name-text');
    if (name) row.style.display = name.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

// ── Copy Public Key ───────────────────────────────────────────
function copyPublicKey() {
  const content = document.getElementById('publicKeyContent');
  if (!content) return;
  navigator.clipboard.writeText(content.textContent).then(() => {
    const btn = document.getElementById('copyKeyBtn');
    if (btn) { btn.textContent = '✅ Copied!'; setTimeout(() => btn.textContent = '📋 Copy Key', 2000); }
  });
}

// ── Doughnut Chart (Canvas API — no external lib) ────────────
function drawSecurityChart() {
  const canvas = document.getElementById('securityChart');
  if (!canvas || typeof window.VAULT_DATA === 'undefined') return;

  const ctx  = canvas.getContext('2d');
  const data = window.VAULT_DATA;
  const total = data.encrypted + data.signed + data.plain;

  if (total === 0) {
    // Empty state — draw grey circle
    ctx.beginPath();
    ctx.arc(100, 100, 70, 0, Math.PI * 2);
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth   = 22;
    ctx.stroke();
    ctx.fillStyle   = getComputedStyle(document.documentElement).getPropertyValue('--text') || '#222';
    ctx.font        = 'bold 13px Inter, sans-serif';
    ctx.textAlign   = 'center';
    ctx.fillText('No files', 100, 96);
    ctx.fillText('yet', 100, 114);
    return;
  }

  const slices = [
    { value: data.encrypted, color: '#1565c0' },
    { value: data.signed,    color: '#6a1b9a' },
    { value: data.plain,     color: '#e0e0e0' },
  ].filter(s => s.value > 0);

  let startAngle = -Math.PI / 2;
  const cx = 100, cy = 100, r = 70, thickness = 22;

  slices.forEach(slice => {
    const angle = (slice.value / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.arc(cx, cy, r, startAngle, startAngle + angle);
    ctx.strokeStyle = slice.color;
    ctx.lineWidth   = thickness;
    ctx.stroke();
    startAngle += angle;
  });

  // Centre text
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  ctx.fillStyle = isDark ? '#e8edf4' : '#1a1a2e';
  ctx.font      = 'bold 22px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(total, cx, cy + 4);
  ctx.font      = '12px Inter, sans-serif';
  ctx.fillStyle = '#607d8b';
  ctx.fillText('files', cx, cy + 20);
}

// ── Share Modal Controls ──────────────────────────────────────

function openShareModal(filename) {
  const modal = document.getElementById('shareModal');
  if (!modal) return;
  document.getElementById('shareFileName').textContent = filename;
  document.getElementById('shareFileInput').value      = filename;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function openShareCodeModal(filename, token, downloads, maxDownloads) {
  const modal = document.getElementById('shareCodeModal');
  if (!modal) return;

  document.getElementById('scFileName').textContent  = filename;
  document.getElementById('scCode').textContent      = token;
  document.getElementById('scDownloads').textContent = downloads;
  document.getElementById('scMax').textContent       = maxDownloads;

  // Build share link
  const shareUrl = `${window.location.origin}/share?code=${token}`;
  document.getElementById('scLink').textContent = shareUrl;

  // Set revoke form action
  document.getElementById('revokeForm').action = `/share/revoke/${token}`;

  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function copyShareCode() {
  const code = document.getElementById('scCode').textContent;
  navigator.clipboard.writeText(code).then(() => {
    const btn = document.getElementById('copyCodeBtn');
    btn.textContent = '✅ Copied!';
    setTimeout(() => btn.textContent = '📋 Copy', 2000);
  });
}

function copyShareLink() {
  const link = document.getElementById('scLink').textContent;
  navigator.clipboard.writeText(link).then(() => {
    const btn = document.querySelector('.copy-link-btn');
    btn.textContent = '✅';
    setTimeout(() => btn.textContent = '📋', 2000);
  });
}
