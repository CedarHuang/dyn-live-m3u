const urlInput = document.getElementById('urlInput');
const taskList = document.getElementById('taskList');

// --- event delegation ---

taskList.addEventListener('click', e => {
  const btn = e.target.closest('button');
  if (!btn) return;
  const id = btn.dataset.id;
  if (btn.classList.contains('js-sync')) syncOne(id, btn);
});

taskList.addEventListener('change', e => {
  if (e.target.classList.contains('js-toggle')) {
    toggleTask(e.target.dataset.id, e.target.checked);
  }
});

urlInput.addEventListener('change', () => {
  chrome.runtime.sendMessage({ type: 'setUrl', url: urlInput.value.trim() });
});

// --- render ---

async function render() {
  const state = await chrome.runtime.sendMessage({ type: 'getState' });
  urlInput.value = state.url || '';

  const logEl = document.getElementById('log');
  const logs = state.logs || [];
  logEl.innerHTML = logs.slice(-20).map(l => {
    const cls = l.level === 'warn' ? 'warn' : l.level === 'error' ? 'err' : '';
    return `<div class="entry ${cls}">${new Date(l.time).toLocaleTimeString('zh-CN')}  ${esc(l.msg)}</div>`;
  }).join('');
  logEl.scrollTop = logEl.scrollHeight;

  taskList.innerHTML = state.tasks.map(t => {
    const r = t._lastResult;
    let statusText = '', statusClass = '';
    if (r) {
      if (!r.ok) { statusText = r.error || '失败'; statusClass = 'err'; }
      else if (r.synced === false) { statusText = '已同步'; statusClass = 'ok'; }
      else { statusText = '已推送'; statusClass = 'ok'; }
    }
    const time = t._lastSync ? new Date(t._lastSync).toLocaleString('zh-CN') : '';

    return `<div class="task">
      <label class="toggle">
        <input type="checkbox" class="js-toggle" data-id="${esc(t.id)}" ${t.enabled ? 'checked' : ''}>
        <span class="slider"></span>
      </label>
      <span class="task-name">${esc(t.name)}</span>
      <span class="task-status ${statusClass}">${time || ''}<br>${statusText || '待同步'}</span>
      <button class="btn btn-primary js-sync" data-id="${esc(t.id)}" ${!t.enabled ? 'disabled' : ''}>同步</button>
    </div>`;
  }).join('');
}

function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

// --- actions ---

async function toggleTask(id, enabled) {
  await chrome.runtime.sendMessage({ type: 'toggle', id, enabled });
  render();
}

async function syncOne(id, btn) {
  btn.disabled = true;
  btn.textContent = '...';
  await chrome.runtime.sendMessage({ type: 'sync', id });
  render();
}

render();
