(() => {
  'use strict';
  const menu = document.querySelector('.menu-toggle');
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    menu.textContent = open ? '閉じる' : 'メニュー';
    document.querySelector('#navigation')?.classList.toggle('open', open);
    document.querySelector('.topbar')?.classList.toggle('menu-open', open);
  });
  const apiInput = document.querySelector('#api-search');
  const group = document.querySelector('#api-group');
  const rows = [...document.querySelectorAll('.operation-row')];
  function filter() {
    if (!apiInput || !group) return;
    const q = apiInput.value.trim().toLocaleLowerCase();
    const words = q.split(/\s+/).filter(Boolean);
    let count = 0;
    for (const row of rows) {
      row.hidden = Boolean((group.value && row.dataset.group !== group.value) || !words.every(w => row.dataset.search.includes(w)));
      count += Number(!row.hidden);
    }
    document.querySelector('#result-count').textContent = `${count} / ${rows.length} 操作`;
    document.querySelector('#empty-result').hidden = count > 0;
  }
  apiInput?.addEventListener('input', filter);
  group?.addEventListener('change', filter);
  document.querySelector('#clear-search')?.addEventListener('click', () => {
    apiInput.value = ''; group.value = ''; filter(); apiInput.focus();
  });
  function anchor() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (!target) return;
    if (target.dataset.destination) {
      location.replace(new URL(target.dataset.destination, location.href));
      return;
    }
    if (target.tagName === 'DETAILS') target.open = true;
    requestAnimationFrame(() => target.scrollIntoView({block:'start'}));
  }
  window.addEventListener('hashchange', anchor);
  if (location.hash) anchor();
  const input = document.querySelector('#site-search');
  const panel = document.querySelector('#search-results');
  if (!input || !panel) return;
  const normalize = s => s.normalize('NFKC').toLocaleLowerCase();
  let indexPromise;
  let sequence = 0;
  function getIndex() {
    if (!indexPromise) indexPromise = fetch(input.dataset.index).then(r => {
      if (!r.ok) throw new Error('search-index');
      return r.json();
    }).then(data => data.entries.map(e => ({...e, title:normalize(e.t), text:normalize(e.x)}))).catch(err => {
      indexPromise = undefined;
      throw err;
    });
    return indexPromise;
  }
  function score(e, words) {
    let value = 0;
    for (const word of words) {
      const hit = (e.title.includes(word) ? 12 : 0) + (e.text.includes(word) ? 1 : 0);
      if (!hit) return 0;
      value += hit;
    }
    return value;
  }
  async function search() {
    const current = ++sequence;
    const q = normalize(input.value.trim());
    panel.replaceChildren();
    if (!q) { panel.hidden = true; return; }
    try {
      const entries = await getIndex();
      if (current !== sequence) return;
      const words = q.split(/\s+/);
      const hits = entries.map(e => [score(e,words),e]).filter(([s]) => s > 0).sort((a,b) => b[0]-a[0]).slice(0,8);
      if (!hits.length) {
        const p = document.createElement('p'); p.textContent = '一致するページはありません。別の言葉で試してください。'; panel.append(p);
      }
      for (const [,e] of hits) {
        const a = document.createElement('a');
        a.href = new URL(e.u,new URL(input.dataset.index,location.href));
        const title = document.createElement('b'); title.textContent = e.t;
        const description = document.createElement('span');
        const at = Math.max(0,e.text.indexOf(words[0])-20);
        description.textContent = e.s + ' · ' + (at ? '…' : '') + e.x.slice(at,at+90);
        a.append(title,description); panel.append(a);
      }
      panel.hidden = false;
    } catch {
      if (current !== sequence) return;
      const p = document.createElement('p'); p.textContent = '検索を読み込めませんでした。接続を確認してもう一度入力してください。'; panel.append(p); panel.hidden = false;
    }
  }
  input.closest('form').addEventListener('submit', event => {
    event.preventDefault(); panel.querySelector('a')?.focus();
  });
  input.addEventListener('input', search);
  input.addEventListener('keydown', event => {
    if (event.key === 'Escape') { input.value = ''; search(); }
    if (event.key === 'ArrowDown') { event.preventDefault(); panel.querySelector('a')?.focus(); }
  });
  panel.addEventListener('keydown', event => {
    const links = [...panel.querySelectorAll('a')];
    const position = links.indexOf(document.activeElement);
    if (event.key === 'ArrowDown') { event.preventDefault(); links[Math.min(position+1,links.length-1)]?.focus(); }
    if (event.key === 'ArrowUp') { event.preventDefault(); if (position <= 0) input.focus(); else links[position-1]?.focus(); }
    if (event.key === 'Escape') { input.value = ''; search(); input.focus(); }
  });
})();
