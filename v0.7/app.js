(() => {
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.sidebar');
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
    menu.textContent = open ? '閉じる' : 'メニュー';
  });
  const input = document.querySelector('#api-search');
  const group = document.querySelector('#api-group');
  const cards = [...document.querySelectorAll('.operation')];
  function filter() {
    const q = (input?.value || '').trim().toLocaleLowerCase();
    let count = 0;
    for (const card of cards) {
      const visible = (!group.value || card.dataset.group === group.value) && (!q || card.dataset.search.includes(q));
      card.hidden = !visible;
      count += Number(visible);
    }
    document.querySelector('#result-count').textContent = `${count} / ${cards.length} 操作を表示`;
    document.querySelector('#empty-result').hidden = count > 0;
  }
  input?.addEventListener('input', filter);
  group?.addEventListener('change', filter);
  document.querySelector('#clear-search')?.addEventListener('click', () => {
    input.value = ''; group.value = ''; filter(); input.focus();
  });
  function openAnchor() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (!target) return;
    if (target.classList.contains('operation')) {
      input.value = ''; group.value = ''; filter();
    }
    if (target.tagName === 'DETAILS') target.open = true;
    requestAnimationFrame(() => target.scrollIntoView({block:'start'}));
  }
  window.addEventListener('hashchange', openAnchor);
  if (input) filter();
  if (location.hash) openAnchor();

  const box = document.querySelector('#site-search');
  const panel = document.querySelector('#search-results');
  let index = null;
  async function loadIndex() {
    if (index) return index;
    try { index = (await (await fetch(box.dataset.index)).json()).entries; } catch { index = []; }
    return index;
  }
  function score(entry, words) {
    let total = 0;
    const title = entry.t.toLocaleLowerCase();
    const heads = entry.h.join(' ').toLocaleLowerCase();
    const text = entry.x.toLocaleLowerCase();
    for (const w of words) {
      let s = 0;
      if (title.includes(w)) s += 10;
      if (heads.includes(w)) s += 5;
      if (text.includes(w)) s += 1;
      if (!s) return 0;
      total += s;
    }
    return total;
  }
  function excerpt(entry, words) {
    const text = entry.x;
    const lower = text.toLocaleLowerCase();
    const at = words.map(w => lower.indexOf(w)).filter(i => i >= 0).sort((a, b) => a - b)[0];
    if (at === undefined) return '';
    return (at > 20 ? '…' : '') + text.slice(Math.max(0, at - 20), at + 70) + '…';
  }
  async function search() {
    const q = box.value.trim().toLocaleLowerCase();
    if (!q) { panel.hidden = true; panel.textContent = ''; return; }
    const words = q.split(/\s+/);
    const hits = (await loadIndex()).map(e => [score(e, words), e]).filter(x => x[0] > 0).sort((a, b) => b[0] - a[0]).slice(0, 8);
    panel.textContent = '';
    if (!hits.length) { const p = document.createElement('p'); p.textContent = '一致するページはありません。別の言葉で試してください。'; panel.append(p); }
    for (const [, e] of hits) {
      const a = document.createElement('a');
      a.href = new URL(e.u, new URL(box.dataset.index, location.href)).href;
      const b = document.createElement('b'); b.textContent = e.t;
      const s = document.createElement('span'); s.textContent = e.s + (excerpt(e, words) ? ' ・ ' + excerpt(e, words) : '');
      a.append(b, s); panel.append(a);
    }
    panel.hidden = false;
  }
  box?.addEventListener('input', search);
  box?.addEventListener('keydown', ev => { if (ev.key === 'Escape') { box.value = ''; search(); } });
})();
