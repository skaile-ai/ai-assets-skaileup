---
name: mockup-walkthrough-migrate-elements
description: "Use once per project when existing screen specs predate the elements: block MUST (experience-screens, depth medium/max) and need retrofitting. Mines each screen's ### UI Elements / ## Actions / ## Information Displayed / ## Wireframe / ## What the User Sees prose (and the shell's ## Navigation) into a proposed elements: frontmatter block, then routes the change through mockup-feedback-patch's diff dialect for human-reviewed application via mockup-feedback-apply. A one-time backfill — not part of the pick-one renderer set."
metadata:
  version: '0.1.0'
  stage: alpha
  tags:
    - 'mockup-walkthrough'
    - 'migration'
    - 'elements-block'
    - 'backfill'
    - 'one-time'
    - 'navigation'
    - 'content-fidelity'
  artifacts:
    requires:
      - id: screens
        gate: hard
  prerequisites:
    files:
      - path: '_concept/experience/screens'
        gate: hard
        description: 'At least one screen spec (excluding 00_layout/) to migrate'
        min_entries: 1
    reads:
      - path: '_concept/experience/screens/00_layout/shell.md'
        description: "Shell's own ## Navigation list — migrated separately into a kind: nav element"
      - path: '_concept/blueprint/datamodel/seed.json'
        description: 'Optional — preferred source for sample_rows/items over wireframe reconstruction'
    produces:
      - path: '_concept/_feedback/patches/<sid>.json'
        description: "This skill's synthetic migration session — proposed elements: patches in mockup-feedback-patch's dialect"
      - path: '_concept/_feedback/patches/<sid>.review.md'
        description: 'Human review checklist; low-confidence items unticked'
---

# Migrate Elements — Backfill `elements:` Frontmatter

## Overview

`experience-screens` now treats an explicit `elements:` block as a hard MUST
at depth `medium`/`max` (see `contracts/elements_block.md`). Screens written
before that MUST landed have no `elements:` block at all, so walkthrough
renderers fall back to guessing widgets from prose (`no_explicit_elements`,
`unresolved_target` warnings). This skill is the one-time backfill: it reads
each existing screen's own prose, derives a proposed `elements:` block, and
emits it as a patch through the existing `mockup-feedback-patch` /
`mockup-feedback-apply` pipeline — it never edits a screen file itself.

**One combined pass, not two.** Target extraction (which action bullets name
a destination screen) is a strict subset of content extraction (the same
bullets' labels/kinds, plus tables/lists/tabs from `## Information
Displayed`/`## Wireframe`/`## What the User Sees`). Splitting them into two
skills would emit two conflicting diffs against the same frontmatter block
and force two review rounds over the same 43 screens — so one pass produces
the complete block per screen.

## When to Use

- A project's screens predate the `elements:` MUST and renderer warnings
  (`no_explicit_elements`, `unresolved_target`) are the dominant warning kinds
  in `manifest.json`.
- User asks to "backfill elements blocks", "migrate old screens", or reports
  mockup renderers guessing widgets instead of showing declared content.

## When NOT to Use

- New screens — `experience-screens` already writes `elements:` going
  forward; this skill is for existing specs only.
- A screen whose `elements:` block already covers everything named in its
  own `### UI Elements`/`## Actions`/`## Information Displayed` — nothing to
  migrate; STEP 1 skips it.
- Editing rendered HTML or walkthrough output — this skill only touches
  `_concept/experience/screens/**` source, and only via a patch, never
  directly.

## Prerequisites

**REQUIRED BACKGROUND:** Read `contracts/elements_block.md`,
`contracts/walkthrough_renderer.md` (§ Auto-slug fallback — this skill reuses
its Actions-bullet extraction rule verbatim), `skaileup/07_mockup-feedback/03_patch/SKILL.md`
(diff dialect), and `skaileup/07_mockup-feedback/04_apply/SKILL.md` (how a
patch lands) before proceeding.

**Hard gate:** `_concept/experience/screens/` must exist with at least one
screen spec besides `00_layout/shell.md`.

---

ROLE Migration agent — retrofits `elements:` frontmatter onto screen specs
written before the block was a MUST, by mining existing prose into patches
for human review; never writes to a screen file directly.

READS
_concept/experience/screens/**/*.md — existing specs (title, ## Route, ### UI Elements, ## Actions, ## Information Displayed, ## Wireframe, ## What the User Sees), excluding 00_layout/
_concept/experience/screens/00_layout/shell.md — ## Navigation destination list (migrated in its own substep)
? _concept/blueprint/datamodel/seed.json — authored fixture rows/items, preferred over wireframe reconstruction

WRITES
_concept/_feedback/patches/<sid>.json — proposed elements: patches (this skill's own synthetic session)
_concept/_feedback/patches/<sid>.review.md — human checklist; low-confidence items start unticked

REFERENCES
contracts/elements_block.md — elements: schema: kind enum, ID rules, § Navigation targets, § Content fidelity
contracts/walkthrough_renderer.md — § Auto-slug fallback (Actions-bullet extraction algorithm, reused here verbatim so a migrated block and the renderer's own fallback agree on the same prose) and the warnings[] kinds this migration is meant to reduce
skaileup/07_mockup-feedback/03_patch/SKILL.md — diff dialect (`@@ frontmatter:elements @@`), patches/<sid>.json + review.md shapes, needs_manual handling
skaileup/07_mockup-feedback/04_apply/SKILL.md — how an approved patch is applied, committed, and audited
skaileup/03_experience/03_screens/SKILL.md STEP 4b — target-resolution precedence (title → route → filename/group stem) this migration mirrors

REQUIRES
hard: _concept/experience/screens/ — at least one screen spec (excluding 00_layout/)
hard: git — mockup-feedback-apply commits the eventual patch landing
soft: _concept/blueprint/datamodel/seed.json — enriches sample_rows/items but not required

INPUT
Read from: _concept/_grounding/mockup-walkthrough-migrate-elements/input.json
If missing, ask the user:
- screen_glob: Screens to migrate (optional) [all | group:<NN_name>] default: all
- session_id: Synthetic session id for this batch (optional) default: migrate-elements-<YYYY-MM-DD>

MUST route every source mutation through mockup-feedback-apply — this skill only ever writes to _concept/_feedback/patches/, never to a screen file
MUST propose label: values that are short on-screen UI copy — the extracted quoted token or verb-stripped clause — never the action sentence itself
MUST source sample_rows/items content only from seed.json or the screen's own wireframe/Template Data, verbatim — never invent patient names, dates, or values absent from the source
MUST leave an action bullet's target unset, and its review item unticked, whenever the destination can't be resolved by title/route/stem match — the prose stays truth until a human resolves it
MUST record in review.md any UI-Elements/Actions/Information-Displayed item the proposed block couldn't represent, rather than silently dropping it
NEVER tick a checklist item for a guessed target below the stated confidence rule
NEVER edit rendered HTML or files under a mockup-walkthrough-*/ output tree
NEVER modify 03_patch, 04_apply, or any renderer — only emit patches compatible with what they already parse

EMIT [migrate-elements] started run_id=<uuid>

STEP 1: Inventory screens and shell

- $ find _concept/experience/screens -name '*.md' -not -path '*/00_layout/*'
- For every screen file: read frontmatter (implements, data_entities, layout, existing elements: if any, last_updated) and the body's headings
- Build a screen_id → (title from the `# Screen: <Name>` heading, ## Route value, filename/group-stem words) lookup — STEP 2's target resolution reads from this same lookup
- Separately read _concept/experience/screens/00_layout/shell.md for its ## Navigation section — the shell is migrated by STEP 2's item (e), not the per-screen loop
- Skip (report, do not patch) any screen whose elements: block already has an entry for every item named in its own ### UI Elements, ## Actions, and ## Information Displayed — this is a backfill for gaps, not a re-derivation of settled screens

STEP 2: Extract proposed elements per screen

(a) ### UI Elements, when present — one entry per named item; label = the item's own name.

(b) ## Actions — one entry per bullet, using the same extraction rule the walkthrough renderer's own auto-slug fallback uses (contracts/walkthrough_renderer.md § Auto-slug fallback, item (d)) — reused verbatim so a migrated block and a future auto-slugged fallback derive the same label/kind for the same prose:
  - label: the bullet's first quoted token ("…" or „…") when present; otherwise the clause preceding the first →, with a leading interaction verb (Click, Change, Select, Switch, Drag, Pick, Open — optionally preceded by an article) stripped, truncated to ≤ 40 chars
  - describes: the bullet's full text
  - kind: a quoted token, or a "Click …" verb → button; "Change …" / "Select …" / "Pick …" → input; "Switch tab" → tabs, with items sourced from bold or quoted tab names in ## What the User Sees (two placeholder items if none found)
  - target: only when the bullet names a destination — resolve against the STEP 1 lookup in precedence order (1) title match, (2) ## Route match, (3) filename/group-stem match; first hit wins, note which tier resolved it in review.md. No hit → leave target unset, leave the item unticked.

(c) ## Information Displayed + ## Wireframe — a repeating record with named fields → kind: table, columns: from the field names, sample_rows: from seed.json scenarios when present, else the wireframe's own example row(s) verbatim (flag low-confidence when reconstructed from ASCII art rather than a labelled example); a repeating record with no named fields → kind: list with items:.

(d) ## What the User Sees — bold or quoted tab names → items[] on a tabs element (also feeds (b)'s "Switch tab" case).

(e) Shell only (00_layout/shell.md) — ## Navigation's ordered destination list → one kind: nav element, items[] one entry per destination in the same order, each items[].target resolved the same way as (b).

- Build the complete proposed elements: list per screen as a MERGE: every existing entry carried over verbatim (an already-promoted id with provisional: false is never touched), plus one new entry per item above not already represented by a case-insensitive label match against an existing entry — mirroring the renderer's own hybrid-ID matching convention.

STEP 3: Emit patches

- session_id = PARAMETERS.session_id, else migrate-elements-<today>
- For each screen with at least one newly-derived item, diff the merged list from STEP 2 against the file's current frontmatter:
  IF the file already has an elements: key (populated or `[]`) — remove exactly those lines, add the full merged block
  ELSE — anchor on the last_updated: line (always present per screen_spec_template): remove it, add the proposed elements: block followed by the same last_updated: line, so the frontmatter patcher always has a non-empty remove set to match against
- One patch per screen: id = p-migrate-<screen_id>, annotationId = migrate-<screen_id> (synthetic — no annotate/triage session exists for a migration batch), file = experience/screens/<group>/<screen>.md, section = "frontmatter:elements", kind = "content", category = null, body = a short summary of which sections were mined (e.g. "### UI Elements (3), ## Actions (5), ## Information Displayed (1 table)"), diff = the @@ frontmatter:elements @@ block per 03_patch's dialect
- Write patches/<sid>.json: {sessionId, proposedAt, patches[], needs_manual[]} — needs_manual for any screen where nothing could be extracted (reason: which sections were empty/absent)
- Write patches/<sid>.review.md: one `- [x]` item per patch by default; `- [ ]` (unticked), with an inline note of which condition triggered it, for any item carrying an ASCII-reconstructed sample_rows or an unresolved target; group items under their screen's path heading; needs_manual screens listed under ## Needs manual review

STEP 4: Checkpoint and apply
CHECKPOINT migration_reviewed
Show the count of screens patched, low-confidence item count, and needs_manual count.
> "Review _concept/_feedback/patches/<sid>.review.md — tick/untick or hand-edit any item, then run mockup-feedback-apply."

UNTIL user has run mockup-feedback-apply (or explicitly defers the rest)

STEP 5: Confirm warning counts drop

- After apply, re-run the project's walkthrough renderer (mockup-walkthrough-*)
- Compare the fresh manifest.json's warnings[] counts for unresolved_target and no_explicit_elements against the pre-migration run
- Report the before/after counts; remaining no_explicit_elements screens or unresolved_target items are candidates for another migration pass (narrower screen_glob) or manual authoring

EMIT [migrate-elements] completed run_id=<uuid> screens_patched=<N> needs_manual=<N> low_confidence=<N>

CHECKLIST

- [ ] Every patch's diff anchors on "@@ frontmatter:elements @@" and matches the file's actual current frontmatter lines verbatim
- [ ] Every label is short on-screen UI copy, never an action sentence
- [ ] Every sample_rows/items entry traces to seed.json or the screen's own wireframe/Template Data — none invented
- [ ] Every low-confidence item (ASCII-reconstructed rows, unresolved targets) is unticked in review.md with its reason noted
- [ ] Screens where nothing was extracted are in needs_manual[], not patches[]
- [ ] No screen file was edited directly — the only output is patches/<sid>.json + review.md
- [ ] Existing entries (especially already-promoted, non-provisional ones) are preserved verbatim in the merged block, not overwritten
- [ ] Shell's ## Navigation is mirrored into shell.md's own kind: nav patch, items[] in the same order
- [ ] Re-ran the walkthrough renderer after apply and compared warnings[] counts before/after

---

## Common Mistakes

| Mistake | What to do instead |
|---|---|
| Emitting one patch for targets and a second for content on the same screen | One combined patch per screen — target extraction is a subset of content extraction |
| Writing the action sentence as label: | label: is short UI copy; the action sentence belongs in describes: |
| Guessing a target and ticking the item anyway | Leave target unset and the item unticked when no tier of the resolution precedence hits |
| Reconstructing sample_rows from ASCII wireframe art and ticking the item | Flag as low-confidence, leave unticked, prefer seed.json when available |
| Replacing an already-promoted (provisional: false) entry | Merge — carry every existing entry over verbatim, only add what's missing |
| Editing the screen .md file directly | Emit a patch; the human runs mockup-feedback-apply |

## Integration

- **Called by:** the orchestrator or standalone, once per project, after noticing renderer warnings dominated by `no_explicit_elements` / `unresolved_target`
- **Requires:** `_concept/experience/screens/` with at least one non-shell spec
- **Feeds into:** `mockup-feedback-patch`'s dialect directly (this skill plays that skill's role for a migration batch, without an antecedent annotate/triage session) → `mockup-feedback-apply` → re-run of `mockup-walkthrough-*`
- **Not wired into any flow's node graph** — this is a manual/orchestrator-routed, one-time pass; a flow's `requires:` exactness would otherwise force churn across every tier flow for a step most projects run at most once
