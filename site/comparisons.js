// Enhance static comparison pages; every example remains readable without JavaScript.
(() => {
  const browser = document.querySelector('.comparison-browser');
  if (browser) {
    const modelFilter = browser.querySelector('#comparison-model-filter');
    const behaviorFilter = browser.querySelector('#comparison-behavior-filter');
    const cells = [...browser.querySelectorAll('.comparison-cell')];
    const status = browser.querySelector('.comparison-filter-status');
    const revealControls = browser.querySelector('.comparison-filters');
    if (modelFilter && behaviorFilter) {
      if (revealControls) revealControls.hidden = false;
      const filter = () => {
        let visible = 0;
        for (const cell of cells) {
          const matchesModel = modelFilter.value === 'all' || cell.dataset.model === modelFilter.value;
          const matchesBehavior = behaviorFilter.value === 'all' || cell.dataset.behavior === behaviorFilter.value;
          cell.hidden = !matchesModel || !matchesBehavior;
          if (!cell.hidden) visible++;
        }
        if (status) status.textContent = `${visible} model and behavior ${visible === 1 ? 'group' : 'groups'} shown.`;
      };
      const filterToCell = cell => {
        modelFilter.value = [...modelFilter.options].some(option => option.value === cell.dataset.model)
          ? cell.dataset.model : 'all';
        behaviorFilter.value = [...behaviorFilter.options].some(option => option.value === cell.dataset.behavior)
          ? cell.dataset.behavior : 'all';
        filter();
      };
      const revealHash = (scroll = false) => {
        if (!location.hash) return;
        let id;
        try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
        const target = document.getElementById(id);
        const cell = target?.closest('.comparison-cell');
        if (!cell) return;
        filterToCell(cell);
        if (scroll) requestAnimationFrame(() => target.scrollIntoView({block: 'start', behavior: 'instant'}));
      };
      modelFilter.addEventListener('change', filter);
      behaviorFilter.addEventListener('change', filter);
      browser.addEventListener('click', event => {
        const link = event.target.closest('a');
        if (!link || link.origin !== location.origin || link.pathname !== location.pathname || !link.hash) return;
        let id;
        try { id = decodeURIComponent(link.hash.slice(1)); } catch { return; }
        const target = document.getElementById(id);
        const cell = target?.closest('.comparison-cell');
        if (cell) filterToCell(cell);
      });
      filter();
      revealHash(true);
      window.addEventListener('hashchange', () => revealHash(true));
    }
  }

  const paired = document.querySelector('.paired-comparison');
  if (!paired) return;
  const leftSelect = paired.querySelector('#pair-left');
  const rightSelect = paired.querySelector('#pair-right');
  const panels = [...paired.querySelectorAll('.comparison-model')];
  const models = panels.map(panel => panel.dataset.model);
  const controls = paired.querySelector('.pair-controls');
  const status = paired.querySelector('.pair-status');
  const expandButton = paired.querySelector('#pair-expand');
  if (models.length < 2) {
    if (controls) controls.hidden = true;
    if (status) status.textContent = models.length === 1
      ? `Only ${panels[0].dataset.modelLabel || models[0]} is available in this comparison group.`
      : 'No model conversations are available in this comparison group.';
    const revealSingle = () => {
      let target;
      try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch { return; }
      if (!target?.closest('.comparison-model')) return;
      for (let ancestor = target.parentElement; ancestor && ancestor !== paired; ancestor = ancestor.parentElement) {
        if (ancestor.tagName === 'DETAILS') ancestor.open = true;
      }
      requestAnimationFrame(() => target.scrollIntoView({block: 'start', behavior: 'instant'}));
    };
    revealSingle();
    window.addEventListener('hashchange', revealSingle);
    return;
  }
  if (!leftSelect || !rightSelect) return;
  const params = new URLSearchParams(location.search);
  const valid = value => models.includes(value);
  let left = valid(params.get('left')) ? params.get('left')
    : valid(paired.dataset.defaultLeft) ? paired.dataset.defaultLeft : models[0];
  let right = valid(params.get('right')) ? params.get('right')
    : valid(paired.dataset.defaultRight) ? paired.dataset.defaultRight : models.find(model => model !== left);
  if (left === right) right = models.find(model => model !== left);
  if (controls) controls.hidden = false;
  paired.classList.add('pair-enhanced');
  for (const panel of panels) {
    const slot = document.createElement('p');
    slot.className = 'pair-slot';
    slot.setAttribute('aria-hidden', 'true');
    panel.prepend(slot);
  }
  const label = model => panels.find(panel => panel.dataset.model === model)?.dataset.modelLabel || model;
  const visibleConversations = () => panels.filter(panel => !panel.hidden)
    .map(panel => panel.querySelector('.model-conversation')).filter(Boolean);
  const updateExpandButton = () => {
    if (!expandButton) return;
    const conversations = visibleConversations();
    const allOpen = conversations.length > 0 && conversations.every(details => details.open);
    expandButton.textContent = allOpen ? 'Close both full conversations' : 'Open both full conversations';
    expandButton.setAttribute('aria-expanded', String(allOpen));
  };
  const render = (saveUrl = false) => {
    leftSelect.value = left;
    rightSelect.value = right;
    for (const panel of panels) {
      const isLeft = panel.dataset.model === left;
      const isRight = panel.dataset.model === right;
      panel.hidden = !isLeft && !isRight;
      panel.dataset.pairSlot = isLeft ? 'left' : isRight ? 'right' : '';
      panel.querySelector('.pair-slot').textContent = isLeft ? 'Left comparison' : 'Right comparison';
    }
    const columns = paired.querySelector('.pair-columns');
    if (columns) {
      const ordered = [panels.find(panel => panel.dataset.model === left),
        panels.find(panel => panel.dataset.model === right),
        ...panels.filter(panel => panel.hidden)];
      if (ordered.some((panel, index) => columns.children[index] !== panel)) {
        for (const panel of ordered) columns.append(panel);
      }
    }
    updateExpandButton();
    if (status) status.textContent = `Comparing ${label(left)} with ${label(right)}. Each conversation keeps its own recorded sequence.`;
    if (saveUrl) {
      const url = new URL(location.href);
      url.searchParams.set('left', left);
      url.searchParams.set('right', right);
      if (url.hash) {
        let target;
        try { target = document.getElementById(decodeURIComponent(url.hash.slice(1))); } catch {}
        if (target?.closest('.comparison-model')?.hidden) url.hash = '';
      }
      history.replaceState(null, '', url);
    }
  };
  leftSelect.addEventListener('change', () => {
    const previous = left;
    left = leftSelect.value;
    if (left === right) right = previous;
    render(true);
  });
  rightSelect.addEventListener('change', () => {
    const previous = right;
    right = rightSelect.value;
    if (left === right) left = previous;
    render(true);
  });
  if (expandButton) {
    expandButton.addEventListener('click', () => {
      const conversations = visibleConversations();
      const open = !conversations.every(details => details.open);
      for (const details of conversations) details.open = open;
      updateExpandButton();
    });
    for (const panel of panels) {
      panel.querySelector('.model-conversation')?.addEventListener('toggle', updateExpandButton);
    }
    updateExpandButton();
  }
  const revealMessage = (scroll = false) => {
    if (!location.hash) return;
    let target;
    try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch { return; }
    const panel = target?.closest('.comparison-model');
    if (!panel) return;
    if (panel.dataset.model !== left && panel.dataset.model !== right) {
      right = panel.dataset.model;
      render(true);
    }
    for (let ancestor = target.parentElement; ancestor && ancestor !== panel; ancestor = ancestor.parentElement) {
      if (ancestor.tagName === 'DETAILS') ancestor.open = true;
    }
    if (scroll) requestAnimationFrame(() => target.scrollIntoView({block: 'start', behavior: 'instant'}));
  };
  paired.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link || link.origin !== location.origin || link.pathname !== location.pathname || !link.hash) return;
    let target;
    try { target = document.getElementById(decodeURIComponent(link.hash.slice(1))); } catch { return; }
    const panel = target?.closest('.comparison-model');
    if (!panel) return;
    if (panel.dataset.model !== left && panel.dataset.model !== right) {
      right = panel.dataset.model;
      render(true);
    }
    for (let ancestor = target.parentElement; ancestor && ancestor !== panel; ancestor = ancestor.parentElement) {
      if (ancestor.tagName === 'DETAILS') ancestor.open = true;
    }
  });
  render();
  revealMessage(true);
  window.addEventListener('hashchange', () => revealMessage(true));
  window.addEventListener('popstate', () => {
    const query = new URLSearchParams(location.search);
    if (valid(query.get('left'))) left = query.get('left');
    if (valid(query.get('right'))) right = query.get('right');
    if (left === right) right = models.find(model => model !== left);
    render();
    revealMessage(true);
  });
})();
