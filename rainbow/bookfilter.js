/* Book categories and a reusable "Books" checkbox filter for the Reference Rainbow and Echoes.
 *
 *   const f = RainbowBooks.filter(container, { names, extras, onChange })
 *   f.has(bookIndex)    -> is the book (0 = Genesis … 65 = Revelation) selected?
 *   f.hasExtra(id)      -> is an extra group (e.g. 'deutero') selected?
 *   f.all()             -> true when everything is selected (no filtering)
 *   f.summary()         -> short label, e.g. "All books", "Gospels + Paul's Letters", "12 of 66 books"
 *   f.setVisibleExtras([...ids]) / f.reset()
 */
(function () {
  'use strict';
  const range = (a, b) => Array.from({ length: b - a + 1 }, (_, i) => a + i);
  const CATEGORIES = [
    { id: 'law', name: 'Law', testament: 'OT', books: range(0, 4) },
    { id: 'history', name: 'History', testament: 'OT', books: range(5, 16) },
    { id: 'wisdom', name: 'Wisdom / Poetry', testament: 'OT', books: range(17, 21) },
    { id: 'major', name: 'Major Prophets', testament: 'OT', books: range(22, 26) },
    { id: 'minor', name: 'Minor Prophets', testament: 'OT', books: range(27, 38) },
    { id: 'gospels', name: 'Gospels', testament: 'NT', books: range(39, 42) },
    { id: 'acts', name: 'Early Church History', testament: 'NT', books: [43] },
    { id: 'paul', name: "Paul's Letters", testament: 'NT', books: range(44, 56) },
    { id: 'general', name: 'General Letters', testament: 'NT', books: range(57, 64) },
    { id: 'prophecy', name: 'Prophecy', testament: 'NT', books: [65] },
  ];
  const TESTAMENTS = [{ id: 'OT', name: 'Old Testament' }, { id: 'NT', name: 'New Testament' }];
  const categoryOf = b => CATEGORIES.find(c => c.books.includes(b));
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const CSS = `
.bf{position:relative;display:inline-block}
.bf-btn{display:inline-flex;align-items:center;gap:6px;height:28px;padding:0 9px;border:1px solid var(--rule);border-radius:4px;background:var(--panel);color:var(--ink);font:inherit;font-size:12.5px;cursor:pointer;white-space:nowrap;max-width:260px}
.bf-btn span{overflow:hidden;text-overflow:ellipsis}
.bf-btn:hover,.bf.open .bf-btn{border-color:var(--ink)}
.bf-btn.filtered{border-color:var(--ribbon,var(--accent));box-shadow:inset 0 0 0 1px var(--ribbon,var(--accent))}
.bf-pop{position:fixed;z-index:60;width:min(560px,calc(100vw - 16px));max-height:min(560px,calc(100vh - 24px));overflow:auto;background:var(--panel);color:var(--ink);border:1px solid var(--rule);border-radius:6px;box-shadow:0 20px 60px var(--shadow);padding:12px 14px 14px;font-size:13px;line-height:1.35}
.bf-top{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;padding-bottom:10px;border-bottom:1px solid var(--rule);margin-bottom:10px}
.bf-top b{margin-right:auto;font-size:13px}
.bf-link{border:0;background:none;padding:0;font:inherit;font-size:12.5px;color:var(--muted);text-decoration:underline;text-decoration-style:dotted;text-underline-offset:3px;cursor:pointer}
.bf-link:hover{color:var(--ink)}
.bf-cols{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px 22px}
.bf-col{display:flex;flex-direction:column;gap:2px}
.bf label{display:flex;align-items:center;gap:7px;cursor:pointer;padding:2px 0}
.bf input[type=checkbox]{margin:0;width:15px;height:15px;accent-color:var(--ribbon,var(--accent));flex:none}
.bf-t{font-weight:600;padding:2px 0 4px;border-bottom:1px solid var(--rule);margin-bottom:2px}
.bf-cat{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center}
.bf-more{border:0;background:none;padding:2px 4px;font:inherit;font-size:11.5px;color:var(--muted);cursor:pointer;border-radius:3px}
.bf-more:hover{color:var(--ink);background:var(--wash,var(--control))}
.bf-books{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 10px;padding:2px 0 6px 22px;font-size:12.5px}
.bf-n{color:var(--muted);font-size:11.5px;font-variant-numeric:tabular-nums}
.bf-extra{margin-top:10px;padding-top:8px;border-top:1px solid var(--rule)}
@media (max-width:560px){.bf-cols{grid-template-columns:1fr}}`;
  let cssDone = false;

  function filter(container, opts) {
    if (!cssDone) { const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st); cssDone = true; }
    const names = opts.names || [];
    const extras = opts.extras || [];            // [{id, name}]
    let visibleExtras = new Set(extras.map(e => e.id));
    const selected = new Set(range(0, 65));
    const selectedExtras = new Set(extras.map(e => e.id));
    const expanded = new Set();
    const root = document.createElement('div');
    root.className = 'bf';
    root.innerHTML = `<button type="button" class="bf-btn" aria-haspopup="dialog" aria-expanded="false"><span></span><svg class="ico" viewBox="0 0 16 16" aria-hidden="true" style="width:12px;height:12px"><path d="M4 6l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button>
      <div class="bf-pop" role="dialog" aria-label="Choose books" hidden></div>`;
    container.appendChild(root);
    const btn = root.querySelector('.bf-btn'), pop = root.querySelector('.bf-pop');

    const all = () => selected.size === 66 && [...visibleExtras].every(id => selectedExtras.has(id));
    function summary() {
      if (all()) return 'All books';
      const n = selected.size, ex = [...visibleExtras].filter(id => selectedExtras.has(id)).length;
      if (!n && !ex) return 'No books';
      const full = CATEGORIES.filter(c => c.books.every(b => selected.has(b)));
      const fullBooks = new Set(full.flatMap(c => c.books));
      const loose = [...selected].filter(b => !fullBooks.has(b));
      for (const t of TESTAMENTS) {
        const tb = CATEGORIES.filter(c => c.testament === t.id).flatMap(c => c.books);
        if (n === tb.length && tb.every(b => selected.has(b))) return t.name;
      }
      if (!loose.length && full.length && full.length <= 2) return full.map(c => c.name).join(' + ');
      if (n === 1 && !ex) return names[[...selected][0]] || '1 book';
      return `${n} of 66 books`;
    }
    const state = cb => cb.every(Boolean) ? 'on' : cb.some(Boolean) ? 'mixed' : 'off';
    const box = (attr, st, label, extra = '') =>
      `<label><input type="checkbox" ${attr} ${st === 'on' ? 'checked' : ''} data-mixed="${st === 'mixed'}">${label}${extra}</label>`;
    function render() {
      btn.querySelector('span').textContent = `Books: ${summary()}`;
      btn.classList.toggle('filtered', !all());
      if (pop.hidden) return;
      const cols = TESTAMENTS.map(t => {
        const cats = CATEGORIES.filter(c => c.testament === t.id);
        const tState = state(cats.flatMap(c => c.books).map(b => selected.has(b)));
        return `<div class="bf-col"><div class="bf-t">${box(`data-t="${t.id}"`, tState, t.name)}</div>` + cats.map(c => {
          const st = state(c.books.map(b => selected.has(b)));
          const open = expanded.has(c.id);
          return `<div class="bf-cat">${box(`data-c="${c.id}"`, st, esc(c.name), ` <span class="bf-n">${c.books.filter(b => selected.has(b)).length}/${c.books.length}</span>`)}
            ${c.books.length > 1 ? `<button type="button" class="bf-more" data-x="${c.id}" aria-expanded="${open}">${open ? 'Hide books' : 'Books'}</button>` : '<span></span>'}</div>
            ${open ? `<div class="bf-books">${c.books.map(b => box(`data-b="${b}"`, selected.has(b) ? 'on' : 'off', esc(names[b] || `Book ${b + 1}`))).join('')}</div>` : ''}`;
        }).join('') + '</div>';
      }).join('');
      const ex = extras.filter(e => visibleExtras.has(e.id));
      pop.innerHTML = `<div class="bf-top"><b>Books</b><button type="button" class="bf-link" data-all>Select all</button><button type="button" class="bf-link" data-none>Deselect all</button><button type="button" class="bf-link" data-close>Done</button></div>
        <div class="bf-cols">${cols}</div>
        ${ex.length ? `<div class="bf-extra">${ex.map(e => box(`data-e="${e.id}"`, selectedExtras.has(e.id) ? 'on' : 'off', esc(e.name))).join('')}</div>` : ''}`;
      pop.querySelectorAll('input[data-mixed="true"]').forEach(i => { i.indeterminate = true; });
    }
    function place() {
      const r = btn.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight;
      let x = Math.min(r.left, innerWidth - w - 8), y = r.bottom + 6;
      if (y + h > innerHeight - 8) y = Math.max(8, r.top - h - 6);
      pop.style.left = Math.max(8, x) + 'px'; pop.style.top = y + 'px';
    }
    function open(v) {
      pop.hidden = !v; root.classList.toggle('open', v); btn.setAttribute('aria-expanded', String(v));
      if (v) { render(); place(); }
    }
    const changed = () => { render(); if (!pop.hidden) place(); opts.onChange && opts.onChange(); };
    btn.addEventListener('click', e => { e.stopPropagation(); open(pop.hidden); });
    pop.addEventListener('click', e => {
      e.stopPropagation();
      if (e.target.closest('[data-all]')) { range(0, 65).forEach(b => selected.add(b)); visibleExtras.forEach(id => selectedExtras.add(id)); changed(); }
      else if (e.target.closest('[data-none]')) { selected.clear(); selectedExtras.clear(); changed(); }
      else if (e.target.closest('[data-close]')) open(false);
      else if (e.target.closest('[data-x]')) { const id = e.target.closest('[data-x]').dataset.x; if (expanded.has(id)) expanded.delete(id); else expanded.add(id); render(); place(); }
    });
    pop.addEventListener('change', e => {
      const i = e.target;
      const set = (books, on) => books.forEach(b => on ? selected.add(b) : selected.delete(b));
      if (i.dataset.t) set(CATEGORIES.filter(c => c.testament === i.dataset.t).flatMap(c => c.books), i.checked);
      else if (i.dataset.c) set(CATEGORIES.find(c => c.id === i.dataset.c).books, i.checked);
      else if (i.dataset.b) set([+i.dataset.b], i.checked);
      else if (i.dataset.e) { if (i.checked) selectedExtras.add(i.dataset.e); else selectedExtras.delete(i.dataset.e); }
      changed();
    });
    document.addEventListener('click', e => { if (!pop.hidden && !root.contains(e.target)) open(false); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !pop.hidden) { open(false); btn.focus(); } });
    window.addEventListener('resize', () => { if (!pop.hidden) place(); });
    render();
    return {
      has: b => selected.has(b),
      hasExtra: id => !visibleExtras.has(id) || selectedExtras.has(id),
      all, summary,
      reset() { range(0, 65).forEach(b => selected.add(b)); extras.forEach(e => selectedExtras.add(e.id)); render(); },
      setVisibleExtras(ids) { visibleExtras = new Set(ids); render(); },
      selectedBooks: () => [...selected],
      button: btn,
    };
  }

  window.RainbowBooks = { CATEGORIES, TESTAMENTS, categoryOf, filter };
})();
