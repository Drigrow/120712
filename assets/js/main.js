/* ═══════════════════════════════════════════════
   洛天依 · Luo Tianyi — main.js v3
   Dynamic Local Music Player + ASCII UI
   ═══════════════════════════════════════════════ */

/* ─────────── Loader ─────────── */
const loader = document.getElementById('loader');
const loaderBar = document.getElementById('loaderBar');

let pct = 0;
const barInterval = setInterval(() => {
  pct += Math.random() * 18;
  if (pct > 100) pct = 100;
  loaderBar.style.width = pct + '%';
  if (pct >= 100) clearInterval(barInterval);
}, 100);

const hideLoader = () => loader.classList.add('hide');
window.addEventListener('load', () => setTimeout(hideLoader, 1400));
setTimeout(hideLoader, 3500);

/* ─────────── Language toggle ─────────── */
const html = document.documentElement;
const langBtn = document.getElementById('langToggle');
let currentLang = 'zh';

try {
  const saved = localStorage.getItem('lt-lang');
  if (saved === 'en') {
    currentLang = 'en';
    html.setAttribute('data-lang', 'en');
    html.setAttribute('lang', 'en');
  }
} catch (e) { }

langBtn.addEventListener('click', () => {
  currentLang = currentLang === 'zh' ? 'en' : 'zh';
  html.setAttribute('data-lang', currentLang);
  html.setAttribute('lang', currentLang === 'zh' ? 'zh-Hans' : 'en');
  try { localStorage.setItem('lt-lang', currentLang); } catch (e) { }
});

/* ─────────── Mobile menu ─────────── */
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');

hamburger.addEventListener('click', () => {
  const open = mobileMenu.classList.toggle('open');
  hamburger.classList.toggle('open', open);
  hamburger.setAttribute('aria-expanded', String(open));
});
function closeMobMenu() {
  mobileMenu.classList.remove('open');
  hamburger.classList.remove('open');
  hamburger.setAttribute('aria-expanded', 'false');
}
window.closeMobMenu = closeMobMenu;
document.addEventListener('click', e => {
  if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) closeMobMenu();
});

/* ─────────── Navbar scroll ─────────── */
const navbar = document.getElementById('navbar');
const navLinks = document.querySelectorAll('.nav-link');
const sections = document.querySelectorAll('section[id]');

function onScroll() {
  navbar.classList.toggle('scrolled', window.scrollY > 40);
  let current = '';
  sections.forEach(sec => { if (window.scrollY >= sec.offsetTop - 80) current = sec.id; });
  navLinks.forEach(link => {
    link.classList.toggle('active', link.getAttribute('href').slice(1) === current);
  });
}
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

/* ─────────── Smooth scroll ─────────── */
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const t = document.querySelector(link.getAttribute('href'));
    if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
});

/* ─────────── Reveal on scroll ─────────── */
const revealObs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); revealObs.unobserve(e.target); } });
}, { threshold: 0.10 });
document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));

/* ─────────── Wave anim text doubling ─────────── */
document.querySelectorAll('.wave-anim').forEach(el => {
  el.textContent = el.textContent + ' ' + el.textContent;
});

/* ─────────── HUD typing effect ─────────── */
const hud = document.querySelector('.hud-ascii');
if (hud) {
  const original = hud.textContent;
  let displayed = '', i = 0;
  hud.textContent = '';
  setTimeout(() => {
    const type = () => {
      if (i < original.length) {
        displayed += original[i++];
        hud.textContent = displayed + (i < original.length ? '▌' : '');
        setTimeout(type, 16);
      }
    };
    type();
  }, 1600);
}

/* ─────────── Hero 3D tilt ─────────── */
let tilting = false;
window.addEventListener('mousemove', e => {
  if (tilting) return; tilting = true;
  requestAnimationFrame(() => {
    const panel = document.querySelector('.char-img-wrap');
    if (panel) {
      const cx = (e.clientX / window.innerWidth - 0.5);
      const cy = (e.clientY / window.innerHeight - 0.5);
      panel.style.transform = `perspective(600px) rotateY(${cx * 6}deg) rotateX(${-cy * 4}deg)`;
    }
    tilting = false;
  });
});
document.addEventListener('mouseleave', () => {
  const p = document.querySelector('.char-img-wrap');
  if (p) p.style.transform = '';
});

/* ══════════════════════════════════════════════════
   MUSIC PLAYER  — reads ./music/ directory listing
   Files named: 曲名-作者名.mp3
   ══════════════════════════════════════════════════ */

const MUSIC_DIR = 'music/';
const WAVE_CHARS = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'];

// DOM refs
const songListEl = document.getElementById('songList');
const playerBar = document.getElementById('playerBar');
const playerLoading = document.getElementById('playerLoading');
const pbTitle = document.getElementById('pbTitle');
const pbArtist = document.getElementById('pbArtist');
const pbPlay = document.getElementById('pbPlay');
const pbPrev = document.getElementById('pbPrev');
const pbNext = document.getElementById('pbNext');
const pbFill = document.getElementById('pbFill');
const pbTime = document.getElementById('pbTime');
const pbWave = document.getElementById('pbWave');
const pbVolSlider = document.getElementById('pbVolSlider');
const pbVolLabel = document.getElementById('pbVolLabel');
const pbVolIcon = document.getElementById('pbVolIcon');

// State
let playlist = [];
let currentIdx = -1;
let waveInterval = null;
let isMuted = false;
let savedVol = 0.8;

// Single persistent audio element (avoids state confusion on switch)
const audio = new Audio();
audio.volume = 0.8;

/* ── Format seconds as m:ss ── */
function fmtTime(s) {
  if (!isFinite(s)) return '0:00';
  const m = Math.floor(s / 60), ss = String(Math.floor(s % 60)).padStart(2, '0');
  return `${m}:${ss}`;
}

/* ── Parse filename: "曲名-作者名.mp3" → {title, artist} ── */
function parseFilename(filename) {
  const base = filename.replace(/\.mp3$/i, '');
  const dash = base.lastIndexOf('-');
  if (dash > 0) return { title: base.slice(0, dash), artist: base.slice(dash + 1) };
  return { title: base, artist: '未知' };
}

/* ── Update play button icon to reflect actual audio state ── */
function syncPlayBtn() {
  const playing = !audio.paused;
  pbPlay.textContent = playing ? '⏸' : '▶';
  pbPlay.classList.toggle('playing', playing);
  pbWave.classList.toggle('active', playing);
  if (playing) startWaveAnim(); else stopWaveAnim();
}

/* ── Fetch music list: tries index.json first, falls back to directory listing ── */
async function fetchMusicList() {
  // 1. Try static index.json (works on any web server / VPS / CDN)
  try {
    const res = await fetch(MUSIC_DIR + 'index.json?_=' + Date.now());
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.files) && data.files.length > 0) {
        console.log('[MusicPlayer] loaded from index.json:', data.files.length, 'tracks');
        return data.files.filter(f => /\.mp3$/i.test(f));
      }
    }
  } catch (e) { /* fall through to directory listing */ }

  // 2. Fallback: Python http.server directory listing (local dev only)
  try {
    const res = await fetch(MUSIC_DIR);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const html = await res.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const links = Array.from(doc.querySelectorAll('a[href]'));
    const mp3s = links
      .map(a => decodeURIComponent(a.getAttribute('href').replace(/^.*\//, '')))
      .filter(f => /\.mp3$/i.test(f));
    console.log('[MusicPlayer] loaded from directory listing:', mp3s.length, 'tracks');
    return mp3s;
  } catch (e) {
    console.warn('[MusicPlayer] both fetch methods failed:', e);
    return [];
  }
}

/* ── Build song list DOM ── */
function renderSongList() {
  if (playerLoading) playerLoading.remove();

  if (playlist.length === 0) {
    songListEl.innerHTML = `
      <div class="player-empty mono">
        <span class="zh">── ./music/ 目录为空，请放入 &lt;曲名-作者名&gt;.mp3 格式的音频文件 ──</span>
        <span class="en">── ./music/ is empty. Add MP3 files named &lt;title-artist&gt;.mp3 ──</span>
      </div>`;
    return;
  }

  songListEl.innerHTML = '';
  playlist.forEach((song, idx) => {
    const row = document.createElement('div');
    row.className = 'song-item';
    row.tabIndex = 0;
    row.setAttribute('role', 'button');
    row.setAttribute('aria-label', `播放 ${song.title} - ${song.artist}`);
    row.dataset.idx = idx;

    row.innerHTML = `
      <span class="snum mono">${String(idx + 1).padStart(2, '0')}</span>
      <div class="swave mono" aria-hidden="true">${Array.from({ length: 7 }, () => WAVE_CHARS[Math.floor(Math.random() * WAVE_CHARS.length)]).map(c => `<span>${c}</span>`).join('')}</div>
      <div class="sinfo">
        <span class="stitle">${escHtml(song.title)}</span>
        <span class="sprod mono">— ${escHtml(song.artist)}</span>
      </div>
      <span class="sdur mono" id="dur-${idx}">─:──</span>`;

    row.addEventListener('click', () => playSong(idx));
    row.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') playSong(idx); });
    songListEl.appendChild(row);
    probeDuration(song.file, idx);
  });
}

function escHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function probeDuration(file, idx) {
  const a = new Audio();
  a.preload = 'metadata';
  a.src = MUSIC_DIR + encodeURIComponent(file);
  a.addEventListener('loadedmetadata', () => {
    const el = document.getElementById('dur-' + idx);
    if (el) el.textContent = fmtTime(a.duration);
  });
}

/* ── Play a song by index ── */
function playSong(idx) {
  if (idx < 0 || idx >= playlist.length) return;

  // Unmark previous active row
  document.querySelectorAll('.song-item.playing').forEach(el => el.classList.remove('playing'));

  currentIdx = idx;
  const song = playlist[idx];

  // Load and play using the single persistent audio element
  audio.src = MUSIC_DIR + encodeURIComponent(song.file);
  audio.load();
  audio.play().catch(err => console.warn('[MusicPlayer] play error:', err));

  // Update now-playing bar
  pbTitle.textContent = song.title;
  pbArtist.textContent = '— ' + song.artist;
  playerBar.style.display = '';

  // Mark new row
  const row = songListEl.querySelector(`[data-idx="${idx}"]`);
  if (row) row.classList.add('playing');
}

/* ── Single audio event listeners (attached once) ── */
audio.addEventListener('play', syncPlayBtn);
audio.addEventListener('pause', syncPlayBtn);
audio.addEventListener('ended', () => {
  playSong((currentIdx + 1) % playlist.length);
});
audio.addEventListener('error', () => {
  pbPlay.textContent = '▶';
  pbPlay.classList.remove('playing');
  pbWave.classList.remove('active');
  pbTime.textContent = 'ERROR';
  stopWaveAnim();
});
audio.addEventListener('timeupdate', () => {
  const pct = audio.duration ? (audio.currentTime / audio.duration) * 100 : 0;
  pbFill.style.width = pct + '%';
  pbTime.textContent = fmtTime(audio.currentTime) + ' / ' + fmtTime(audio.duration);
});

/* ── Play/pause toggle ── */
pbPlay.addEventListener('click', () => {
  if (currentIdx < 0) { if (playlist.length > 0) playSong(0); return; }
  if (audio.paused) audio.play().catch(() => { });
  else audio.pause();
});

pbPrev.addEventListener('click', () => {
  if (playlist.length === 0) return;
  playSong((currentIdx - 1 + playlist.length) % playlist.length);
});
pbNext.addEventListener('click', () => {
  if (playlist.length === 0) return;
  playSong((currentIdx + 1) % playlist.length);
});

/* ── Progress bar click to seek ── */
document.querySelector('.pb-prog-wrap')?.addEventListener('click', e => {
  if (!audio || !audio.duration) return;
  const rect = e.currentTarget.getBoundingClientRect();
  const ratio = (e.clientX - rect.left) / rect.width;
  audio.currentTime = ratio * audio.duration;
});

/* ── Volume slider ── */
pbVolSlider.addEventListener('input', () => {
  const v = parseInt(pbVolSlider.value) / 100;
  audio.volume = v;
  savedVol = v;
  isMuted = v === 0;
  pbVolLabel.textContent = pbVolSlider.value + '%';
  pbVolIcon.textContent = v === 0 ? '🔇' : v < 0.4 ? '🔉' : '🔊';
});

pbVolIcon.addEventListener('click', () => {
  if (isMuted) {
    isMuted = false;
    audio.volume = savedVol || 0.8;
    pbVolSlider.value = Math.round((savedVol || 0.8) * 100);
    pbVolLabel.textContent = pbVolSlider.value + '%';
    pbVolIcon.textContent = '🔊';
  } else {
    savedVol = audio.volume;
    isMuted = true;
    audio.volume = 0;
    pbVolSlider.value = 0;
    pbVolLabel.textContent = '0%';
    pbVolIcon.textContent = '🔇';
  }
});

/* ── ASCII waveform animation in now-playing bar ── */
const WAVE_BLOCKS = '▁▁▂▂▃▃▄▄▅▅▆▆▇▇████▇▇▆▆▅▅▄▄▃▃▂▂▁▁';
let waveOffset = 0;
function startWaveAnim() {
  if (waveInterval) return;
  waveInterval = setInterval(() => {
    waveOffset = (waveOffset + 1) % WAVE_BLOCKS.length;
    // Fill the full container width with repeated wave chars
    const base = WAVE_BLOCKS.slice(waveOffset) + WAVE_BLOCKS.slice(0, waveOffset);
    // Repeat to ensure it always fills wider containers
    const repeated = (base + base).slice(0, 60);
    pbWave.textContent = repeated;
  }, 80);
}
function stopWaveAnim() {
  clearInterval(waveInterval); waveInterval = null;
  pbWave.textContent = '▁'.repeat(40);
}

/* ── Init: fetch and render ── */
(async () => {
  const files = await fetchMusicList();
  playlist = files.map(f => ({ file: f, ...parseFilename(f) }));
  renderSongList();

  // Update header count
  const header = document.getElementById('playerHeader');
  if (header && playlist.length > 0) {
    header.textContent = `┌─── [ LOCAL_MUSIC · 本地曲目 · ${playlist.length} tracks ] ` + '─'.repeat(Math.max(0, 42 - String(playlist.length).length)) + '┐';
  }
})();
