/**
 * annotation-overlay.js — vanilla DOM annotation overlay
 * v0.1.0 — no framework, no build step
 *
 * Loaded as the last <script type="module"> in every walkthrough page.
 * Two modes (auto-detected):
 *   iframe      → postMessage to parent (forge-concept context)
 *   standalone  → floating toolbar with "Download annotations" button
 *
 * postMessage protocol (from docs/superpowers/notes/forge-concept-walkthrough.md):
 *   overlay→parent: { type: "overlay.ready",      route, manifest?: undefined }
 *     (manifest omitted in v0.1 — requires runtime fetch of manifest.json; TODO Task 3A+)
 *   overlay→parent: { type: "overlay.annotation",  annotation }
 *   overlay→parent: { type: "overlay.navigate",    route }
 *   parent→overlay: { type: "parent.setMode",      mode: "view"|"annotate" }
 *   parent→overlay: { type: "parent.replay",       annotations: Annotation[] }
 */

// ── Session ──────────────────────────────────────────────────────────────────

const SESSION_KEY = 'overlay-session-id';

function initSessionId() {
  let sid = sessionStorage.getItem(SESSION_KEY);
  if (!sid) {
    sid = typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : Date.now().toString(36) + '-' + Math.random().toString(36).slice(2);
    sessionStorage.setItem(SESSION_KEY, sid);
  }
  return sid;
}

const SESSION_ID = initSessionId();
const annotations = [];

// ── Mode detection ────────────────────────────────────────────────────────────

const IS_IFRAME = (() => {
  try { return window !== window.parent; } catch (_) { return true; }
})();

// ── HTML escape helper ────────────────────────────────────────────────────────

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Spec-ref resolution ───────────────────────────────────────────────────────

/**
 * Walk up from `el` to find the nearest data-spec-element.
 * Returns null if the click was outside any annotatable node.
 *
 * @param {Element} el
 * @returns {{ element: string, screen: string|null, journey: string|null, route: string, provisional: boolean }|null}
 */
function resolveTarget(el) {
  let node = el;
  while (node && node !== document.documentElement) {
    if (node.dataset && node.dataset.specElement) {
      return {
        element:     node.dataset.specElement,
        screen:      document.body.dataset.specScreen  || null,
        journey:     document.body.dataset.specJourney || null,
        route:       location.pathname,
        provisional: node.dataset.specProvisional === 'true',
      };
    }
    node = node.parentElement;
  }
  return null;
}

// TODO: also capture data-spec-feature (from node ancestor) and
// data-spec-route attribute (canonical walkthrough route vs location.pathname).
// Deferred to Task 3B design — downstream patch mapper needs feature field.

// ── Popover ───────────────────────────────────────────────────────────────────

let activePopover = null;
let outsideClickHandler = null;
let escapeHandler = null;

function closePopover() {
  if (outsideClickHandler) {
    document.removeEventListener('mousedown', outsideClickHandler, true);
    outsideClickHandler = null;
  }
  if (escapeHandler) {
    document.removeEventListener('keydown', escapeHandler);
    escapeHandler = null;
  }
  if (activePopover) { activePopover.remove(); activePopover = null; }
}

const POPOVER_STYLE = [
  'position:fixed', 'z-index:2147483647', 'background:#fff',
  'border:1px solid #e2e8f0', 'border-radius:8px', 'padding:16px',
  'box-shadow:0 8px 24px rgba(0,0,0,0.18)', 'min-width:280px',
  'font-family:system-ui,sans-serif', 'font-size:14px', 'line-height:1.5',
  'top:50%', 'left:50%', 'transform:translate(-50%,-50%)',
].join(';');

const CATEGORIES = ['change', 'add', 'remove', 'question'];

function showPopover(specRef) {
  closePopover();
  const div = document.createElement('div');
  div.setAttribute('style', POPOVER_STYLE);
  const provisionalBanner = specRef.provisional
    ? `<p style="margin:0 0 8px;padding:6px 8px;background:#fef3c7;border-radius:4px;font-size:12px;color:#92400e;">⚠ Provisional ID — will be promoted on first annotation</p>`
    : '';
  div.innerHTML = `
<div style="font-weight:600;margin-bottom:10px;">Annotate: <code style="background:#f1f5f9;padding:2px 4px;border-radius:3px">${escHtml(specRef.element)}</code></div>
${provisionalBanner}
<select id="ov-cat" style="width:100%;padding:5px;margin-bottom:8px;border:1px solid #cbd5e1;border-radius:4px">
  ${CATEGORIES.map(c => `<option value="${c}">${c[0].toUpperCase() + c.slice(1)}</option>`).join('')}
</select>
<textarea id="ov-body" rows="3" placeholder="Describe the issue or request…"
  style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;resize:vertical;margin-bottom:10px"></textarea>
<div style="display:flex;gap:8px">
  <button id="ov-submit" style="padding:5px 14px;background:#0ea5e9;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:14px">Submit</button>
  <button id="ov-cancel" style="padding:5px 14px;background:#f8fafc;border:1px solid #cbd5e1;border-radius:4px;cursor:pointer;font-size:14px">Cancel</button>
</div>`;
  document.body.appendChild(div);
  outsideClickHandler = (e) => {
    if (activePopover && !activePopover.contains(e.target)) closePopover();
  };
  setTimeout(() => document.addEventListener('mousedown', outsideClickHandler, true), 0);
  escapeHandler = (e) => { if (e.key === 'Escape') closePopover(); };
  document.addEventListener('keydown', escapeHandler);
  activePopover = div;
  div.querySelector('#ov-body').focus();
  div.querySelector('#ov-body').addEventListener('input', (e) => {
    e.target.style.borderColor = '#cbd5e1';
  });
  div.querySelector('#ov-cancel').addEventListener('click', closePopover);
  div.querySelector('#ov-submit').addEventListener('click', () => {
    const body = div.querySelector('#ov-body').value.trim();
    if (!body) { div.querySelector('#ov-body').style.borderColor = '#ef4444'; return; }
    const category = div.querySelector('#ov-cat').value;
    submitAnnotation({ specRef, body, category });
    closePopover();
  });
}

// ── Annotation submission ─────────────────────────────────────────────────────

function makeId() {
  return Date.now().toString(36) + '-' + Math.random().toString(36).slice(2);
}
// Returns base-36 timestamp+random. Will be replaced by ULID when
// annotation-overlay is extracted to @skaile/annotation-overlay (catalog § row 7).

function submitAnnotation({ specRef, body, category }) {
  const annotation = {
    id:        makeId(),
    sessionId: SESSION_ID,
    createdAt: new Date().toISOString(),
    specRef,
    body,
    category,
    status:    'open',
  };
  annotations.push(annotation);
  if (IS_IFRAME) {
    window.parent.postMessage({ type: 'overlay.annotation', annotation }, '*');
  } else {
    refreshDownloadButton();
  }
}

// ── Click interception ────────────────────────────────────────────────────────

let annotateMode = false;

function setMode(mode) {
  annotateMode = mode === 'annotate';
  document.body.style.cursor = annotateMode ? 'crosshair' : '';
}

document.addEventListener('click', (e) => {
  if (!annotateMode) return;
  const ref = resolveTarget(e.target);
  if (!ref) return;
  e.preventDefault();
  e.stopPropagation();
  showPopover(ref);
}, true);

// ── Navigation interception (iframe only) ─────────────────────────────────────

if (IS_IFRAME) {
  document.addEventListener('click', (e) => {
    const anchor = e.target.closest('a[href]');
    if (!anchor || annotateMode) return;
    const href = anchor.getAttribute('href');
    if (href && !href.startsWith('http') && !href.startsWith('//') &&
        !href.startsWith('mailto:') && !href.startsWith('tel:') &&
        !href.startsWith('#') && !href.startsWith('javascript:')) {
      e.preventDefault();
      window.parent.postMessage({ type: 'overlay.navigate', route: href }, '*');
    }
  });
}

// ── Standalone toolbar ────────────────────────────────────────────────────────

let downloadBtn = null;

function refreshDownloadButton() {
  if (downloadBtn) downloadBtn.textContent = `Download (${annotations.length})`;
}

if (!IS_IFRAME) {
  const bar = document.createElement('div');
  bar.setAttribute('style', [
    'position:fixed', 'bottom:16px', 'right:16px', 'z-index:2147483646',
    'display:flex', 'gap:10px', 'align-items:center',
    'background:#1e293b', 'color:#fff', 'padding:10px 14px',
    'border-radius:8px', 'font-family:system-ui,sans-serif', 'font-size:13px',
  ].join(';'));
  bar.innerHTML = `
<label style="display:flex;align-items:center;gap:6px;cursor:pointer;user-select:none">
  <input type="checkbox" id="ov-toggle"> Annotate
</label>
<button id="ov-dl" style="padding:4px 12px;background:#0ea5e9;color:#fff;border:none;border-radius:4px;cursor:pointer">
  Download (0)
</button>`;
  document.body.appendChild(bar);
  downloadBtn = bar.querySelector('#ov-dl');
  bar.querySelector('#ov-toggle').addEventListener('change', (e) => {
    setMode(e.target.checked ? 'annotate' : 'view');
  });
  downloadBtn.addEventListener('click', () => {
    if (!annotations.length) return;
    const payload = JSON.stringify({ sessionId: SESSION_ID, annotations }, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `annotations-${SESSION_ID.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  });
}

// ── Parent ↔ overlay message bus ──────────────────────────────────────────────

window.addEventListener('message', (e) => {
  const msg = e.data;
  if (!msg || typeof msg.type !== 'string') return;
  if (msg.type === 'parent.setMode')  setMode(msg.mode);
  if (msg.type === 'parent.replay')   console.debug('[overlay] replay', msg.annotations?.length ?? 0);
});

// ── Ready signal ──────────────────────────────────────────────────────────────

if (IS_IFRAME) {
  window.parent.postMessage({ type: 'overlay.ready', route: location.pathname }, '*');
}
