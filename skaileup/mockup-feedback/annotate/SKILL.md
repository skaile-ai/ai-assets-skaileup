---
name: mockup-feedback-annotate
description: "Use when a walkthrough site is ready and you need stakeholders to annotate it. Injects the annotation overlay so stakeholders can click elements and submit comments; produces _concept/_feedback/sessions/ for storage. First skill in the mockup-feedback cluster."
metadata:
  version: "0.1.0"
  tags:
    - mockup-feedback
    - annotation
    - overlay
    - data-spec
    - walkthrough
  stage: alpha
  artifacts:
    requires:
      - id: walkthrough
        gate: hard
    produces:
      - id: feedback-overlay-bundle
      - id: feedback-sessions
      - id: feedback-index
  prerequisites:
    files:
      - path: "_concept/mockup-walkthrough"
        gate: hard
        description: "At least one mockup-walkthrough-* output must exist (manifest.json + HTML files)"
        min_entries: 1
    reads:
      - path: "_concept/mockup-walkthrough/static-html/manifest.json"
        description: "Validates data-spec-element IDs and identifies provisional ones"
    produces:
      - path: "_concept/mockup-walkthrough/static-html/annotation-overlay.js"
        description: "The overlay bundle copied from skill/overlay/"
      - path: "_concept/_feedback/sessions/"
        description: "Session JSON directory (gitignored); created if absent"
      - path: "_concept/_feedback/index.json"
        description: "Session index (gitignored); created if absent"
---

# mockup-feedback-annotate

## Overview

Injects the `annotation-overlay.js` bundle into a walkthrough site so
stakeholders can click on any labelled element, type a comment, and
submit it. The first skill in the `mockup-feedback` cluster — run it
after `mockup-walkthrough-static-html` (or any `mockup-walkthrough-*`
variant).

**What you will do:**

1. Locate the walkthrough site root.
2. Copy the overlay bundle from this skill's `overlay/` directory.
3. Inject a `<script>` tag into every HTML file.
4. Initialise `_concept/_feedback/sessions/` and `_concept/_feedback/index.json`.
5. Report a summary.

---

## Step 1 — Locate the site root

Default site root: `_concept/mockup-walkthrough/static-html/`

Override by checking `PARAMETERS.walkthrough_site_root` if provided.
Abort with an error if the directory or `manifest.json` does not exist.

```
SITE_ROOT = <project-root>/_concept/mockup-walkthrough/static-html
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
  site root       : _concept/mockup-walkthrough/static-html/
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
| `walkthrough_site_root` | path | `_concept/mockup-walkthrough/static-html/` | Any `mockup-walkthrough-*` output dir |

## Outputs

| Path | Description |
|---|---|
| `<site-root>/annotation-overlay.js` | The overlay bundle |
| `<site-root>/**/*.html` | HTML files with script tag injected |
| `_concept/_feedback/sessions/` | Session directory (gitignored) |
| `_concept/_feedback/index.json` | Session index (gitignored) |

## References

- `contracts/elements_block.md` — `data-spec-element` id conventions
- `mockup-walkthrough/static-html/SKILL.md` — `data-spec-*` attribute table
- `docs/superpowers/notes/forge-concept-walkthrough.md` — postMessage protocol + storage layout
- `docs/devlog/mockup-design.md` § 11 — resolved decisions (storage policy, overlay packaging)
