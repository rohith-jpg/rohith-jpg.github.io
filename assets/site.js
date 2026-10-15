const root = document.documentElement;
const themeButton = document.querySelector('.theme-toggle');
function labelTheme() {
  const dark = root.dataset.theme !== 'light';
  themeButton?.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} mode`);
  themeButton?.setAttribute('aria-pressed', String(!dark));
}
themeButton?.addEventListener('click', () => {
  root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
  try { localStorage.setItem('theme', root.dataset.theme); } catch { /* Private browsing. */ }
  labelTheme();
});
labelTheme();
const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('.nav');
menu?.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  menu.setAttribute('aria-expanded', String(open));
});
nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
  nav.classList.remove('open');
  menu?.setAttribute('aria-expanded', 'false');
}));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && nav?.classList.contains('open')) {
    nav.classList.remove('open');
    menu?.setAttribute('aria-expanded', 'false');
    menu?.focus();
  }
});
const filters = document.querySelector('.filters');
if (filters) {
  filters.hidden = false;
  const cards = [...document.querySelectorAll('.project')];
  filters.addEventListener('click', event => {
    const button = event.target.closest('[data-filter]');
    if (!button) return;
    filters.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    cards.forEach(card => { card.hidden = button.dataset.filter !== 'All' && card.dataset.category !== button.dataset.filter; });
    const count = cards.filter(card => !card.hidden).length;
    document.querySelector('#filter-status').textContent = `${count} projects shown`;
  });
}
