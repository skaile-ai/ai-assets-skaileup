# Slice Loop Contract

Shared lifecycle rules for the two per-feature slice loops. Consumed by
`concept-slice-{brainstorm,align,scope-feature,design-feature}`,
`impl-plan-{brainstorm,align,plan-vertical}`, and the `impl-slice-*` chain.
Cite these sections instead of restating them.

## Tier gate

| `scope.yaml` tier | concept-loop entry | impl-loop entry |
|---|---|---|
| `appbuilder-mvp` | (concept loop skipped) | `impl-plan-plan-vertical` |
| `appbuilder-simple` | `concept-slice-align` | `impl-plan-align` |
| `appbuilder-standard` | `concept-slice-brainstorm` | `impl-plan-brainstorm` |
| `appbuilder-complex` | `concept-slice-brainstorm` | `impl-plan-brainstorm` |

Every loop skill MUST refuse when `_concept/_meta/scope.yaml` is missing
(iron_laws § 7) and when `scope.tier` sits outside its row above. Refuse
message format (pinned):

> "[<skill>] tier=<tier> does not run <phase>.
>  <one sentence naming the correct entry skill for that tier>."

## Slug rule

`slice_id` regex: `^[a-z][a-z0-9-]{1,47}$`

Derivation from a human title: lowercase → replace each non-`[a-z0-9]` run
with a single `-` → trim leading/trailing `-` → truncate to 48 chars.
Impl side: `slice_id := feature_slug` verbatim (same regex) — never
re-derived from the title. `feature_slug` resolves by globbing
`_concept/experience/features/*/<feature_slug>.md`; refuse on zero or >1
matches (>1 = slug collision across groups; name the matches, ask).

## Resume-or-fresh

When the phase's target handoff file already exists:

1. NEVER overwrite silently.
2. Ask STANDALONE: "(a) resume — load and refine the existing file, or
   (b) start fresh". Entry-phase skills may offer a `-2`-suffixed new slug
   for (b); every fresh-overwrite requires explicit confirmation before any
   write.
3. On resume: load the existing file, show what would change, ask before
   writing.

When the dossier directory does not exist: `mkdir -p` it.

## Handoff frontmatter

| Side | Keys (all required, this order) |
|---|---|
| concept (`_concept/slices/<id>/`) | `slice_id`, `feature_title`, `phase`, `tier`, `created_at`, `last_updated` |
| impl (`_implementation/slices/<id>/`) | `slice_id`, `feature_title`, `feature_path`, `phase`, `tier`, `created_at`, `last_updated` |

Rules: `phase` = the writing skill's phase name; `created_at` copied from the
predecessor handoff when present, else `now()` (ISO-8601 UTC);
`last_updated` = `now()`; `slice_id` / `feature_title` / `feature_path`
copied VERBATIM from the predecessor — never re-derived.

## Context isolation

`/clear` between every phase. A phase reads ONLY its predecessor's handoff
plus the durable concept artifacts it names — no phase carries the whole
slice in context (dumb-zone guard, ~100k tokens).

## Freeze lifecycle

Slice dossiers are frozen, never deleted. The terminators
(`concept-slice-design-feature`, `impl-slice-commit`) write `index.md` and
keep every phase handoff as permanent per-feature documentation;
`impl-slice-commit` additionally removes the transient `progress.yaml`.
No other loop skill deletes or freezes the dossier.
