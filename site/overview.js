// Optional condition inspector. Full curves and exact tables remain available without JS.
(() => {
  const input = document.getElementById('dose-probability');
  const target = document.getElementById('dose-comparison');
  const payload = document.getElementById('overview-data');
  if (!input || !target || !payload) return;
  const data = JSON.parse(payload.textContent);
  const names = {'gpt-6-luna':'GPT-6 Luna','glm-5.3-flash':'GLM-5.3 Flash','kimi-k3':'Kimi K3','nemotron':'Nemotron','qwen-ablated':'Qwen ablated'};
  const render = () => {
    const probability = Number(input.value);
    const wrapper = document.createElement('div');
    wrapper.className = 'table-scroll'; wrapper.tabIndex = 0;
    wrapper.setAttribute('role','region'); wrapper.setAttribute('aria-label','Comparison at selected timeout probability');
    const table = document.createElement('table');
    const caption = table.createCaption();
    caption.textContent = `${Math.round(probability * 100)}% assigned timeout probability · all eligible episodes`;
    const head = table.createTHead().insertRow();
    for (const name of ['Model','Checker pass','Failed + success claim','No answer at cap','n']) {
      const th = document.createElement('th'); th.scope = 'col'; th.textContent = name; head.append(th);
    }
    const body = table.createTBody();
    for (const [model,name] of Object.entries(names)) {
      const cell = data.rate_sweep.find(c => c.model === model && c.p === probability);
      const tr = body.insertRow();
      if (model === 'nemotron') tr.className = 'is-nemotron';
      const th = document.createElement('th'); th.scope = 'row'; th.textContent = name; tr.append(th);
      for (const metric of ['success','unsupported','cap']) {
        const rate = cell.rates[metric];
        const td = tr.insertCell(); td.textContent = rate.value.toFixed(1) + '%';
        td.title = `${rate.k}/${rate.n}; task-cluster 95% interval ${rate.lo.toFixed(1)}–${rate.hi.toFixed(1)}%`;
      }
      tr.insertCell().textContent = cell.n;
    }
    wrapper.append(table); target.replaceChildren(wrapper);
  };
  input.addEventListener('change',render); render();
})();
