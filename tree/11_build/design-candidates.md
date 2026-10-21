---
path: _concept/11_build/design-candidates.md
summary: evidenced candidates for a better design, found in the code
owner: [quality-design]
may_propose: []
---

# _concept/11_build/design-candidates.md

The report `quality-design` leaves after scanning the running code: each candidate is a place where the adopted design, or the absence of one, costs users something — with the `file:line` that shows it and the concept that would replace it. The user reads it to pick one candidate to pursue; the owning artifacts take the result, so the report is a working list and never a design store: it holds no decision that `APP-DESIGN.md`, the glossary, a screen spec or `_concept/10_blueprint/decisions.md` does not also hold once the user has decided. A candidate without a measured `file:line` is a guess and misleads the grill.

## Format

The file is rewritten whole each scan, so it always describes the code as it is now.

```markdown
---
last_updated: YYYY-MM-DD
source_sha: <git HEAD of the code scanned>
roots: [src/]
intent: [APP-DESIGN.md, rulebook/rules.md, _concept/glossary.md]
---
# Design candidates

## DC-1 — Archive is a screen, not a filter
- **Kind**: shallow-screen
- **Evidence**: `src/pages/archive.vue:1-40` lists tasks with one fixed filter; `src/pages/tasks.vue:88` already has the filter bar
- **Friction**: to see a finished task the user leaves the list and loses their filters and scroll position
- **Before**: Archive is a route with its own list, header and nav entry
- **After**: Archive is a saved filter of the task list (`status: done`), reachable from the list's filter bar
- **Affects**: NAV-2, OBJ-1, screen `archive`, glossary term `Archive`
- **Strength**: field — `rulebook/rules.md § P8`, `§ P27`
- **Uncertainty**: the archive route may be linked from outside the app; not searched
- **Status**: open

## Not examined
- `src/legacy/**` — 40 files, sampled by grep
```

- `intent` lists what was read; `rulebook only` when the project holds none of `APP-DESIGN.md`, glossary or screen specs, which says every candidate was judged against the rulebook's statement and no decision of the app.
- `source_sha` ties the report to a revision; a candidate whose evidence lines no longer match at a later HEAD is dropped on the next scan, not edited.
- Ids are `DC-<n>`, never reused within a file; a scan that rewrites the file keeps the `Status` and decision of a candidate it finds again (same kind and evidence file) so a rejected candidate is not offered twice.

| field | holds |
|---|---|
| `Kind` | one of the five kinds of `## Detection` |
| `Evidence` | one or more `` `path:line` `` (or `path:from-to`) with what each shows, paths from the repository root; an absence cites the nearest line and says `absence:` |
| `Friction` | the task a user is doing and what goes wrong or costs extra, in the user's terms; no friction means no candidate |
| `Before` · `After` | the current concept and the proposed one, one sentence each, named with glossary terms where the glossary has them |
| `Affects` | entry ids of `APP-DESIGN.md`, glossary terms, screen ids and features the change touches |
| `Strength` | the strongest rulebook grade (`standard · field · heuristic · owner`, `rulebook/README.md § Strength grades`) among the rules that back it, with the rule ids; `owner` when only the app's own entry backs it |
| `Uncertainty` | what the scan could not see (dynamic routes, unread regions, a consumer outside the repo); `none known` is allowed only after a search that is named |
| `Status` | `open` · `selected` · `accepted DR-<n>` · `rejected DR-<n>` |

## Detection

Each kind has one detection pass, a subagent task that returns `file:line` lists.

| kind | looks for | rules |
|---|---|---|
| `shallow-screen` | a route or screen whose purpose is a subset or a single verb of another (one fixed filter, one form, one action) and would work as a representation, saved filter, dialog or action; a screen with no concept purpose | `P8`, `P18`, `P27` |
| `overloaded-concept` | one word that names two things in code or UI (a status that is both lifecycle and visibility; a purpose that needs "and"), or two words for one thing | `P13`, `P27` |
| `hidden-mode` | a state that changes what the same control does and shows no sign of it (an edit toggle without indicator, a filter that persists unseen, a scope that silently narrows search) | `P25`, `P23` |
| `undeclared-representation` | an object rendered in a form `APP-DESIGN.md § Objects` does not list (a third card style, an ad-hoc chip), or a form with two implementations | `P2`, `P4` |
| `tier-violation` | a tier-3 attribute in a row or outside a peek, popover or named disclosure, or a tier-1 attribute absent from the primary region, with no `§ Exceptions` row | `P21` |

## Landing proposals

The owner's node holds the entry shape; this is the shape `quality-design` appends there. Each proposal names its source `DC-<n>` and carries `proposed_by: quality-design` and `proposed_on: YYYY-MM-DD`, or in `APP-DESIGN.md` and a screen's `### Open` the marker `(proposed by quality-design, YYYY-MM-DD)` that stands for both, and adds without editing a confirmed entry. An owner file that does not exist is created holding only the proposal (`tree/README.md § Ownership`); the completion summary names the owner who settles it.

| owner artifact | proposal |
|---|---|
| `_concept/glossary.md` | a `status: proposed` term entry per `tree/glossary.md § Format`: both terms of a split, or the winning term of a rename (the losing word goes under `_Avoid_` when the owner promotes it) |
| `APP-DESIGN.md` | a § Open row `Q<n>` per `tree/APP-DESIGN.md § Format`: question naming `DC-<n>`, the alternatives as options, and the recommendation cell ending `(proposed by quality-design, YYYY-MM-DD)` |
| `_concept/07_screens/<screen>.md` | a `### Open` bullet `Q-<screen_id>-<n>` per `tree/07_screens/[screen].md § Format`, with the recommendation, a one-line consequence and the same marker; a merge lands on the surviving screen |
| `_concept/10_blueprint/decisions.md` | a record `By: quality-design` per `tree/10_blueprint/decisions.md § Format`; **Decision** states the chosen concept, **Options rejected** the design-it-twice losers and the status quo, **Refs** `DC-<n>`, the evidence lines and the proposed entry ids |

## Writing it

1. **Read the intent** (`tree/README.md § How a skill runs`, rule 1), in any order and none required: `APP-DESIGN.md` per `tree/APP-DESIGN.md § Reading it`, `rulebook/rules.md` for the rules of `## Detection`, `_concept/glossary.md`, `_concept/07_screens/`, and the code roots `_concept/10_blueprint/techstack.md` or `_concept/02_grounding/findings/stack.md` name, else `src/`, else the stack's own roots. Where `_concept/02_grounding/findings/screens.md` or `interaction.md` exist and their `source_sha` equals HEAD, start from them; where they are missing or stale, Call the Skill tool with "concept-reverse" scoped to `screens` and `interaction` for the paths in focus. Missing intent is not a stop: the scan runs against the rulebook and `intent:` says so. Several apps in one repo is a question for the user.
2. **Scan in parallel.** One subagent per kind of `## Detection`, on a small, fast model, briefed with its row and the citation rule (paths from the repository root); each returns `file:line` lists and writes nothing. Skip generated and vendored code (`tree/02_grounding/findings/interaction.md § Generated and vendored code`). Judging stays in this session.
3. **Judge into candidates.** One candidate per distinct cause, filled per `## Format`; drop any without a measured `file:line` or without user friction. Check every citation per `tree/02_grounding/findings/interaction.md § Verifying citations`. Order by strength grade, then by how many tasks the friction touches; keep at most seven, the rest named in the summary.
4. **Write the report** to `_concept/11_build/design-candidates.md`. When the user asks for a presentation, render the same candidates as one self-contained HTML file in the system temp directory and print its path; the Markdown file stays the only artifact.
5. **Ask which candidate** in one decision batch (`tree/README.md § How a skill runs`, rule 2): the question is which one to pursue, options are the candidates plus `none, stop here`. One candidate is pursued per run; mark it `selected`.
6. **Grill the candidate.** Call the Skill tool with "grilling" on the selected candidate: its purpose, the "and" in it, the task that suffers, what users see after, data and permission effects, the entries it affects, reversibility. When the skill is absent, ask the same as one decision batch (rule 2).
7. **Design it twice** when the grill leaves the after-concept open or the change is hard to reverse, and the user agrees: three subagents each design a different after-concept (for instance minimal interface, most flexible, tuned to the commonest task), then compare them with the status quo as one consequence table (user-visible · data/permission · affected artifacts · reversibility) per rule 5, and ask which wins.
8. **Land the result** per `## Landing proposals`: the proposals for the artifacts the decision touches, and one decision record whether the candidate was accepted or rejected (a rejection with `Status: rejected`, so it is not offered again). Set the candidate's `Status` to `accepted DR-<n>` or `rejected DR-<n>`. Application code stays untouched.
9. **Completion summary** (rule 8): the report path with candidate counts per kind, the proposals landed and where, the record id, the unread regions, and next steps by demand — `experience-interaction`, `concept-glossary` and `experience-screen` promote what landed in their artifacts, `build-plan` plans the code change once the design is promoted.

## Checks

- The file has `last_updated`, `source_sha` and `intent`; every candidate has all eight fields and a unique `DC-<n>`.
- Every `Evidence` line passes the citation check; no candidate lacks friction.
- At most one candidate is `selected` or decided per run, and a decided one cites its `DR-<n>` and a record exists.
- Every proposal landed carries `proposed_by: quality-design`, `proposed_on` and `source: DC-<n>` (or the marker and `DC-<n>` where § Landing proposals says so), and no confirmed entry or application file changed.
- The unread regions are named under `## Not examined`.
