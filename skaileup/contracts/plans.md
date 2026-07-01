# PLANS.md Convention

`PLANS.md` is a **lean scope + phase plan**, not a status tracker and not a decision
log. It answers two questions only: *what is in scope for this session* and *what are
the phases, in order*. Everything it used to carry now lives in the artifact that
owns it:

| Concern | Owner (single source of truth) | Not in PLANS.md |
|---|---|---|
| Which steps are done / skipped / blocked | `_implementation/progress.yaml` (impl) · `concept.yaml` artifact-status (concept) | ✗ no checkbox progress |
| Why a hard-to-reverse choice was made | ADR logs — `_concept/decisions.md`, `_implementation/decisions.md` (see `domain_model.md`) | ✗ no decisions section |
| Domain vocabulary | `_concept/blueprint/glossary.md` (see `domain_model.md`) | ✗ no glossary |
| Per-slice open questions / edge cases | the slice's `align.md` under `slices/<id>/` | ✗ no per-slice detail |

This split mirrors the rest of the tree: status is machine-read where it's produced,
decisions append to the ADR logs where they're made, and PLANS.md stays small enough
to read at a glance. Duplicating progress or decisions here is how they drift.

## Plan sections

`PLANS.md` lives at the project root (or split as `_concept/PLANS.md` +
`_implementation/PLANS.md`). Two parts, written at different times.

### Concept Plan

Written by the concept orchestrator at session start; live status is read from
`concept.yaml` artifact-status, **not** re-checkboxed here.

```markdown
## Concept Plan: <App Name>

### Scope
<One paragraph: what this concept session covers, what's explicitly out.>

### Phases
1. discovery
2. experience/features
3. blueprint (techstack → glossary → architecture → datamodel)
4. experience/screens

> Live status: `concept.yaml` artifact-status. Decisions: `_concept/decisions.md`. Vocabulary: `_concept/blueprint/glossary.md`.
```

### Implementation Plan

Written after the concept pipeline; references concept artifacts as source of truth.

```markdown
## Implementation Plan: <App Name>

### Scope
<What will be built this phase, what's out of scope.>

### Source Artifacts
- Features: _concept/experience/features/ (N features, M must-have)
- Tech stack: _concept/blueprint/techstack.md
- Data model: _concept/blueprint/datamodel/ (N entities)
- Screens: _concept/experience/screens/ (N screens)
- Glossary: _concept/blueprint/glossary.md
- Brand: _concept/discovery/brand/tokens.json

### Phases
1. scaffold
2. foundation (brand tokens, auth config, app shell)
3. infrastructure (if architecture specifies custom modules)
4. migrate → seed
5. per-feature slice loop (one slice per must-have feature)
6. e2e → deploy

> Live status: `_implementation/progress.yaml`. Decisions: `_implementation/decisions.md`.
```

---

## Rules

- Create `PLANS.md` at session start, before writing any concept files.
- Keep it to **scope + ordered phases**. If you catch yourself writing a checkbox or a
  dated decision, it belongs elsewhere — `progress.yaml` / `concept.yaml` for status,
  the ADR logs for decisions.
- Phases reference concept artifacts by path; impl phases map 1:1 to features/slices.
- Never track completion here — a reader gets live status from `progress.yaml` /
  `concept.yaml`, which the build skills keep current. PLANS.md going stale is the
  failure mode this split removes.
- Record decisions as ADRs per `domain_model.md` (subject to the 3-test gate), not as
  a running list in this file.
