# 20: Who writes a feedback session — the annotate → triage seam

**Type:** grilling
**Blocked by:** None (14 resolved)
**Status:** resolved

## Question

Graduated from ticket 14, which ported the mockup domain and found the seam broken in the
source collection: **nothing writes `_concept/_feedback/sessions/<sid>.json`**, the artifact
the entire feedback half keys on.

Outside forge-concept's iframe, the annotation overlay downloads
`annotations-<hash>.json` to the *reader's* downloads folder, and a human must move and
rename it — the filename stem **becomes** the session id everything downstream keys on.
`index.json` is created and never appended to. Ticket 14 wrote that manual hop into
`mockup-annotate` explicitly rather than paper over it, but the hop is the question.

Decide:

- **Does `-mp` accept the manual hop, or does something write the session?** The obvious
  writer is forge-concept's iframe — but that makes the iframe the *only* supported path,
  which is a real product ruling, not a shrug. The alternative writers are a script shipped
  with `mockup-annotate` or a step in `mockup-feedback` that adopts a downloaded file.
- **Note the map's fence:** making forge-concept write it is a forge-concept edit, which
  this map rules out (see Out of scope, and ticket 09's two forge-concept-gated follow-ons).
  So "the iframe writes it" is a ruling about what `-mp` *depends on*, not work `-mp` does.
  If the answer is "iframe only", say so on the map and note what breaks outside it.
- **Who owns the session id**, given the filename stem currently carries it. If a writer
  lands, does the id stay filename-derived or become explicit in the file?
- **`index.json`** — created and never appended to. Does it survive at all?

Two riders found in the same pass, both cheap and both real:

- **`triage.py` resolves journeys to `experience/journeys/<id>.md`, but journeys live in
  `stories.yaml`.** Every journey annotation therefore lands unresolved.
- **The overlay never emits `specRef.feature`**, although `triage.py` resolves it. So one of
  the three routing keys is dead on the producing side.

## Answer

**The ticket's two options were both wrong, because the standalone path does not work today
and its three faults are all inside files `-mp` already owns.** The writer is the overlay,
made whole; the filer is `mockup-feedback`. Nothing waits on forge-concept.

### The standalone path was broken three ways, not one

1. **`type="module"` blocks the overlay entirely over `file://`.** The overlay has *zero*
   `import`/`export`, yet `mockup-annotate` injected `<script type="module">` and
   `validator.py:23,103` pinned it. A module script is fetched with CORS and a `file://`
   origin is opaque, so the browser refuses the load — against a renderer whose stated
   promise is *"a stakeholder can open `index.html` from a shared folder"*
   (`static-html/RENDERER.md:80`). **Brief Q3 answered: the Download branch has never been
   reachable the documented way.**
2. **The annotation array reset on every navigation** — worse than the brief's tab-close
   framing. `const annotations = []` was in-memory; `SESSION_ID` persisted in `sessionStorage`
   but the notes did not. The walkthrough is multi-page (`screen/<g>/<n>.html`,
   `journey/<id>.html`), navigation is a real page load, and interception is **iframe-only**
   (`:198`). A reader annotating five screens could download at most the page they stood on.
3. **The documented rename guaranteed stem ≠ `sessionId`**, so `applied/<sid>.json` never
   appeared beside the session and every round read as unapplied forever.

### Rulings

- **The browser is the supported path; the iframe is kept correct and unused.** forge-concept
  has no listener, no route, no store — "iframe only" would make `-mp`'s whole feedback half
  depend on an unbuilt feature in a fenced repo, and it is the wrong ruling anyway: the
  stakeholder who annotates is the one who cannot be given a login. The postMessage branch
  stays in the overlay for whenever a host implements it; nothing in `-mp` requires it.
- **The overlay owns the session id and the filename** (`<sessionId>.json`, no rename). Zero
  code ever depended on the stem; five call sites depend on the field (`triage.py:88`,
  `apply.py:181,186,141`, `validate_applied.py:39`).
- **The human-readable name is a `label` field inside the session file**, asked for at adopt
  time. `mockup-feedback` step 2 names rounds by label; paths stay machine-owned.
- **`index.json` is deleted.** No reader, no writer, no schema — a registry of gitignored
  files that a skill must remember to append to is stale by construction, which is why it was
  already empty. `label` covers discovery; the durable record is `applied/` + `devlog.md`,
  both committed.
- **`mockup-feedback` gains step 1, adopt.** Point it at any path; it validates, files the
  file under its own `sessionId`, and asks what to call the round. The `_feedback/sessions`
  gate drops **hard → soft** — a hard gate refused the skill in exactly the case adoption
  exists to handle.
- **`specRef.feature` routing is deleted.** `resolveTarget` returns
  element/screen/journey/route/provisional and `walkthrough_renderer.md` declares no
  `data-spec-feature`: a router key with no producer reads as coverage the loop does not have.
  Removed from `triage.py` and from both `session.schema.json` copies.
- **The journey branch is re-pointed at `stories.yaml` and made `needs_manual`.** Journeys
  have never lived in per-journey files. **A hazard found while doing it:** `apply.py` anchors
  every diff on a literal markdown heading, and `_patch_section`'s no-removes path *appends to
  the end of the file* (`apply.py:58-61`) — aimed at YAML that is silent corruption, not a
  failed patch. So journey annotations now resolve (visible, quoted, hand-actionable) but are
  never patched. **This one ruling went beyond the grilling round**; it is recorded here
  because the alternative was a patcher writing prose into `stories.yaml`.
- **Annotations made on `index.html` are unresolved by design** — the site root carries
  `data-spec-index` only, no screen and no journey. Stated in the skill so it reads as a
  boundary rather than a bug.

### Landed

`-mp` working tree, **uncommitted** — a ticket-16 session is live in the same tree
(`scripts/check.py`, plus its ADR-0007 path sweep across all four mockup skills), so the two
sets of changes are interleaved in `mockup-{annotate,feedback}/SKILL.md` and cannot be
separated into two commits.

- `mockup-annotate/overlay/annotation-overlay.js` — annotations mirrored to `sessionStorage`
  under `overlay-annotations:<sid>` on every submit and reloaded on every page; download named
  `<sessionId>.json`; button count restored from storage; header comment rewritten.
- `mockup-annotate/SKILL.md` — plain `<script>` tag, `index.json` gone, *Getting the notes
  back* rewritten (the old text asserted *"the host stores the session"*, false in every
  deployed configuration, and taught the rename that caused fault 3).
- `mockup-annotate/validator.py` — `type="module"` on the overlay tag is now a **violation**,
  with a fourth regression test behind it.
- `mockup-feedback/SKILL.md` — adopt step, label-based picking, journey/feature routing rules,
  soft gate; steps renumbered.
- `mockup-feedback/scripts/triage.py` — feature branch deleted, journey re-pointed, both paths
  hoisted to named constants (`SCREEN_DIR`, `JOURNEYS_FILE`) so ticket 16's sweep is two lines.
- New fixture `test-routing` asserting both rulings; both `session.schema.json` copies gain
  `label` and lose `feature`; `patch-format.md`'s feature-file section list folded into screens.
- All harnesses green: annotate validator (4 tests), triage (5), apply integration.

**Handed to ticket 16:** the 0007 path sweep, as Q6 ruled — `triage.py`'s two constants and
the fixture tree still read `experience/`, and 16 is already mid-sweep on the SKILL.md files.
