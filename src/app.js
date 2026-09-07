// Progressive enhancement only: the guides and navigation work without JS.
function updateLanguageLinks() {
  for (const link of document.querySelectorAll('.language')) {
    const url = new URL(link.href);
    url.hash = location.hash;
    link.href = url.href;
  }
}
updateLanguageLinks();
window.addEventListener('hashchange', updateLanguageLinks);

const sections = [...document.querySelectorAll('main section')];
const navigation = [...document.querySelectorAll('.contents a')];
function updateActiveSection() {
  const current = sections.findLast((section) => section.getBoundingClientRect().top <= 80) ?? sections[0];
  for (const link of navigation) {
    if (link.hash === `#${current.id}`) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
}
let scheduled = false;
window.addEventListener('scroll', () => {
  if (scheduled) return;
  scheduled = true;
  requestAnimationFrame(() => { updateActiveSection(); scheduled = false; });
}, { passive: true });
updateActiveSection();
