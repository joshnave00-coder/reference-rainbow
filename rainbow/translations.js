/* Bible translations for the Reference Rainbow and Echoes.
 * The King James Version is built into data.js; every other translation is a separate file in texts/,
 * loaded only when chosen (script tags, so it also works when the page is opened straight from disk).
 * The list comes from texts/manifest.js (written by build_texts.py). */
(function () {
  'use strict';
  const KEY = 'reference-rainbow-translation';
  const LIST = (window.RAINBOW_TRANSLATIONS && window.RAINBOW_TRANSLATIONS.length) ? window.RAINBOW_TRANSLATIONS
    : [{ id: 'KJV', name: 'King James Version', short: 'KJV', group: 'King James tradition', builtin: true, red: true, coverage: 'Old and New Testaments', license: 'Public domain' }];
  const byId = id => LIST.find(t => t.id === id);
  const b64 = s => { const bin = atob(s), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u; };
  const inflate = s => new Response(new Blob([b64(s)]).stream().pipeThrough(new DecompressionStream('gzip')));
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const cache = new Map();

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const el = document.createElement('script');
      el.src = src; el.charset = 'utf-8';
      el.onload = resolve;
      el.onerror = () => reject(new Error(`Could not load ${src}. Keep the texts folder next to this page.`));
      document.head.appendChild(el);
    });
  }

  // -> Promise<{id, info, verses: string[31102] (KJV verse order; '' = not in this translation), red: Map(verse -> [[start, end, kind]])}>
  function load(id) {
    if (!byId(id)) id = 'KJV';
    if (cache.has(id)) return cache.get(id);
    const job = (async () => {
      const info = byId(id);
      let payload;
      if (info.builtin) payload = { text: window.RAINBOW_DATA.text, red: window.RAINBOW_DATA.red };
      else {
        if (!(window.RAINBOW_TEXTS || {})[id]) await loadScript(`texts/${id}.js`);
        payload = (window.RAINBOW_TEXTS || {})[id];
        if (!payload) throw new Error(`texts/${id}.js did not contain ${id}.`);
      }
      const verses = (await inflate(payload.text).text()).split('\n');
      const red = new Map();
      if (payload.red && payload.red.count) {
        const [g, a, z, k] = await Promise.all([payload.red.gid, payload.red.start, payload.red.end, payload.red.kind].map(x => inflate(x).arrayBuffer()));
        const G = new Uint16Array(g), A = new Uint16Array(a), Z = new Uint16Array(z), K = new Uint8Array(k);
        for (let i = 0; i < G.length; i++) { if (!red.has(G[i])) red.set(G[i], []); red.get(G[i]).push([A[i], Z[i], K[i]]); }
      }
      return { id, info, verses, red };
    })();
    cache.set(id, job);
    job.catch(() => cache.delete(id));
    return job;
  }

  function saved() {
    let v = null;
    try { v = localStorage.getItem(KEY); } catch (_) { /* storage blocked */ }
    return byId(v) ? v : 'KJV';
  }
  function save(id) { try { localStorage.setItem(KEY, id); } catch (_) { /* storage blocked */ } }

  // <optgroup>/<option> markup for a <select>, grouped as in the manifest
  function optionsHtml(current) {
    const groups = [];
    for (const t of LIST) {
      let g = groups.find(x => x.name === t.group);
      if (!g) groups.push(g = { name: t.group, items: [] });
      g.items.push(t);
    }
    return groups.map(g => `<optgroup label="${esc(g.name)}">${g.items.map(t =>
      `<option value="${esc(t.id)}"${t.id === current ? ' selected' : ''}>${esc(t.name)}${t.coverage && t.coverage !== 'Old and New Testaments' ? ` (${esc(t.coverage)})` : ''}</option>`).join('')}</optgroup>`).join('');
  }

  window.RainbowTexts = { list: LIST, byId, load, saved, save, optionsHtml };
})();
