/**
 * GitBook Downloader v7 — Desktop GUI Controller
 */

// ── State ─────────────────────────────────────────────────────────────
const state = {
  isCapturing: false,
  detectionData: null,
  currentDomain: null,
  activeTab: 'wizard',
  autoScrollLog: true,
  logLines: [],
};

// Helper: Format bytes
function formatSize(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Helper: Format count
function formatCount(n) {
  return (n || 0).toLocaleString();
}

// Helper: Notification toast
function showToast(msg, duration = 3000) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.remove('hidden');
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.classList.add('hidden');
  }, duration);
}

// ── DOM Ready & Tab Switching ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupWizard();
  setupLibrary();
  setupSearch();
  setupDiff();
  setupDiagnostics();
  setupTheme();

  // Polling check for pywebview bridge
  const checkBridge = setInterval(() => {
    if (window.pywebview && window.pywebview.api) {
      clearInterval(checkBridge);
      onBridgeReady();
    }
  }, 100);
});

function onBridgeReady() {
  loadLibrary();
  loadDiagnostics();
}

function setupTabs() {
  const navBtns = document.querySelectorAll('.nav-btn');
  navBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');
      switchTab(tabId);
    });
  });
}

function switchTab(tabId) {
  state.activeTab = tabId;
  document.querySelectorAll('.nav-btn').forEach((b) => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });
  document.querySelectorAll('.tab-pane').forEach((p) => {
    p.classList.toggle('active', p.id === `tab-${tabId}`);
  });

  if (tabId === 'library') loadLibrary();
  if (tabId === 'search') refreshSearchDomains();
  if (tabId === 'diff') refreshDiffDomains();
  if (tabId === 'diagnostics') loadDiagnostics();
}

function setupTheme() {
  const themeBtn = document.getElementById('theme-btn');
  themeBtn.addEventListener('click', () => {
    document.body.classList.toggle('light-theme');
  });
}

// ── TAB 1: CAPTURE STUDIO ──────────────────────────────────────────────
function setupWizard() {
  const urlInput = document.getElementById('url-input');
  const startBtn = document.getElementById('start-btn');
  const pasteBtn = document.getElementById('paste-btn');
  const cancelBtn = document.getElementById('cancel-btn');
  const clearLogBtn = document.getElementById('clear-log-btn');
  const copyLogBtn = document.getElementById('copy-log-btn');
  const autoScrollCheck = document.getElementById('autoscroll-check');
  const newCaptureBtn = document.getElementById('new-capture-btn');
  const openOutBtn = document.getElementById('open-out-btn');
  const viewLibBtn = document.getElementById('view-library-btn');

  // Enter to capture
  urlInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleStartCapture();
    }
  });

  // Paste button
  pasteBtn.addEventListener('click', async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        urlInput.value = text.trim();
        triggerDetection(text.trim());
      }
    } catch (err) {
      urlInput.focus();
      showToast('Right-click or press Ctrl+V to paste URL');
    }
  });

  urlInput.addEventListener('blur', () => {
    const val = urlInput.value.trim();
    if (val && !state.isCapturing) {
      triggerDetection(val);
    }
  });

  startBtn.addEventListener('click', () => handleStartCapture());
  cancelBtn.addEventListener('click', () => handleCancelCapture());

  autoScrollCheck.addEventListener('change', (e) => {
    state.autoScrollLog = e.target.checked;
  });

  clearLogBtn.addEventListener('click', () => {
    document.getElementById('terminal-body').innerHTML = '';
    state.logLines = [];
  });

  copyLogBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(state.logLines.join('\n'));
    showToast('Log copied to clipboard');
  });

  newCaptureBtn.addEventListener('click', () => {
    document.getElementById('summary-card').classList.add('hidden');
    document.getElementById('progress-card').classList.add('hidden');
    urlInput.value = '';
    urlInput.focus();
  });

  openOutBtn.addEventListener('click', () => {
    if (state.lastResult && state.lastResult.local_path) {
      window.pywebview.api.open_local_folder(state.lastResult.local_path);
    }
  });

  viewLibBtn.addEventListener('click', () => {
    switchTab('library');
  });
}

async function triggerDetection(url) {
  if (!url || !(url.startsWith('http://') || url.startsWith('https://'))) return;
  if (!window.pywebview || !window.pywebview.api) return;

  const banner = document.getElementById('detection-banner');
  const details = document.getElementById('detection-details');
  const text = document.getElementById('detection-text');
  const badge = document.getElementById('provider-badge');
  const evidence = document.getElementById('evidence-text');
  const versionsRegion = document.getElementById('versions-region');
  const versionsCheckboxes = document.getElementById('versions-checkboxes');

  banner.classList.remove('hidden');
  details.classList.add('hidden');
  text.textContent = 'Detecting provider…';

  try {
    const res = await window.pywebview.api.detect(url);
    if (res.success) {
      state.detectionData = res;
      text.textContent = 'Detected:';
      badge.textContent = res.provider.toUpperCase();
      evidence.textContent = res.evidence ? `— ${res.evidence}` : '';
      details.classList.remove('hidden');

      // Site versions
      if (res.site_versions && res.site_versions.length > 1) {
        versionsRegion.classList.remove('hidden');
        versionsCheckboxes.innerHTML = '';
        res.site_versions.forEach((v) => {
          const label = document.createElement('label');
          label.className = 'custom-checkbox';
          label.innerHTML = `
            <input type="checkbox" value="${v}" checked>
            <span class="checkmark"></span>
            ${v}
          `;
          versionsCheckboxes.appendChild(label);
        });
      } else {
        versionsRegion.classList.add('hidden');
      }
    } else {
      text.textContent = `Detection notice: ${res.error}`;
    }
  } catch (err) {
    text.textContent = 'Could not run provider detection.';
  }
}

async function handleStartCapture() {
  if (state.isCapturing) return;
  const url = document.getElementById('url-input').value.trim();
  if (!url || !(url.startsWith('http://') || url.startsWith('https://'))) {
    showToast('Please enter a valid http(s) URL first');
    return;
  }

  // Selected site versions
  const versionCbs = document.querySelectorAll('#versions-checkboxes input[type="checkbox"]');
  let selectedVersions = null;
  if (versionCbs.length > 0) {
    selectedVersions = Array.from(versionCbs).filter(cb => cb.checked).map(cb => cb.value);
  }

  const options = {
    path_scope: document.getElementById('scope-input').value.trim(),
    exclude_paths: document.getElementById('exclude-input').value.trim(),
    workers: parseInt(document.getElementById('workers-input').value) || 5,
    max_pages: document.getElementById('maxpages-input').value.trim() || null,
    snapshot: document.getElementById('snapshot-check').checked,
    site_versions: selectedVersions,
  };

  state.isCapturing = true;
  document.getElementById('start-btn').disabled = true;
  document.getElementById('url-input').disabled = true;
  document.getElementById('summary-card').classList.add('hidden');

  // Reset Progress UI & classes
  const progressCard = document.getElementById('progress-card');
  const circle = document.getElementById('gauge-bar');
  const number = document.getElementById('gauge-percent');
  const label = document.querySelector('.gauge-label');
  const heading = document.getElementById('progress-heading');
  const linearBar = document.getElementById('linear-progress-bar');
  const cancelBtn = document.getElementById('cancel-btn');

  circle.classList.remove('complete');
  number.classList.remove('complete');
  if (label) {
    label.classList.remove('complete');
    label.textContent = 'PROGRESS';
  }
  heading.classList.remove('complete');
  linearBar.classList.remove('complete');
  cancelBtn.classList.remove('hidden');

  progressCard.classList.remove('hidden');
  updateProgressGauge(0);
  linearBar.style.width = '0%';
  heading.textContent = 'Connecting to Documentation…';
  document.getElementById('progress-sub').textContent = url;
  document.getElementById('stat-discovered').textContent = '0';
  document.getElementById('stat-downloaded').textContent = '0';
  document.getElementById('stat-failed').textContent = '0';
  document.getElementById('stat-elapsed').textContent = '0.0s';

  addTerminalLog(`[START] Capturing: ${url}`, 'info');

  try {
    await window.pywebview.api.start_capture(url, options);
  } catch (err) {
    showToast(`Failed to start capture: ${err}`);
    state.isCapturing = false;
    document.getElementById('start-btn').disabled = false;
    document.getElementById('url-input').disabled = false;
  }
}

async function handleCancelCapture() {
  if (!state.isCapturing) return;
  addTerminalLog('[CANCEL] Cancelling active capture…', 'failed');
  try {
    await window.pywebview.api.cancel_capture();
  } catch (err) {
    // best-effort
  }
}

function updateProgressGauge(percent) {
  const circle = document.getElementById('gauge-bar');
  const number = document.getElementById('gauge-percent');
  const circumference = 264;
  const offset = circumference - (percent / 100) * circumference;
  circle.style.strokeDashoffset = offset;
  number.textContent = `${Math.round(percent)}%`;
}

function addTerminalLog(msg, type = 'info') {
  const terminal = document.getElementById('terminal-body');
  const line = document.createElement('div');
  line.className = `log-line ${type}`;
  const timeStr = new Date().toLocaleTimeString();
  line.textContent = `[${timeStr}] ${msg}`;
  terminal.appendChild(line);
  state.logLines.push(line.textContent);

  if (state.autoScrollLog) {
    terminal.scrollTop = terminal.scrollHeight;
  }
}

// Real-time Event Callback from Python
window.onCaptureProgress = function(data) {
  const { kind, url, title, count, done, total, elapsed } = data;

  if (total > 0) {
    const pct = Math.min(100, Math.round((done / total) * 100));
    updateProgressGauge(pct);
    document.getElementById('linear-progress-bar').style.width = `${pct}%`;
    document.getElementById('progress-heading').textContent = `Downloading Pages (${done}/${total})`;
  }

  document.getElementById('stat-discovered').textContent = formatCount(total);
  document.getElementById('stat-downloaded').textContent = formatCount(done);
  document.getElementById('stat-elapsed').textContent = `${elapsed}s`;

  if (kind === 'discovered') {
    addTerminalLog(`Discovered ${count} documentation URLs`, 'discovered');
  } else if (kind === 'downloaded') {
    const label = title ? `"${title}"` : url;
    addTerminalLog(`Downloaded: ${label}`, 'downloaded');
  } else if (kind === 'failed') {
    document.getElementById('stat-failed').textContent = formatCount(parseInt(document.getElementById('stat-failed').textContent || 0) + 1);
    addTerminalLog(`Failed: ${url} (${data.message || 'error'})`, 'failed');
  } else if (kind === 'written') {
    addTerminalLog('Writing output contract (page tree, book.md, llms.txt)…', 'written');
  }
};

window.onCaptureDone = function(data) {
  state.isCapturing = false;
  document.getElementById('start-btn').disabled = false;
  document.getElementById('url-input').disabled = false;
  document.getElementById('cancel-btn').classList.add('hidden');

  if (data.success && data.result) {
    state.lastResult = data.result;

    // Set 100% Green Completed UI
    const circle = document.getElementById('gauge-bar');
    const number = document.getElementById('gauge-percent');
    const label = document.querySelector('.gauge-label');
    const heading = document.getElementById('progress-heading');
    const sub = document.getElementById('progress-sub');
    const linearBar = document.getElementById('linear-progress-bar');

    circle.classList.add('complete');
    circle.style.strokeDashoffset = 0;
    number.classList.add('complete');
    number.textContent = '100%';
    if (label) {
      label.classList.add('complete');
      label.textContent = 'DONE';
    }

    heading.classList.add('complete');
    heading.textContent = `✅ Capture Complete (${data.result.pages_captured} Pages)`;
    sub.textContent = `All documentation pages downloaded, formatted into Markdown, and saved to Library.`;

    linearBar.classList.add('complete');
    linearBar.style.width = '100%';

    addTerminalLog(`[COMPLETE] Finished capture in ${data.result.duration_s}s! (${data.result.pages_captured} pages saved)`, 'downloaded');

    // Show Summary Card
    const summaryCard = document.getElementById('summary-card');
    summaryCard.classList.remove('hidden');
    document.getElementById('summary-title').textContent = `Captured ${data.result.pages_captured} Pages Successfully`;
    document.getElementById('summary-subtitle').textContent = `Provider: ${data.result.provider.toUpperCase()} · Duration: ${data.result.duration_s}s`;

    const details = document.getElementById('summary-details');
    details.innerHTML = `
      <div><strong>Local Output:</strong> ${data.result.local_path || 'N/A'}</div>
      <div><strong>Combined Book:</strong> ${data.result.book_file || 'N/A'}</div>
      <div><strong>Manifest:</strong> ${data.result.manifest_file || 'N/A'}</div>
      <div><strong>Snapshot Version:</strong> ${data.result.version_id || 'None (first capture)'}</div>
    `;

    // Immediately reload library in the background so it's fresh when clicking Library tab
    loadLibrary();
    refreshSearchDomains();
    refreshDiffDomains();

    showToast('Documentation capture complete & saved to Library!');
  } else {
    if (data.cancelled) {
      addTerminalLog('[STOP] Capture was cancelled by user.', 'failed');
      showToast('Capture cancelled.');
    } else {
      addTerminalLog(`[ERROR] Capture failed: ${data.error}`, 'failed');
      showToast(`Capture failed: ${data.error}`, 4000);
    }
  }
};

// ── TAB 2: LIBRARY ─────────────────────────────────────────────────────
function setupLibrary() {
  document.getElementById('refresh-lib-btn').addEventListener('click', () => loadLibrary());
  document.getElementById('close-viewer-btn').addEventListener('click', () => {
    document.getElementById('doc-viewer-modal').classList.add('hidden');
  });
}

async function loadLibrary() {
  if (!window.pywebview || !window.pywebview.api) return;
  try {
    const list = await window.pywebview.api.list_library();
    const tbody = document.getElementById('library-tbody');
    const empty = document.getElementById('library-empty');
    tbody.innerHTML = '';

    if (!list || list.length === 0) {
      empty.classList.remove('hidden');
      return;
    }
    empty.classList.add('hidden');

    list.forEach((doc) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${doc.domain}</strong></td>
        <td><span class="badge-pill">${(doc.provider || 'GENERIC').toUpperCase()}</span></td>
        <td>${formatCount(doc.pages)}</td>
        <td>${formatSize(doc.size_bytes)}</td>
        <td>${doc.snapshot_count}</td>
        <td class="mono">${(doc.last_crawled || '').slice(0, 10)}</td>
        <td>
          <div class="table-actions">
            <button class="btn-mini" onclick="openDocViewer('${doc.domain}')">Read</button>
            <button class="btn-mini" onclick="openFolder('${doc.domain}')">Folder</button>
            <button class="btn-mini" onclick="recrawlDoc('${doc.url || doc.domain}')">Re-crawl</button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Error loading library:', err);
  }
}

window.openDocViewer = async function(domain) {
  state.currentDomain = domain;
  const modal = document.getElementById('doc-viewer-modal');
  const title = document.getElementById('doc-viewer-title');
  const pagesTree = document.getElementById('doc-pages-tree');
  const contentPre = document.getElementById('doc-markdown-content');

  title.textContent = `Documentation: ${domain}`;
  modal.classList.remove('hidden');
  pagesTree.innerHTML = '<li>Loading pages…</li>';
  contentPre.textContent = 'Select a page from the sidebar to read.';

  try {
    const docData = await window.pywebview.api.get_library_doc(domain);
    if (docData.success) {
      pagesTree.innerHTML = '';
      
      // Add Book.md option
      const bookLi = document.createElement('li');
      bookLi.textContent = '📖 book.md (All Pages)';
      bookLi.classList.add('active');
      bookLi.addEventListener('click', () => {
        document.querySelectorAll('#doc-pages-tree li').forEach(l => l.classList.remove('active'));
        bookLi.classList.add('active');
        contentPre.textContent = docData.book_content;
      });
      pagesTree.appendChild(bookLi);
      contentPre.textContent = docData.book_content;

      // Add individual pages
      docData.pages.forEach((p) => {
        const li = document.createElement('li');
        li.textContent = `📄 ${p.relpath}`;
        li.addEventListener('click', async () => {
          document.querySelectorAll('#doc-pages-tree li').forEach(l => l.classList.remove('active'));
          li.classList.add('active');
          const fileRes = await window.pywebview.api.read_file(p.path);
          if (fileRes.success) {
            contentPre.textContent = fileRes.content;
          }
        });
        pagesTree.appendChild(li);
      });
    }
  } catch (err) {
    contentPre.textContent = `Error loading document: ${err}`;
  }
};

window.openFolder = function(target) {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.open_local_folder(target);
  }
};

window.recrawlDoc = function(url) {
  switchTab('wizard');
  const input = document.getElementById('url-input');
  input.value = url.startsWith('http') ? url : `https://${url}`;
  triggerDetection(input.value);
};

// ── TAB 3: SEARCH ──────────────────────────────────────────────────────
function setupSearch() {
  const searchInput = document.getElementById('search-query-input');
  const searchBtn = document.getElementById('search-btn');

  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') executeSearch();
  });
  searchBtn.addEventListener('click', () => executeSearch());
}

async function refreshSearchDomains() {
  if (!window.pywebview || !window.pywebview.api) return;
  const select = document.getElementById('search-domain-select');
  const current = select.value;
  try {
    const list = await window.pywebview.api.list_library();
    select.innerHTML = '<option value="all">All Domains</option>';
    list.forEach((doc) => {
      const opt = document.createElement('option');
      opt.value = doc.domain;
      opt.textContent = doc.domain;
      select.appendChild(opt);
    });
    if (current) select.value = current;
  } catch (err) {}
}

async function executeSearch() {
  const query = document.getElementById('search-query-input').value.trim();
  const domain = document.getElementById('search-domain-select').value;
  const resultsInfo = document.getElementById('search-results-info');
  const listContainer = document.getElementById('search-results-list');

  if (!query) {
    listContainer.innerHTML = '<div class="empty-state">Type a query above to search.</div>';
    return;
  }

  resultsInfo.textContent = 'Searching…';
  listContainer.innerHTML = '';

  try {
    const hits = await window.pywebview.api.search_docs(query, domain);
    resultsInfo.textContent = `Found ${hits.length} matches for "${query}"`;

    if (hits.length === 0) {
      listContainer.innerHTML = '<div class="empty-state">No matching documentation pages found.</div>';
      return;
    }

    hits.forEach((h) => {
      const card = document.createElement('div');
      card.className = 'search-hit-card';
      // Highlight query keyword in snippet safely
      const safeSnippet = h.snippet.replace(/\[\.\.\.\]/g, ' … ');
      card.innerHTML = `
        <div class="hit-title">${h.title || h.url}</div>
        <div class="hit-snippet">${safeSnippet}</div>
        <div class="hit-meta">${h.domain} ${h.section_heading ? '· ' + h.section_heading : ''} · Score: ${h.rank}</div>
      `;
      card.addEventListener('click', () => {
        openDocViewer(h.domain);
      });
      listContainer.appendChild(card);
    });
  } catch (err) {
    resultsInfo.textContent = `Search failed: ${err}`;
  }
}

// ── TAB 4: SNAPSHOT DIFF ───────────────────────────────────────────────
function setupDiff() {
  const domainSel = document.getElementById('diff-domain-select');
  const compareBtn = document.getElementById('diff-compare-btn');

  domainSel.addEventListener('change', async (e) => {
    const domain = e.target.value;
    if (!domain) return;
    try {
      const snapshots = await window.pywebview.api.list_snapshots(domain);
      const oldSel = document.getElementById('diff-old-select');
      const newSel = document.getElementById('diff-new-select');
      oldSel.innerHTML = '';
      newSel.innerHTML = '';

      snapshots.forEach((s, idx) => {
        const label = `${s.version_id} (${s.created_at.slice(0, 10)}) - ${s.pages}p`;
        oldSel.appendChild(new Option(label, s.version_id));
        newSel.appendChild(new Option(label, s.version_id));
      });

      if (snapshots.length >= 2) {
        newSel.selectedIndex = 0;
        oldSel.selectedIndex = 1;
      }
    } catch (err) {}
  });

  compareBtn.addEventListener('click', async () => {
    const domain = document.getElementById('diff-domain-select').value;
    const oldV = document.getElementById('diff-old-select').value;
    const newV = document.getElementById('diff-new-select').value;
    const container = document.getElementById('diff-output-container');
    const summaryRow = document.getElementById('diff-summary-row');

    if (!domain || !oldV || !newV) {
      showToast('Select a domain and two snapshot versions to compare');
      return;
    }

    container.innerHTML = 'Computing diff…';

    try {
      const res = await window.pywebview.api.diff_snapshots(domain, oldV, newV);
      if (res.success) {
        summaryRow.classList.remove('hidden');
        summaryRow.innerHTML = `
          <span><strong>Added:</strong> +${res.pages_added} pages (+${res.lines_added} lines)</span>
          <span><strong>Removed:</strong> -${res.pages_removed} pages (-${res.lines_removed} lines)</span>
          <span><strong>Changed:</strong> ~${res.pages_changed} pages</span>
        `;

        container.innerHTML = '';
        if (res.changes.length === 0) {
          container.innerHTML = '<div class="empty-state">No changes between selected snapshots.</div>';
          return;
        }

        res.changes.forEach((c) => {
          const block = document.createElement('div');
          block.className = 'glass-card';
          block.style.marginBottom = '12px';
          block.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 6px;">[${c.status.toUpperCase()}] ${c.url}</div>
            <pre class="markdown-preview mono" style="font-size: 12px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px;">${c.diff_text || 'Binary or metadata change'}</pre>
          `;
          container.appendChild(block);
        });
      }
    } catch (err) {
      container.innerHTML = `Diff error: ${err}`;
    }
  });
}

async function refreshDiffDomains() {
  if (!window.pywebview || !window.pywebview.api) return;
  const select = document.getElementById('diff-domain-select');
  try {
    const list = await window.pywebview.api.list_library();
    select.innerHTML = '<option value="">Select domain...</option>';
    list.forEach((doc) => {
      select.appendChild(new Option(doc.domain, doc.domain));
    });
  } catch (err) {}
}

// ── TAB 5: DIAGNOSTICS ─────────────────────────────────────────────────
function setupDiagnostics() {}

async function loadDiagnostics() {
  if (!window.pywebview || !window.pywebview.api) return;
  try {
    const diag = await window.pywebview.api.get_diagnostics();
    const sysInfo = await window.pywebview.api.get_system_info();

    if (diag && diag.url) {
      document.getElementById('diag-provider-info').textContent =
        `Target URL:  ${diag.url}\n` +
        `Provider:    ${(diag.provider || 'generic').toUpperCase()}\n` +
        `Status:      ${diag.cancelled ? 'Cancelled' : (diag.error ? 'Error' : 'Complete')}`;

      document.getElementById('diag-metrics-info').textContent =
        `Duration:    ${diag.duration_s || 0}s\n` +
        `Captured:    ${diag.pages_captured || 0} pages\n` +
        `Skipped:     ${diag.skipped || 0} pages\n` +
        `Discovered:  ${diag.stats?.discovered || 0} URLs`;

      document.getElementById('diag-scoping-info').textContent =
        `Local Path:  ${diag.local_path || 'N/A'}\n` +
        `Book File:   ${diag.book_file || 'N/A'}\n` +
        `Snapshot ID: ${diag.version_id || 'None'}`;
    }

    if (sysInfo) {
      document.getElementById('diag-system-info').textContent =
        `App Version:  v${sysInfo.version}\n` +
        `Python:       ${sysInfo.python}\n` +
        `Platform:     ${sysInfo.platform}\n` +
        `Library:      ${sysInfo.library_dir}\n` +
        `Working Dir:  ${sysInfo.cwd}`;
    }
  } catch (err) {}
}
