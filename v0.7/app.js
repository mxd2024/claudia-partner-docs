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
})();
