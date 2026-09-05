# Recon 20 — Who writes a feedback session

Evidence only. `S/` = `ai-assets-skaileup`, `MP/` = `ai-assets-skaileup-mp`, `FC/` = `forge/forge-concept`.
## The chain, end to end

**Producer.** One overlay, byte-identical in both repos (`diff` clean):
`S/skaileup/07_mockup-feedback/01_annotate/overlay/annotation-overlay.js` ==
`MP/skills/mockup-annotate/overlay/annotation-overlay.js`, with **two mutually exclusive branches** on
`IS_IFRAME` (`:38-40`, `window !== window.parent`):

- **iframe:** `submitAnnotation` posts each annotation as it is submitted —
  `window.parent.postMessage({ type: 'overlay.annotation', annotation }, '*')` (`:172`). **No
  Download button exists** (the toolbar sits inside `if (!IS_IFRAME)`, `:220`) and **no flush or
  session-end message** is ever sent — a host must accumulate N messages and invent its own session
  boundary.
- **standalone:** a floating toolbar (`:220-250`) serialising `{sessionId, annotations}` (`:243`)
  to `annotations-${SESSION_ID.slice(0, 8)}.json` (`:247`).

`SESSION_ID` is `crypto.randomUUID()` in `sessionStorage` (`:23-34`); `annotations` is an in-memory
`const annotations = []` (`:35`), **never persisted** — close the tab before Download and the round
is gone.

**← THE GAP.** Neither branch writes `_concept/_feedback/sessions/<sid>.json`. The iframe branch needs
a host listener that does not exist (§ next); the standalone branch lands a file in the reader's
downloads folder under a name downstream does not want.

**Directory-only writer.** `S/…/01_annotate/SKILL.md:110-128` creates `sessions/` (empty) and
`index.json` = `{"schema_version":"1.0","sessions":[]}`, and **never mentions the download hop at
all** — its report ends at "verify the popover appears" (`:157`). **Consumers:**
`S/…/02_triage/SKILL.md:43-56` reads `sessions/<sid>.json` (`triage.py:81-83` requires `sessionId` +
`annotations`); `03_patch` reads `triage/<sid>.json`; `04_apply/apply.py` reads
`patches/<sid>.json`. Nothing reads `index.json`.

**As ported (ticket 14).** `MP/skills/mockup-annotate/SKILL.md:60-71` is the only place in either
repo that states the hop: *"Inside forge-concept the overlay posts each annotation to the host frame
and **the host stores the session**. … That file has to be moved by hand … and **the name it is
saved under becomes the session id** every later step keys on."* Both bolded claims are false — the
first about FC (§ next), the second about the scripts (§ below).
`MP/skills/mockup-feedback/SKILL.md:7-10` gates hard on `_feedback/sessions`, `min_entries: 1`, and
step 1 (`:28`) opens *"A session is `…/sessions/<sid>.json`"* — assuming the file is there, with no
adoption path. The hard gate is all that stands where a writer should be.

## What forge-concept has today

**Nothing. It would be a new feature, not a wiring change.**
- **No postMessage listener at all.** Repo-wide `addEventListener\(.message` → **zero hits**. All five
  protocol strings appear in exactly one file, as a `draft` TypeScript proposal:
  `FC/docs/superpowers/specs/2026-05-05-bidirectional-spec-visual-loop.md:250-263`.
- **No walkthrough route.** `app/pages/` has no `walkthrough/`; the spec's `pages/walkthrough/index.vue`
  (`:364`) was never built.
- **The one real iframe is generic.** `FC/app/components/HtmlPreview.vue:40-47`,
  `<iframe sandbox="allow-scripts allow-same-origin">`, zero postMessage code in the file; used by
  `mockups/index.vue:38`, `brand-book.vue:43`, `concepts/[...name].vue:29`.
- **No write path.** No `server/api/feedback/`, no `getFeedbackDir()` (spec `:397`), no
  `_concept/_feedback/` on disk, no `.gitignore` entry. Every `writeFile` site (`settings.ts:40`,
  `content.ts:98,152,172`, `concepts/upload.post.ts:63`, `flows/[flowId]/start.post.ts:63`) is unrelated.
- **The near-miss:** FC *does* ship a working annotation system — TipTap text-anchor comment threads
  (`app/composables/useComments.ts`, `server/utils/concept-comment-store.ts`,
  `server/api/comments/[...document].post.ts`) — writing **one flat file**,
  `{projectRoot}/data/concept-discussions.json` (`concept-comment-store.ts:25,52`), outside `_concept/`,
  with no `specRef`/`sessionId`/`data-spec-element`. Not reusable, but a precedent for where FC puts
  review state.

The spec's "What is missing" (`:26-31`) lists all five components as unbuilt; `:461` proposes a
throwaway spike. **Building the writer in FC hits the map's Out of scope fence**, and is no small
edit: overlay listener + accumulator + session boundary + write path + gitignore.

## Session-id dependencies

**Zero code depends on the filename stem; two scripts depend on the JSON field.**
- **stem**, prose only: `MP/skills/mockup-feedback/SKILL.md:28-29` (pick a session).
- **JSON field**: `triage.py:88` (`out_path = output_dir / f"{session['sessionId']}.json"`),
  `apply.py:181-182` (`applied/<sid>.json`), `apply.py:186` (idempotency guard), `apply.py:141`
  (devlog `## <date> · session <sid>`), `validate_applied.py:39-42` (applied-vs-patches match).

Follow `-mp`'s own instruction literally — rename the download to
`sessions/2026-09-05-stakeholder-review.json` — and stem and field are **guaranteed** to differ (the
field is still the UUID). Triage then writes `triage/550e8400-….json`, apply writes
`applied/550e8400-….json`, and step 1's "no `applied/<sid>.json` **beside it**" looks for
`applied/2026-09-05-stakeholder-review.json`, which never appears: **the session reads as unapplied
forever**, and the same split defeats `apply.py`'s idempotency guard from the discovery side. Every
fixture sets stem == `sessionId` (`tests/shared-fixtures/sessions/test-minimal.json:2`,
`tests/apply/…/test-pass.json:2`) — green on an invariant nothing enforces, while the documented
workflow breaks.

**Inverting the ticket's framing:** if a writer generated the id and named the file after it,
**nothing breaks** — both scripts already key on the field; it *closes* the divergence. At stake is
a human-recognisable name, not a code dependency.

## index.json

Created by `S/…/01_annotate/SKILL.md:121-128` and `MP/skills/mockup-annotate/SKILL.md:47-48`. **Read
by nothing, appended to by nothing** — grep in `S/` returns only the annotate SKILL, the tree
drawing (`contracts/concept_structure.md:159`), dead `artifacts.yaml:496`, and devlogs; in
`MP/skills/` the only hit is the writing line, and the `feedback-index` artifact id no longer exists
in `-mp`. No schema exists. Vestigial: adopted verbatim from the FC spec's storage layout
(`FC/docs/…/bidirectional-spec-visual-loop.md:308-316`) without a reader. If it dies, nothing makes
session discovery durable — both skills glob a gitignored, rotating directory, and the registry was
the spec's answer to exactly that.

## Path check against ADR 0007 — stale, and it is the whole domain

ADR 0007 landed **after** the port (`MP` log: `f5ea080` port → `609ee67` ADR). ADR `:84-85` —
"`mockup-walkthrough/<renderer>/` collapse into `09_mockup/`. The renderer leaves the path";
`MP/contracts/concept_structure.md:68-71` gives `09_mockup/{walkthrough,storybook,feedback}/`.
Every ported skill still writes the old tree:

| file:line | writes | contract says |
|---|---|---|
| `mockup-annotate/SKILL.md:26,47,49,52,67,77` | `_concept/mockup-walkthrough/<renderer>/`, `_concept/_feedback/…` | `09_mockup/walkthrough/`, `09_mockup/feedback/` |
| `mockup-feedback/SKILL.md:10,28-29,36,69-70` | `_feedback/sessions`, `_concept/_feedback/…` | `09_mockup/feedback/` |
| `mockup-walkthrough/SKILL.md:22,39,43,75` | `mockup-walkthrough/<renderer>/`, `_feedback/devlog.md` | `09_mockup/…` |
| `mockup-{walkthrough,storybook}/SKILL.md` + **`mockup-feedback/scripts/triage.py:29-31`** | `experience/{screens,journeys,features}` | `07_screens/`, `04_journeys/`, `05_features/` |

`triage.py:29-31` is the worst — **code**, wrong three ways: two stale roots plus a `journey` branch
resolving to `experience/journeys/<id>.md` when journeys have never lived in a per-journey file
(`MP/contracts/concept_structure.md:52-53`: `04_journeys/stories.yaml`). The screen path *shape*
also changed (`…/<NN_group>/<screen>.md` → `07_screens/<feature_slug>/<screen>.md`), so the
`data-spec-screen` value the renderer emits (`walkthrough_renderer.md:26`, e.g.
`01_user_auth/login`) no longer matches the destination. Ticket 08 handed "every written path
resolves to a real top-level entry" to **ticket 16** — claimed, but a writer landing before 16 gets
built against a dead tree. **`specRef.feature` is dead on the producing side, confirmed twice:**
`resolveTarget` returns only `element / screen / journey / route / provisional`
(`annotation-overlay.js:62-78`, TODO at `:79-81`), and `walkthrough_renderer.md:26-31` has **no
`data-spec-feature` row** — no renderer emits it. `triage.py:30` resolves it anyway.

## Open questions for the human

1. **Is this a choice between two writers, or between a manual hop and building a feature?** FC has
   nothing — no listener, no route, no store. "The iframe writes it" costs listener + accumulator +
   session boundary + write path, in a repo the map fences off.
2. **The iframe branch has no session boundary** (`:172`, one message per annotation, no end
   signal). Whoever writes the session must invent it. A "Finish review" button is `-mp` work
   (overlay change); a host-side debounce is FC work. Which side pays?
3. **Does the standalone path even run today?** The injected tag is `<script type="module" src="…">`
   (enforced by `MP/skills/mockup-annotate/validator.py:23,103`) while
   `MP/…/references/static-html/RENDERER.md:11-13` claims the site works "from a `file://` path".
   Browsers block **module** script loads over `file://` (CORS), and the overlay has no
   `import`/`export` needing `type="module"`. If so, the Download branch was never reachable by
   double-clicking and the only working path is an undocumented local HTTP server. **Worth 60
   seconds in a browser first** — it decides whether "iframe only" is a ruling or a description.
4. **Killing `lit` killed the only no-iframe embed path.**
   `S/…/05_mockup-walkthrough/01_d_lit/SKILL.md:69-75` was explicitly the renderer mounting into a
   host's light DOM "**without iframe**" so the overlay could query `data-spec-*`. Ticket 06 dropped
   it; neither survivor mentions iframe or postMessage at all. Did 06 know?
5. **The stem-vs-field split is a live bug independent of the ruling** — one line either way. Does
   20 fix it, or hand it to 16 with the paths? Same for the false FC claim at
   `mockup-annotate/SKILL.md:62-63`, which needs correcting whichever writer wins.
6. **What does "iframe only" cost?** The stakeholder who annotates is the one who cannot be given a
   forge-concept login. Is the walkthrough still shareable as a link, and to whom?
