# 0011 — The machine layer sits under `metadata:`, and its paths carry `_concept/`

**Status:** accepted

Repairs the defect recorded in [ADR 0008](0008-gates-live-at-the-step-they-bind.md)'s
context. Narrows the frontmatter clause of [ADR 0001](0001-skill-name-is-the-identity.md).

## Context

`-mp`'s first eight skills declared `artifacts:` and `prerequisites:` at the root of their
frontmatter, with paths written bare (`07_screens`, `brief.md`). Both halves are invisible
to the only readers there are:

- `parseSkillRequirements` reads `fm.metadata ?? {}` and never falls back to the root
  (`workspaces/packages/workspaces/resolver/src/parser.ts:45-46`, identical in the deployed
  `@skaile/workspaces@0.48.1` bundle). `extractSkillRequires` returns early on a missing
  `metadata` (`discovery/src/requires-graph.ts:236-238`).
- `validateRequirements` joins each declared path to `projectDir`
  (`resolver/src/validator.ts:81`), which is `getProjectRoot()` — the *project* root, not the
  concept. A path without the prefix resolves one level too high.

Neither failure raises. `parseSkillRequirements` returns empty requirements, `satisfied` is
vacuously `true`, and a node runs with every gate unmet and no error anywhere. The template
(`docs/skill-template.md`) fixed the convention wrong at the first port and every skill
written since inherited it.

## Decision

**Everything a machine reads sits under `metadata:`; every declared prerequisite path starts
with `_concept/`.** `name`, `description` and `version` stay at the root — those readers
normalise root and nested both (`discovery/src/discover.ts:705-719`).

`artifacts.requires[]` keeps `id` and drops `gate:`. No code has ever read that key; its one
reader takes `id` only, for cycle detection over edges whose targets are artifact ids and so
can never resolve to an asset. Carrying gate strength in two blocks had already produced
three disagreements with `prerequisites.files[]` — the live declaration wins.

`scripts/check.py` enforces both halves, because both fail silently.

**Amended 2026-09-05 (ticket 32).** The path half is narrowed from a blanket ban to a named
list. `validator.ts:81` joins to the *project* root, so a project-root gate such as
`package.json` resolves correctly and the blanket rule was stricter than the reader it
protects — ticket 23 had to move `quality-test`'s source-exists gate into the step body to
work around it. The rule is now: a declared path is legal if it starts with `_concept/` and
its first segment is a real entry of the artifact tree, **or** if it is named in
`check.py`'s `PROJECT_ROOT_PREREQUISITES`. The restriction survives for everything else on a
drift argument, not a reader argument: without it, a superseded concept path like
`experience/screens/foo.md` would pass as "some project-root file", and that pre-0007 shape
is the dominant defect class in this repo (ticket 30 swept 32 files of it).

## Alternatives

**Fix the reader instead.** One line in `parser.ts` would make `metadata` optional for every
skill forever, and root-level is the Claude-skill shape ADR 0001 adopted deliberately. It
was rejected on sequencing, not on merit: changing `@skaile/workspaces` means a release and
a forge-concept bump mid-migration, and this map treats the host as fixed. The site is
recorded in the map's forge-concept register as the successor effort's cheapest entry.

## Consequences

- A `soft` gate still renders nowhere — excluded from `satisfied`
  (`resolver/src/validator.ts:149`), never warned on, and the one route that would report it
  has no callers. Where absence changes what a skill does, the step says so in prose. The
  declaration is for the machine; the sentence is for the human.
- `metadata:` is now the only nesting in the frontmatter, which reads as inconsistent beside
  root-level `version`. That inconsistency is the reader's, and it is written down here so
  the next author does not helpfully "correct" it.
- The input dialog's collected values are read from `_concept/_grounding/<skillId>/input.json`
  (`resolver/src/validator.ts:107`) — a hardcoded path that ADR 0007 renamed to
  `02_grounding/`. No `-mp` skill declares inputs yet; the first one that does inherits the
  clash. Recorded in the register.
