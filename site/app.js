// Progressive enhancement only; all content, charts, and sources exist without JS.
const navLinks = [...document.querySelectorAll('.site-header nav a[href^="#"], .method-toc a')];
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      for (const link of navLinks) {
        if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      }
    }
  }, {rootMargin: '-15% 0px -65% 0px'});
  for (const link of navLinks) {
    const section = document.querySelector(link.hash);
    if (section) observer.observe(section);
  }
}
