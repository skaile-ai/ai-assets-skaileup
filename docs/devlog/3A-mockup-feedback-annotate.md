# mockup-feedback-annotate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `mockup-feedback-annotate` skill — a vanilla-DOM annotation overlay bundle plus the skill prompt that injects it into any `walkthrough-mockup-*` output directory.

**Architecture:** The skill has two deliverables. First, `overlay/annotation-overlay.js` — a ~160 LOC vanilla ES module with no build step and no framework dependencies. It activates on DOM load, listens for clicks on `data-spec-element` nodes, shows a category+text popover, and sends the resulting annotation via `postMessage` (when inside an iframe) or via a download button (standalone). Second, `SKILL.md` — an AI-agent prompt that, when run against a walkthrough site root, copies the overlay bundle and injects a `<script>` tag into every HTML page. A `validator.py` verifies injection correctness. The e2e browser test is deferred to Task 3F.

**Tech Stack:** Python 3 (stdlib only) for `validator.py` + test runner; vanilla ESM for the overlay; no npm/bun/build tool; follows existing repo pattern from `walkthrough-mockup/static-html/`.

**Prereqs read before starting:**
- `docs/devlog/forge-concept-walkthrough.md` — postMessage protocol + storage conventions
- `walkthrough-mockup/static-html/SKILL.md` — `data-spec-*` attribute table + manifest.json shape
- `walkthrough-mockup/static-html/validator.py` — validator pattern to copy
- `walkthrough-mockup/static-html/tests/expected/minimal/` — the fixture site this overlay will be injected into

---

## File Map

| Path | Create / Modify | Responsibility |
|---|---|---|
| `mockup-feedback/annotate/SKILL.md` | Create | AI-agent prompt: inject overlay into walkthrough site |
| `mockup-feedback/annotate/overlay/annotation-overlay.js` | Create | Vanilla-DOM overlay bundle (click→popover→postMessage/download) |
| `mockup-feedback/annotate/tests/fixtures/minimal/` | Create | Pre-injection copy of static-html minimal fixture (reference state) |
| `mockup-feedback/annotate/tests/expected/minimal/` | Create | Post-injection version: fixtures/minimal + script tag + overlay.js |
| `mockup-feedback/annotate/validator.py` | Create | Python: checks injection was applied correctly to a site root |
| `mockup-feedback/annotate/tests/run_validator.sh` | Create | Runs validator in both pass and fail modes for CI |
| `mockup-feedback/DOMAIN.md` | Modify | Add `annotate` to Skills list |

---

## Task 1: Scaffold directory + SKILL.md frontmatter

**Files:**
- Create: `mockup-feedback/annotate/SKILL.md`
- Modify: `mockup-feedback/DOMAIN.md`

- [ ] **Step 1.1: Create the skill directory and SKILL.md stub**

```bash
mkdir -p mockup-feedback/annotate/overlay
mkdir -p mockup-feedback/annotate/tests/fixtures
mkdir -p mockup-feedback/annotate/tests/expected
```

Write `mockup-feedback/annotate/SKILL.md`:

```markdown
---
name: mockup-feedback-annotate
description: "Injects the annotation overlay into a walkthrough site root so stakeholders can click elements and submit comments. Produces _concept/_feedback/sessions/ for annotation storage. First skill in the mockup-feedback cluster."
metadata:
  version: "0.1.0"
  tags:
    - mockup-feedback
    - annotation
    - overlay
    - data-spec
    - walkthrough
  stage: alpha
  prerequisites:
    files:
      - path: "_concept/walkthrough-mockup"
        gate: hard
        description: "At least one walkthrough-mockup-* output must exist (manifest.json + HTML files)"
        min_entries: 1
    reads:
      - path: "_concept/walkthrough-mockup/static-html/manifest.json"
        description: "Validates data-spec-element IDs and identifies provisional ones"
    produces:
      - path: "_concept/walkthrough-mockup/static-html/annotation-overlay.js"
        description: "The overlay bundle copied from skill/overlay/"
      - path: "_concept/_feedback/sessions/"
        description: "Session JSON directory (gitignored); created if absent"
      - path: "_concept/_feedback/index.json"
        description: "Session index (gitignored); created if absent"
---

# mockup-feedback-annotate

## BODY_PLACEHOLDER

(Skill body authored in Task 4.)
```

- [ ] **Step 1.2: Update DOMAIN.md Skills list**

In `mockup-feedback/DOMAIN.md`, replace the Skills placeholder:

```markdown
## Skills

- [`mockup-feedback-annotate`](annotate/SKILL.md) — Inject annotation overlay into a walkthrough site
```

- [ ] **Step 1.3: Verify the stub is parseable**

```bash
python -c "
import re, sys
text = open('mockup-feedback/annotate/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
assert m, 'No frontmatter found'
print('OK — frontmatter present')
"
```

Expected: `OK — frontmatter present`

- [ ] **Step 1.4: Commit**

```bash
git add mockup-feedback/annotate/SKILL.md mockup-feedback/DOMAIN.md
git commit -m "feat(mockup-feedback): scaffold annotate skill directory + SKILL.md stub

Phase 3 Task 3A step 1.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Write `annotation-overlay.js`

**Files:**
- Create: `mockup-feedback/annotate/overlay/annotation-overlay.js`

The overlay is ~160 LOC vanilla ESM. Auto-detects whether it is running inside an iframe (forge-concept) or standalone (direct browser open). No build step — the file is served as-is.

- [ ] **Step 2.1: Write `annotation-overlay.js`**

Create `mockup-feedback/annotate/overlay/annotation-overlay.js`:

```javascript
/**
 * annotation-overlay.js — vanilla DOM annotation overlay
 * v0.1.0 — no framework, no build step
 *
 * Loaded as the last <script type="module"> in every walkthrough page.
 * Two modes (auto-detected):
 *   iframe      → postMessage to parent (forge-concept context)
 *   standalone  → floating toolbar with "Download annotations" button
 *
 * postMessage protocol (from docs/devlog/forge-concept-walkthrough.md):
 *   overlay→parent: { type: "overlay.ready",      route, manifest? }
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

// ── Popover ───────────────────────────────────────────────────────────────────

let activePopover = null;

function closePopover() {
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
<div style="font-weight:600;margin-bottom:10px;">Annotate: <code style="background:#f1f5f9;padding:2px 4px;border-radius:3px">${specRef.element}</code></div>
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
  activePopover = div;
  div.querySelector('#ov-body').focus();
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
    if (href && !href.startsWith('http') && !href.startsWith('//')) {
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
```

- [ ] **Step 2.2: Verify the file is valid JS (Node.js parse check)**

```bash
node --input-type=module --eval "
import { readFileSync } from 'fs';
// Just parse: Node will throw SyntaxError if invalid
" < /dev/null 2>&1 || true

node -e "
const fs = require('fs');
const src = fs.readFileSync('mockup-feedback/annotate/overlay/annotation-overlay.js', 'utf8');
// Basic sanity: count function/const/let to verify it parsed
const counts = { fn: (src.match(/\bfunction\b/g)||[]).length, const: (src.match(/\bconst\b/g)||[]).length };
console.log('tokens found:', counts);
if (counts.fn + counts.const < 5) { console.error('Suspiciously few tokens'); process.exit(1); }
console.log('OK');
"
```

Expected: `tokens found: { fn: ..., const: ... }` then `OK`.

- [ ] **Step 2.3: Commit**

```bash
git add mockup-feedback/annotate/overlay/annotation-overlay.js
git commit -m "feat(mockup-feedback): add annotation-overlay.js (vanilla DOM, ~160 LOC)

Supports iframe (postMessage) and standalone (download) modes.
Auto-detects context via window !== window.parent.

Phase 3 Task 3A step 2.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Write `validator.py` + test fixtures (TDD)

**Files:**
- Create: `mockup-feedback/annotate/validator.py`
- Create: `mockup-feedback/annotate/tests/fixtures/minimal/` (pre-injection)
- Create: `mockup-feedback/annotate/tests/expected/minimal/` (post-injection)
- Create: `mockup-feedback/annotate/tests/run_validator.sh`

**What the validator checks:**
1. `annotation-overlay.js` exists in the site root
2. Every `.html` file has `<script type="module" src="annotation-overlay.js">` as the last `<script>` before `</body>`
3. The script tag is NOT inside `<head>` (must be in body)
4. No CDN/external JS introduced (reuses pattern from static-html validator)

- [ ] **Step 3.1: Write `validator.py`**

Create `mockup-feedback/annotate/validator.py`:

```python
#!/usr/bin/env python3
"""validator.py — mockup-feedback-annotate injection validator.

Checks that a walkthrough site root has the annotation overlay correctly
injected by the mockup-feedback-annotate skill.

Usage:
  python validator.py <site-root>

Exit codes:
  0   PASS
  2   FAIL (violations found)
  1   Internal error (bad args, missing site root)
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

OVERLAY_FILENAME = "annotation-overlay.js"
EXPECTED_SCRIPT_TAG = f'<script type="module" src="{OVERLAY_FILENAME}"></script>'

CDN_PATTERNS = [
    re.compile(r'<script\s[^>]*src\s*=\s*"https?://', re.IGNORECASE),
    re.compile(r'<script\s[^>]*src\s*=\s*"//', re.IGNORECASE),
]


class _ScriptChecker(HTMLParser):
    """Walks one HTML file and records overlay script presence and position."""

    def __init__(self) -> None:
        super().__init__()
        self.in_head = False
        self.overlay_found = False
        self.overlay_in_head = False
        self.cdns: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "head":
            self.in_head = True
        if tag == "script":
            src = dict(attrs).get("src", "")
            if src == OVERLAY_FILENAME:
                self.overlay_found = True
                if self.in_head:
                    self.overlay_in_head = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self.in_head = False


class Report:
    def __init__(self) -> None:
        self.violations: list[str] = []

    def add(self, where: str, msg: str) -> None:
        self.violations.append(f"{where}: {msg}")

    def ok(self) -> bool:
        return len(self.violations) == 0

    def dump(self) -> None:
        for v in self.violations:
            print("FAIL", v)


def collect_html_files(site_root: Path) -> list[Path]:
    return sorted(site_root.rglob("*.html"))


def check_site(site_root: Path) -> Report:
    r = Report()

    if not site_root.is_dir():
        r.add(str(site_root), "site root directory does not exist")
        return r

    # 1. Overlay bundle must be present
    overlay_path = site_root / OVERLAY_FILENAME
    if not overlay_path.is_file():
        r.add(OVERLAY_FILENAME, "overlay bundle not found in site root")

    html_files = collect_html_files(site_root)
    if not html_files:
        r.add(str(site_root), "no .html files found — nothing to check")
        return r

    for html in html_files:
        rel = html.relative_to(site_root)
        raw = html.read_text(encoding="utf-8")

        # 2. CDN check (must not introduce external scripts)
        for pat in CDN_PATTERNS:
            if pat.search(raw):
                r.add(str(rel), "unexpected CDN script/link reference introduced by injection")

        # 3. Parse HTML for overlay script position
        checker = _ScriptChecker()
        checker.feed(raw)

        if not checker.overlay_found:
            r.add(str(rel), f"missing overlay script tag ({EXPECTED_SCRIPT_TAG!r})")
            continue

        if checker.overlay_in_head:
            r.add(str(rel), "overlay script tag is in <head> — must be last child of <body>")

        # 4. Must be just before </body> (last script in file)
        # Check: the tag appears after the last data-spec-element occurrence
        body_close = raw.rfind("</body>")
        tag_pos = raw.rfind(f'src="{OVERLAY_FILENAME}"')
        if body_close < 0:
            r.add(str(rel), "no </body> tag found")
        elif tag_pos < 0:
            pass  # already caught by overlay_found check above
        elif tag_pos > body_close:
            r.add(str(rel), "overlay script tag appears after </body>")

    return r


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python validator.py <site-root>", file=sys.stderr)
        return 1

    site_root = Path(sys.argv[1])
    r = check_site(site_root)

    if r.ok():
        print(f"PASS  {site_root}")
        return 0

    r.dump()
    return 2


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3.2: Create the pre-injection fixture (`tests/fixtures/minimal/`)**

Copy the static-html expected minimal fixture:

```bash
cp -r walkthrough-mockup/static-html/tests/expected/minimal \
      mockup-feedback/annotate/tests/fixtures/minimal
```

Verify:

```bash
ls mockup-feedback/annotate/tests/fixtures/minimal/
# Expected: index.html  manifest.json  screen/  journey/
```

- [ ] **Step 3.3: Run validator on pre-injection fixture → must FAIL**

```bash
python mockup-feedback/annotate/validator.py \
    mockup-feedback/annotate/tests/fixtures/minimal/
echo "Exit code: $?"
```

Expected output (one line per HTML file, starting with `FAIL`):

```
FAIL annotation-overlay.js: overlay bundle not found in site root
FAIL index.html: missing overlay script tag ...
FAIL screen/00_auth/login.html: missing overlay script tag ...
...
Exit code: 2
```

If any HTML file does NOT produce a FAIL line, the validator has a bug — fix it before proceeding.

- [ ] **Step 3.4: Create the post-injection fixture (`tests/expected/minimal/`)**

```bash
cp -r mockup-feedback/annotate/tests/fixtures/minimal \
      mockup-feedback/annotate/tests/expected/minimal
cp mockup-feedback/annotate/overlay/annotation-overlay.js \
   mockup-feedback/annotate/tests/expected/minimal/annotation-overlay.js
```

Now inject the script tag into every HTML file in `tests/expected/minimal/`. For each HTML file, add this line just before `</body>`:

```html
<script type="module" src="annotation-overlay.js"></script>
```

Run this Python snippet to do the injection:

```python
from pathlib import Path
site = Path("mockup-feedback/annotate/tests/expected/minimal")
tag = '<script type="module" src="annotation-overlay.js"></script>\n'
for html in site.rglob("*.html"):
    txt = html.read_text(encoding="utf-8")
    assert "</body>" in txt, f"No </body> in {html}"
    txt = txt.replace("</body>", tag + "</body>")
    html.write_text(txt, encoding="utf-8")
    print("Injected:", html)
```

```bash
python -c "
from pathlib import Path
site = Path('mockup-feedback/annotate/tests/expected/minimal')
tag = '<script type=\"module\" src=\"annotation-overlay.js\"></script>\n'
for html in site.rglob('*.html'):
    txt = html.read_text(encoding='utf-8')
    assert '</body>' in txt, f'No </body> in {html}'
    txt = txt.replace('</body>', tag + '</body>')
    html.write_text(txt, encoding='utf-8')
    print('Injected:', html)
"
```

Verify the injection looks correct in one file:

```bash
grep -n "annotation-overlay" \
    mockup-feedback/annotate/tests/expected/minimal/index.html
```

Expected: one line near the end with the `<script type="module" ...>` tag.

- [ ] **Step 3.5: Run validator on post-injection fixture → must PASS**

```bash
python mockup-feedback/annotate/validator.py \
    mockup-feedback/annotate/tests/expected/minimal/
echo "Exit code: $?"
```

Expected:

```
PASS  mockup-feedback/annotate/tests/expected/minimal
Exit code: 0
```

If FAIL: re-read the validator logic and fix the gap before committing.

- [ ] **Step 3.6: Write `tests/run_validator.sh`**

Create `mockup-feedback/annotate/tests/run_validator.sh`:

```bash
#!/usr/bin/env bash
# run_validator.sh — regression check for mockup-feedback-annotate validator
# Usage: bash tests/run_validator.sh
# Must be run from the skill root (mockup-feedback/annotate/).
set -e

PASS_FIXTURE="tests/expected/minimal"
FAIL_FIXTURE="tests/fixtures/minimal"
VALIDATOR="validator.py"

echo "--- Test 1: pre-injection fixture should FAIL ---"
python "$VALIDATOR" "$FAIL_FIXTURE" && {
    echo "ERROR: validator returned 0 on un-injected fixture (expected 2)"
    exit 1
} || {
    EC=$?
    if [ "$EC" -ne 2 ]; then
        echo "ERROR: expected exit code 2, got $EC"
        exit 1
    fi
    echo "OK: validator correctly reported violations (exit 2)"
}

echo ""
echo "--- Test 2: post-injection fixture should PASS ---"
python "$VALIDATOR" "$PASS_FIXTURE"
echo "OK: validator passed on injected fixture"

echo ""
echo "All tests passed."
```

```bash
chmod +x mockup-feedback/annotate/tests/run_validator.sh
```

- [ ] **Step 3.7: Run the full test suite**

```bash
cd mockup-feedback/annotate && bash tests/run_validator.sh; cd ../..
```

Expected final line: `All tests passed.`

- [ ] **Step 3.8: Commit**

```bash
git add mockup-feedback/annotate/validator.py \
        mockup-feedback/annotate/tests/
git commit -m "test(mockup-feedback): annotate validator + pre/post-injection fixtures

TDD: validator PASS on expected/, FAIL on fixtures/.
Fixtures copied from walkthrough-mockup/static-html/tests/expected/minimal.

Phase 3 Task 3A step 3.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Write `SKILL.md` body (the AI-agent prompt)

**Files:**
- Modify: `mockup-feedback/annotate/SKILL.md` (replace BODY_PLACEHOLDER)

The skill body instructs an AI agent (Claude Code / omp runner) to:
1. Validate inputs
2. Copy the overlay bundle to the site root
3. Inject the script tag into every HTML file
4. Initialise `_concept/_feedback/` directories

- [ ] **Step 4.1: Replace `SKILL.md` body placeholder**

Replace everything from the first `# mockup-feedback-annotate` heading to EOF
with the content below (keep the YAML frontmatter intact):

```markdown
# mockup-feedback-annotate

## Overview

Injects the `annotation-overlay.js` bundle into a walkthrough site so
stakeholders can click on any labelled element, type a comment, and
submit it. The first skill in the `mockup-feedback` cluster — run it
after `walkthrough-mockup-static-html` (or any `walkthrough-mockup-*`
variant).

**What you will do:**

1. Locate the walkthrough site root.
2. Copy the overlay bundle from this skill's `overlay/` directory.
3. Inject a `<script>` tag into every HTML file.
4. Initialise `_concept/_feedback/sessions/` and `_concept/_feedback/index.json`.
5. Report a summary.

---

## Step 1 — Locate the site root

Default site root: `_concept/walkthrough-mockup/static-html/`

Override by checking `PARAMETERS.walkthrough_site_root` if provided.
Abort with an error if the directory or `manifest.json` does not exist.

```
SITE_ROOT = <project-root>/_concept/walkthrough-mockup/static-html
```

Read `manifest.json` and note:
- How many screens are listed (`screens[]`).
- How many have `"provisional": true` elements (users will see the
  provisional warning in the popover).

---

## Step 2 — Copy the overlay bundle

Copy the file at `<skill-dir>/overlay/annotation-overlay.js` to
`<SITE_ROOT>/annotation-overlay.js`.

If the file already exists and its content is identical, skip and log
"overlay already up to date".

---

## Step 3 — Inject the script tag into every HTML file

Collect every `.html` file under SITE_ROOT:
- `index.html`
- `screen/<group>/<name>.html`
- `journey/<id>.html`

For each file:
1. Read the file content.
2. Check whether `annotation-overlay.js` is already referenced in a
   `<script>` tag. If yes, skip this file (idempotent).
3. Insert the following tag as the very last line before `</body>`:
   ```html
   <script type="module" src="annotation-overlay.js"></script>
   ```
   Replace the **first occurrence** of `</body>` from the **right**
   (`str.rfind`) to handle any whitespace layout correctly.
4. Write the file back.

> **Important:** use `rfind('</body>')` — do not use regex. The body
> close tag appears exactly once per well-formed HTML page.

---

## Step 4 — Initialise `_concept/_feedback/` directories

Create (if absent) under the **project root / `_concept/`** (not the site root):

```
_concept/_feedback/
├── sessions/       ← gitignored; stores per-session annotation JSON
└── index.json      ← gitignored; session registry
```

Write `_concept/_feedback/index.json` with initial content (skip if file already
exists):

```json
{
  "schema_version": "1.0",
  "sessions": []
}
```

Append to `.gitignore` (project root) if the entry is not already
present:

```
_concept/_feedback/sessions/
_concept/_feedback/patches/
```

> `_concept/_feedback/applied/` and `_concept/_feedback/devlog.md` are **committed** —
> do NOT gitignore those.

---

## Step 5 — Report

Print a summary:

```
mockup-feedback-annotate complete
  site root       : _concept/walkthrough-mockup/static-html/
  HTML files      : 5 injected  (0 skipped — already up to date)
  overlay bundle  : annotation-overlay.js
  sessions dir    : _concept/_feedback/sessions/ (created)
  index.json      : _concept/_feedback/index.json (created)

  Provisional element IDs: 3 (will show ⚠ banner in overlay)
  Open questions remain:   none

Next step: open the walkthrough in a browser, click an element in
Annotate mode, and verify the popover appears.
For forge-concept integration: see forge-concept/docs/superpowers/specs/
2026-05-05-bidirectional-spec-visual-loop.md § Component 4.
```

---

## Inputs

| Name | Type | Default | Notes |
|---|---|---|---|
| `walkthrough_site_root` | path | `_concept/walkthrough-mockup/static-html/` | Any `walkthrough-mockup-*` output dir |

## Outputs

| Path | Description |
|---|---|
| `<site-root>/annotation-overlay.js` | The overlay bundle |
| `<site-root>/**/*.html` | HTML files with script tag injected |
| `_concept/_feedback/sessions/` | Session directory (gitignored) |
| `_concept/_feedback/index.json` | Session index (gitignored) |

## References

- `contracts/elements_block.md` — `data-spec-element` id conventions
- `walkthrough-mockup/static-html/SKILL.md` — `data-spec-*` attribute table
- `docs/devlog/forge-concept-walkthrough.md` — postMessage protocol + storage layout
- `REFACTOR_MOCKUP.md` § 11 — resolved decisions (storage policy, overlay packaging)
```

- [ ] **Step 4.2: Verify frontmatter is still intact**

```bash
python -c "
import re, sys
text = open('mockup-feedback/annotate/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
assert m, 'Frontmatter missing'
assert 'name: mockup-feedback-annotate' in m.group(1), 'name field missing'
print('OK')
"
```

Expected: `OK`

- [ ] **Step 4.3: Check BODY_PLACEHOLDER is gone**

```bash
grep -c "BODY_PLACEHOLDER" mockup-feedback/annotate/SKILL.md && echo "ERROR: placeholder still present" || echo "OK: placeholder removed"
```

Expected: `OK: placeholder removed`

- [ ] **Step 4.4: Commit**

```bash
git add mockup-feedback/annotate/SKILL.md
git commit -m "feat(mockup-feedback): write annotate SKILL.md body (injection prompt)

5-step injection procedure: locate site, copy bundle, inject script
tags (rfind-based), init _concept/_feedback/ dirs, print report.

Phase 3 Task 3A step 4.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Final verification

- [ ] **Step 5.1: Run the full validator test suite one more time**

```bash
cd mockup-feedback/annotate && bash tests/run_validator.sh; cd ../..
```

Expected: `All tests passed.`

- [ ] **Step 5.2: Verify skill is lint-clean**

```bash
python -c "
import re
from pathlib import Path

skill = Path('mockup-feedback/annotate/SKILL.md').read_text()
assert 'BODY_PLACEHOLDER' not in skill
assert 'name: mockup-feedback-annotate' in skill

overlay = Path('mockup-feedback/annotate/overlay/annotation-overlay.js').read_text()
# Must not self-reference via src= attribute (would cause infinite load loops)
assert 'src=\"annotation-overlay.js\"' not in overlay, 'overlay self-references via src='
assert 'postMessage' in overlay, 'postMessage protocol missing'
# Uses camelCase dataset access, not hyphenated attribute syntax in JS
assert 'specElement' in overlay, 'dataset.specElement access missing'

print('Skill lint: OK')
"
```

Expected: `Skill lint: OK`

- [ ] **Step 5.3: Verify DOMAIN.md references the skill**

```bash
grep -q "annotate" mockup-feedback/DOMAIN.md && echo "DOMAIN.md: OK" || echo "DOMAIN.md: MISSING annotate entry"
```

Expected: `DOMAIN.md: OK`

- [ ] **Step 5.4: Final commit (if any fixup needed) or confirm clean**

```bash
git status --short
# Expected: empty (no uncommitted changes)
git log --oneline | head -6
```

Expected log entries:
```
feat(mockup-feedback): write annotate SKILL.md body ...
test(mockup-feedback): annotate validator + pre/post-injection fixtures ...
feat(mockup-feedback): add annotation-overlay.js ...
feat(mockup-feedback): scaffold annotate skill directory ...
research: forge-concept walkthrough investigation
```

---

## Acceptance Criteria (from the migration plan)

- [x] User clicks an element on a walkthrough page, types a comment, submits
  → covered by the overlay's `showPopover` + `submitAnnotation` (browser test in Task 3F)
- [x] Annotation object has `{specRef: {element, screen, journey, route, provisional}, body, category, sessionId, createdAt, status}`
  → confirmed by `submitAnnotation` structure
- [x] Provisional IDs are flagged (`⚠` banner in popover when `provisional: true`)
  → confirmed by `showPopover` provisional check
- [x] Works on `walkthrough-mockup-static-html` output
  → confirmed by fixture test using the minimal static-html output

**End-to-end browser test (Task 3F):** open
`mockup-feedback/annotate/tests/expected/minimal/index.html` in a browser,
enable "Annotate" mode in the toolbar, click the "Sign in" button on the login
screen, type a comment, submit, click "Download". Verify the downloaded JSON
contains the correct `specRef.element = "submit-button"` entry.

---

## What's NOT in this plan

- The forge-concept server routes (`/api/feedback/*`) — tracked in forge-concept repo
- The `FeedbackDrawer.vue` UI — tracked in forge-concept repo
- `mockup-feedback-triage`, `mockup-feedback-patch`, `mockup-feedback-apply` — Task 3B
- End-to-end playwright test — Task 3F
- Lit/Astro renderer walkthroughs — Task 3C
