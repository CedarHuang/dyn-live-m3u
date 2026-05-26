const PRESET_TASKS = [
  {
    id: 'bilibili-cookie',
    name: 'B站 Cookie',
    platform: 'bilibili',
    cookies: [
      { name: 'SESSDATA', url: 'https://live.bilibili.com' },
      { name: 'bili_jct', url: 'https://live.bilibili.com' },
    ],
  },
];

// precompute tracked cookie identifiers for fast onChanged matching
const _WATCHED = new Set(PRESET_TASKS.flatMap(t =>
  (t.cookies || []).map(c => {
    const host = new URL(c.url).hostname;
    return c.name + '@' + host;
  })
));

// --- storage ---

async function _getState() {
  const data = await chrome.storage.local.get(['url', 'tasks', 'logs']);
  return {
    url: data.url || '',
    tasks: data.tasks || {},
    logs: data.logs || [],
  };
}

async function _log(level, msg) {
  try {
    const data = await chrome.storage.local.get('logs');
    const logs = (data.logs || []).slice(-50);
    logs.push({ time: Date.now(), level, msg });
    await chrome.storage.local.set({ logs });
  } catch (e) {
    console.error('[sync] log error:', e);
  }
}

async function _saveTask(task) {
  const { tasks } = await _getState();
  tasks[task.id] = {
    enabled: task.enabled,
    _lastValue: task._lastValue,
    _lastSync: task._lastSync,
    _lastResult: task._lastResult,
  };
  await chrome.storage.local.set({ tasks });
}

// --- task building (pure) ---

function _buildTasks(state) {
  const { url, tasks } = state;
  if (!url) return [];
  return PRESET_TASKS.filter(t => {
    const saved = tasks[t.id] || {};
    return saved.enabled !== false;
  }).map(t => {
    const saved = tasks[t.id] || {};
    return {
      ...t,
      url,
      enabled: saved.enabled !== false,
      _lastValue: saved._lastValue,
      _lastSync: saved._lastSync,
      _lastResult: saved._lastResult,
    };
  });
}

function _viewTasks(state) {
  const { url, tasks } = state;
  return PRESET_TASKS.map(t => {
    const saved = tasks[t.id] || {};
    return {
      ...t,
      enabled: saved.enabled !== false,
      _lastValue: saved._lastValue,
      _lastSync: saved._lastSync,
      _lastResult: saved._lastResult,
    };
  });
}

// --- sync engine ---

async function _readCookies(task) {
  const pairs = [];
  for (const item of (task.cookies || [])) {
    const c = await chrome.cookies.get({ url: item.url, name: item.name });
    if (c) pairs.push({ name: item.name, value: c.value });
  }
  return pairs;
}

function _fingerprint(pairs) {
  return pairs.map(p => p.name + '=' + p.value).sort().join('; ');
}

async function syncTask(task, force) {
  const pairs = await _readCookies(task);
  if (pairs.length === 0) {
    const result = { ok: false, error: '未读取到 cookie' };
    task._lastSync = Date.now();
    task._lastResult = result;
    await _log('error', `${task.name}: 未读取到 cookie`);
    await _saveTask(task);
    return result;
  }

  const current = _fingerprint(pairs);
  if (!force && current === task._lastValue) {
    const result = { ok: true, synced: false };
    task._lastSync = Date.now();
    task._lastResult = result;
    await _saveTask(task);
    return result;
  }

  try {
    const resp = await fetch(task.url + '/api/default/cookie', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform: task.platform, cookies: current }),
    });

    let result;
    if (resp.ok) {
      const body = await resp.json();
      result = { ok: true, synced: body.synced !== false };
    } else {
      result = { ok: false, error: 'HTTP ' + resp.status };
    }
    task._lastSync = Date.now();
    task._lastResult = result;
    if (result.synced) {
      task._lastValue = current;
      await _log('info', `${task.name}: 已推送`);
    }
    await _saveTask(task);
    return result;
  } catch (e) {
    const result = { ok: false, error: e.message };
    task._lastSync = Date.now();
    task._lastResult = result;
    await _log('error', `${task.name}: 推送失败 (${e.message})`);
    await _saveTask(task);
    return result;
  }
}

async function syncAll(force) {
  const state = await _getState();
  const tasks = _buildTasks(state);
  for (const task of tasks) {
    await syncTask(task, force);
  }
}

// --- lifecycle ---

chrome.runtime.onStartup.addListener(() => { _log('info', '扩展启动'); syncAll(); });
syncAll();

// --- cookie change ---

chrome.cookies.onChanged.addListener(async ({ cookie, removed }) => {
  if (removed) return;
  // check against precomputed set: cookie-name @ hostname
  for (const entry of _WATCHED) {
    const [name, host] = entry.split('@');
    if (cookie.name === name && (cookie.domain.includes(host) || host.includes(cookie.domain.replace(/^\./, '')))) {
      await _log('info', `cookie "${name}" 变化`);
      syncAll(true);
      return;
    }
  }
});

// --- messages ---

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'getState') {
    _getState().then(state => {
      sendResponse({ url: state.url, tasks: _viewTasks(state), logs: state.logs });
    });
    return true;
  }
  if (msg.type === 'setUrl') {
    chrome.storage.local.set({ url: msg.url }).then(() => sendResponse({ ok: true }));
    return true;
  }
  if (msg.type === 'toggle') {
    _getState().then(async state => {
      const tasks = { ...state.tasks };
      const saved = tasks[msg.id] || {};
      saved.enabled = msg.enabled;
      tasks[msg.id] = saved;
      await chrome.storage.local.set({ tasks });
      if (msg.enabled) syncAll(true);
      sendResponse({ ok: true });
    });
    return true;
  }
  if (msg.type === 'clearLogs') {
    chrome.storage.local.set({ logs: [] }).then(() => sendResponse({ ok: true }));
    return true;
  }
  if (msg.type === 'sync') {
    _getState().then(state => {
      const tasks = _buildTasks(state);
      const task = tasks.find(t => t.id === msg.id);
      if (task) syncTask(task, true).then(sendResponse);
      else sendResponse({ ok: false, error: 'task disabled' });
    });
    return true;
  }
});
