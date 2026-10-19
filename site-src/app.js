// Progressive enhancement: every finding and episode also works without JavaScript.
const lab = document.querySelector('.example-lab');
if (lab) {
  const panels = [...lab.querySelectorAll('details.episode')];
  const links = [...lab.querySelectorAll('.example-nav a')];
  const selectEpisode = hash => {
    const panel = panels.find(item => '#' + item.id === hash);
    if (!panel) return;
    for (const item of panels) item.open = item === panel;
    for (const link of links) {
      if (link.hash === hash) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    }
  };
  lab.classList.add('is-enhanced');
  selectEpisode(location.hash);
  // Runs before the browser follows any same-page episode anchor, including deep links.
  document.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (link && link.hash && link.pathname === location.pathname) {
      selectEpisode(link.hash);
      if (link.closest('.example-nav')) {
        event.preventDefault();
        if (location.hash !== link.hash) history.pushState(null, '', link.hash);
      }
    }
  });
  window.addEventListener('hashchange', () => selectEpisode(location.hash));
}
const navLinks = [...document.querySelectorAll('.site-header nav a[href^="#"], .method-toc a')];
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      for (const link of navLinks) {
        if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      }
    }
  }, {rootMargin: '-15% 0px -65% 0px'});
  for (const link of navLinks) {
    const section = document.querySelector(link.hash);
    if (section) observer.observe(section);
  }
}
