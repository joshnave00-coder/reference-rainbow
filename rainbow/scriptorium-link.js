/* The "Scriptorium" links on the Rainbow, Echoes, Read and Guide pages.
 * Scriptorium is a small local program, so a plain link fails when it isn't running. Instead the link opens a window that
 * checks whether it's running, offers "Open Scriptorium" when it is, and otherwise spells out how to start it. */
(function () {
  'use strict';
  const ADDR = 'http://127.0.0.1:8770/';
  const links = [...document.querySelectorAll('[data-scriptorium]')];
  if (!links.length) return;
  const served = location.protocol.startsWith('http') && location.pathname.startsWith('/rainbow/');
  if (served) { links.forEach(a => { a.href = '/'; }); return; }  // already inside Scriptorium

  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
  const WIN = 'Start Scriptorium (Windows).bat', MAC = 'Start Scriptorium (Mac).command';
  const folder = (() => {
    if (location.protocol !== 'file:') return '';
    let p = decodeURIComponent(location.pathname).replace(/\/rainbow\/[^/]*$/, '');
    if (/^\/[A-Za-z]:/.test(p)) p = p.slice(1).replace(/\//g, '\\');
    return p;
  })();

  const css = document.createElement('style');
  css.textContent = `
dialog.scr{width:min(620px,calc(100vw - 24px));max-height:calc(100vh - 32px);padding:0;border:1px solid var(--rule,#ddd);border-radius:8px;background:var(--panel,#fff);color:var(--ink,#1b1a21);box-shadow:0 30px 80px rgba(0,0,0,.3);font-family:var(--sans,system-ui,sans-serif)}
dialog.scr::backdrop{background:rgba(12,11,17,.45)}
.scr-head{display:flex;align-items:center;gap:10px;padding:18px 22px 12px;border-bottom:1px solid var(--rule,#ddd)}
.scr-head h2{margin:0 auto 0 0;font-family:var(--serif,Georgia,serif);font-weight:400;font-size:24px}
.scr-body{padding:14px 22px 20px;display:flex;flex-direction:column;gap:12px;font-size:14px;line-height:1.55}
.scr-status{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:6px;background:var(--wash,#f2f1f5);font-weight:600}
.scr-dot{width:10px;height:10px;border-radius:50%;background:#999;flex:none}
.scr-status[data-state="up"] .scr-dot{background:#2E9E5B}
.scr-status[data-state="down"] .scr-dot{background:#C8102E}
.scr-status[data-state="checking"] .scr-dot{animation:scrpulse 1s infinite alternate}
@keyframes scrpulse{from{opacity:.3}to{opacity:1}}
@media (prefers-reduced-motion: reduce){.scr-status[data-state="checking"] .scr-dot{animation:none}}
.scr-body ol{margin:0 0 4px;padding-left:22px;display:flex;flex-direction:column;gap:9px}
.scr-body ol li::marker{font-family:var(--sans,system-ui,sans-serif);font-weight:700}
.scr-body p{margin:0}
.scr-body code{font-size:12.5px;padding:2px 6px;border-radius:4px;background:var(--wash,#f2f1f5);word-break:break-all}
.scr-btn{display:inline-flex;align-items:center;justify-content:center;height:34px;padding:0 14px;border:1px solid var(--rule,#ddd);border-radius:5px;background:var(--panel,#fff);color:var(--ink,#1b1a21);font:inherit;font-size:13.5px;text-decoration:none;cursor:pointer;white-space:nowrap}
.scr-btn:hover{border-color:var(--ink,#1b1a21)}
.scr-btn.primary{background:var(--ribbon,var(--accent,#8C6A1C));border-color:var(--ribbon,var(--accent,#8C6A1C));color:#fff;font-weight:600}
.scr-row{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.scr-note{font-size:12.5px;color:var(--muted,#666)}
.scr-body details summary{cursor:pointer;font-weight:600}
.scr-body details ul{margin:8px 0 0;padding-left:20px}`;
  document.head.appendChild(css);

  const dlg = document.createElement('dialog');
  dlg.className = 'scr';
  dlg.setAttribute('aria-labelledby', 'scrTitle');
  const launcher = isMac ? MAC : WIN, other = isMac ? WIN : MAC;
  dlg.innerHTML = `
    <div class="scr-head"><h2 id="scrTitle">Scriptorium</h2><button class="scr-btn" type="button" data-scr-close>Close</button></div>
    <div class="scr-body">
      <p>Scriptorium is the full Bible database with its own reading room: 152 texts in 57 languages, word-by-word Hebrew and Greek, a Strong's concordance, a timeline of who wrote each book, and your own searches. It runs as a small program on this computer.</p>
      <p class="scr-status" data-state="checking" role="status"><span class="scr-dot"></span><span class="scr-text">Checking whether Scriptorium is running…</span></p>
      <div class="scr-up" hidden>
        <div class="scr-row"><a class="scr-btn primary" href="${ADDR}" target="_blank" rel="noopener">Open Scriptorium</a><span class="scr-note">It opens in a new tab at ${ADDR}</span></div>
      </div>
      <div class="scr-down" hidden>
        <p><b>It isn't running yet. To start it:</b></p>
        <ol>
          <li><b>First time only: install Python</b> (free) from <a href="https://www.python.org/downloads/" target="_blank" rel="noopener">python.org/downloads</a>.${isMac ? '' : ' On the installer\'s first screen, tick <b>Add python.exe to PATH</b>.'}</li>
          <li><b>Open the project folder</b>${folder
            ? `: <div class="scr-row" style="margin-top:4px"><code>${esc(folder)}</code><button class="scr-btn" type="button" data-scr-copy>Copy path</button></div>`
            : ': the folder you unzipped, with <b>Read the Bible.html</b> in it.'}</li>
          <li><b>Double-click “${esc(launcher)}”.</b> A black window opens.
            ${isMac ? "If macOS says it can't be opened, right-click the file and choose <b>Open</b>." : 'If Windows shows “Windows protected your PC”, click <b>More info</b>, then <b>Run anyway</b>.'}
            The first time, it downloads about 350 MB and builds the database, which takes a few minutes.</li>
          <li><b>Leave the black window open.</b> Scriptorium opens in your browser by itself when it's ready, and this window updates too. Close the black window when you're done to stop it.</li>
        </ol>
        <p class="scr-note">On ${isMac ? 'Windows' : 'a Mac'}, double-click “${esc(other)}” instead.</p>
        <div class="scr-row"><button class="scr-btn" type="button" data-scr-check>Check again</button><a class="scr-btn" href="${ADDR}" target="_blank" rel="noopener">Open Scriptorium anyway</a><a class="scr-note" href="guide.html#scriptorium">More in the guide</a></div>
      </div>
      <details><summary>What's inside Scriptorium?</summary><ul>
        <li><b>Read</b>: any passage in several translations side by side, with the Hebrew or Greek word by word.</li>
        <li><b>Strong's</b>: look up any word: definitions, how translations render it, every verse it's in.</li>
        <li><b>Books &amp; dating</b>: a timeline of who wrote each book, when and where, with sources.</li>
        <li><b>Translations</b>: every text with its language, coverage and licence.</li>
        <li><b>Tables</b> and <b>SQL</b>: browse the database or ask your own questions.</li>
        <li><b>Data &amp; setup</b>: start, stop, update the data, or make a copy to share.</li>
      </ul></details>
    </div>`;
  document.body.appendChild(dlg);
  const status = dlg.querySelector('.scr-status'), statusText = dlg.querySelector('.scr-text');
  let timer = 0;

  async function check() {
    status.dataset.state = 'checking';
    statusText.textContent = 'Checking whether Scriptorium is running…';
    let up = false;
    try {
      const ctl = new AbortController();
      const t = setTimeout(() => ctl.abort(), 1500);
      const r = await fetch(ADDR + 'api/ping', { cache: 'no-store', signal: ctl.signal });
      clearTimeout(t);
      up = r.ok && (await r.json()).app === 'Scriptorium';
    } catch (_) { up = false; }
    status.dataset.state = up ? 'up' : 'down';
    statusText.textContent = up ? 'Scriptorium is running.' : 'Scriptorium is not running on this computer.';
    dlg.querySelector('.scr-up').hidden = !up;
    dlg.querySelector('.scr-down').hidden = up;
    clearTimeout(timer);
    if (dlg.open && !up) timer = setTimeout(check, 3000);  // keep watching while the instructions are shown
  }
  function open(e) {
    e.preventDefault();
    if (!dlg.open) dlg.showModal();
    check();
  }
  links.forEach(a => { a.href = ADDR; a.addEventListener('click', open); });
  dlg.addEventListener('close', () => clearTimeout(timer));
  dlg.addEventListener('click', async e => {
    if (e.target === dlg || e.target.closest('[data-scr-close]')) return dlg.close();
    if (e.target.closest('[data-scr-check]')) return check();
    const copy = e.target.closest('[data-scr-copy]');
    if (copy) {
      try { await navigator.clipboard.writeText(folder); copy.textContent = 'Copied'; } catch (_) { copy.textContent = 'Select the path to copy it'; }
      setTimeout(() => { copy.textContent = 'Copy path'; }, 1800);
    }
  });
})();
