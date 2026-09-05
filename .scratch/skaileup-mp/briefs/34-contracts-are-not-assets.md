# Brief 34: The contracts layer is not installable

Measured 2026-09-05 against `-mp` `7cc3bbf`, `workspaces` working tree, `ai-assets-skaileup`.
Findings only — no answer here.

## How a contract becomes an asset (the mechanism the ticket assumed)

`core/src/walker.ts:132` — `{ dir: "contracts", kind: "contract", mdName: "CONTRACT.md" }`.
Discovery is **not** the top-level `<kind-plural>/<name>/` scan the comment names: `walkOne`
(`:164-175`) looks for `skaile.manifest.yaml` anywhere, and finding none falls to
`walkFilenameConvention` (`:425-451`), which delegates to `scanDirectory` — **recursive, by
manifest filename, at any depth**. `contract` is in `DIR_SCOPED_KINDS` (`:33-40`), so the asset
spans its `CONTRACT.md`'s whole containing directory, recursively (`walkDirRecursive`).
Asset name: `fromContractMdContent` (`manifest.ts:467-471`) takes frontmatter `name:`, falling
back to the parent directory name.

Two consequences the ticket's option list did not carry:

- **Option 2 cannot be "14 tiny CONTRACT.md files".** One `CONTRACT.md` per contract means one
  *directory* per contract — `contracts/<stem>/CONTRACT.md` — because the manifest names its
  folder, not its neighbours. 14 files becomes 14 directories plus 14 manifests.
- **Options 1 and 2 do not compose.** A top-level `contracts/CONTRACT.md` dir-scopes
  `contracts/` recursively, swallowing any per-contract subdirectory into the same asset.

Install target: `driver-targets.ts` `claude-code.local.contract = ".claude/contracts"`, so a
dir-scoped `shared-contracts` lands at `.claude/contracts/shared-contracts/<every file>`.

## The old repo's manifest, for reference

`skaileup/contracts/CONTRACT.md`: `name: "shared-contracts"`, `do_not_invoke: true`, and a
Contents table listing 17 files. Ticket 09 merged it into `contracts/README.md` — which has the
table but **no frontmatter**, so the asset went with the frontmatter, not with the merge.

## Readership — what option 3 would duplicate

Every `-mp` contract, by count of skills whose body cites it:

| contract | skills | | contract | skills |
|---|---|---|---|---|
| `concept_structure.md` | **16** | | `seed_data.md` | 4 |
| `artifact_frontmatter.md` | 10 | | `semantic_types.md` | 3 |
| `acceptance_criteria.md` | 6 | | `domain_model.md` | 3 |
| `agent_patterns.md` | 6 | | `evaluator.md` | 3 |
| `feedback_loop.md` | 6 | | `golden_principles.md` | 3 |
| `walkthrough_renderer.md` | 6 | | `slice_loop.md` | 3 |
| `elements_block.md` | 4 | | `README.md` | 0 |

**No contract has fewer than three readers.** Folding into `references/` is 3 copies at best and
16 at worst — and `concept_structure.md` is the file `scripts/check.py` parses as the **single
source of the artifact tree** (`check.py:137-144`, `:185-194`); sixteen copies is sixteen things
for the gate to disagree with.

## The citation path, measured

90 `contracts/<file>.md` occurrences across 28 skill files. Written repo-relative, in backticks
or parens; **zero** occurrences of `.claude/contracts` anywhere in the repo. No path rewriting
exists in the installer (grepped `workspaces/packages/workspaces/*/src`).

So deployed, a skill sits at `.claude/skills/<name>/` and cites `contracts/x.md`, which resolves
to nothing from any cwd a run uses. **This is true of the old collection too** — it is not a
regression `-mp` introduced.

The reader is an **agent**, not a program: a wrong path costs a search, not a crash. The one
program-level reader is `check.py`, and it reads the repo, not an install.

## What the gate does today

`check.py:_contract_names` / `check_flow_contracts` — a flow's `requires:` contract set must
equal the union of contracts its node skills cite, and every cited `contracts/<ref>` must exist
in the repo (`:237-239`). So the refs are gated **consistent** and **repo-resolvable**, and
nothing gates them **installable**.

## Live or inert

Inert today: `bundleDeps` (`@skaile/workspaces` 0.48.1) opens `if (kind !== "bundle") return
undefined`, so a flow's `requires:` provisions nothing at all — skills included. The monorepo's
`main` has already widened this (`manifestDeps`). When that ships, 8-13 unresolvable `contract:`
refs per flow go live at the same moment the `skill:` refs start working.

## The scoping question this raises

The map's destination — "one real project installs `-mp` and its flows load green" — was reached
by ticket 29 with the contracts layer in exactly this state. Whether 34 is a step on the route or
past its end is itself open.
