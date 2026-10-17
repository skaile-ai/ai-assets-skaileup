---
name: mockup-walkthrough
description: "Use when stakeholders need a clickable walkthrough of the application — one page per screen and per journey, openable in a browser, plus the manifest.json mockup-annotate reads. Renders zero-build static HTML or a built Astro site; the renderer comes from the project, not from you."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: screens }
      - { id: journeys }
      - { id: brand-tokens }
      - { id: features }
    produces:
      - { id: walkthrough, path: "_concept/09_mockup/walkthrough/" }
  prerequisites:
    files:
      - { path: "_concept/07_screens", gate: hard, min_entries: 1 }
      - { path: "_concept/04_journeys/stories.yaml", gate: hard }
      - { path: "_concept/03_brand/brand.tokens.json", gate: hard }
      - { path: "_concept/05_features", gate: soft, min_entries: 1 }
---

# mockup-walkthrough

Turns screen specs, journeys and brand tokens into a clickable site at `_concept/09_mockup/walkthrough/<renderer>/`: `index.html`, one page per screen and journey, and a `manifest.json`. This skill stops at the built site; instrumenting it for comments is `mockup-annotate`.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve the renderer, once, before anything else** — `tree/09_mockup/walkthrough/README.md § Writing it` step 1. A flow the table does not list means an unscoped project: say so and stop.
2. **Read the inputs into one in-memory model** — `tree/09_mockup/walkthrough/README.md § Writing it` step 2, with `§ Auto-slug fallback` and `§ items[] id derivation`; brand tokens flatten per `tree/03_brand/brand.tokens.md § Flattening to CSS`.
3. **Read that renderer's references, and only those, then render** — `skills/mockup-walkthrough/references/<renderer>/RENDERER.md` expands `tree/09_mockup/walkthrough/README.md § Writing it` step 3. The other renderer's directory stays closed: its hrefs, build step and styling would leak into the output. Each directory also holds a `validator.py` (step 5's check) and `tests/` with a hand-curated expected snapshot, worth reading when a rule is ambiguous.
4. **Write `manifest.json`** — `tree/09_mockup/walkthrough/README.md § Manifest schema`, written per `§ Writing it` step 4: declared targets echoed verbatim, arrays sorted, atomic write.
5. **Validate** — `tree/09_mockup/walkthrough/README.md § Writing it` step 5: `python skills/mockup-walkthrough/references/<renderer>/validator.py _concept/09_mockup/walkthrough/<renderer>`.

**Done when** the validator exits 0 and `manifest.json` names every screen under `07_screens/` and every journey in `stories.yaml`.
