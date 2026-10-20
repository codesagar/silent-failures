// Open the selected episode when a shared link targets a message or its verdict.
(() => {
  const revealConversationTarget = (hash, scroll = false) => {
    if (!hash) return;
    let id;
    try { id = decodeURIComponent(hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    const episode = target?.closest('details.episode');
    if (!episode || target === episode) return;
    const lab = episode.closest('.example-lab');
    if (!lab) return;
    for (const panel of lab.querySelectorAll('details.episode')) {
      panel.open = panel === episode;
    }
    for (const link of lab.querySelectorAll('.example-nav a')) {
      if (link.hash === '#' + episode.id) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    }
    for (let parent = target.parentElement; parent && parent !== episode; parent = parent.parentElement) {
      if (parent.tagName === 'DETAILS') parent.open = true;
    }
    if (scroll) {
      requestAnimationFrame(() => {
        if (location.hash === hash) target.scrollIntoView({behavior: 'instant', block: 'start'});
      });
    }
  };
  revealConversationTarget(location.hash, true);
  document.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (link && link.origin === location.origin && link.pathname === location.pathname) {
      revealConversationTarget(link.hash);
    }
  });
  window.addEventListener('hashchange', () => revealConversationTarget(location.hash, true));
})();
