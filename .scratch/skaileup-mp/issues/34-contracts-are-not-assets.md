# 34: The contracts layer is not installable — 13 refs per flow name nothing

**Type:** grilling
**Blocked by:** None — surfaced by 29 on 2026-09-05
**Status:** resolved

## Question

Graduated from ticket 29's acceptance run, which found it while proving the flow install.

`-mp` ships `contracts/*.md` as **flat files with no manifest**, so
`@skaile/workspaces` discovers **zero contract assets** in the repo (measured:
`buildProvenanceIndex` over the `-mp` clone yields 29 skills, 4 flows, **0 contracts**).
Every flow's `requires:` block names them anyway — 8 refs in `appbuilder-mvp`, 13 in the
two that list all of them — as `contract:@skaile-ai/<file_stem>`. Those refs resolve to
nothing, in both directions: no asset carries that name, and nothing puts a contract file
into an installed workspace.

The old repo did have one: `skaileup/contracts/CONTRACT.md` carries
`name: "shared-contracts"`, and `contract` is a **dir-scoped kind**, so that single
manifest made the whole reference layer one asset. Installed, it lands at
`.claude/contracts/shared-contracts/<every contract file>` (verified against
`ai-assets-skaileup` in a throwaway workspace). Ticket 09 merged `CONTRACT.md` into
`README.md` — which is where the asset went.

Two facts keep this from being urgent, and neither makes it safe:

- **Nothing reads a flow's `requires:` today.** `@skaile/workspaces` 0.48.1 resolves
  transitive deps for `bundle` only, so the refs are inert decoration — until the version
  that widens it (already on the monorepo's `main`) ships, at which point 13 unresolvable
  refs per flow become live.
- **The citation path was never right anyway.** Skill bodies cite `contracts/x.md`
  repo-relatively (`concept-brief:28-29`, and so on across the collection). Deployed, a
  skill sits at `.claude/skills/<name>/` and the contracts at `.claude/contracts/<asset>/`,
  so the cited path resolves in the repo and in no installed workspace — the old collection
  included.

So the question is what a contract *is* at install time, and there are at least three
answers, each with a different cost:

1. **Restore one dir-scoped asset** (`contracts/CONTRACT.md`, `name: shared-contracts`) and
   collapse each flow's 13 `contract:` refs to one. Cheapest; keeps ticket 09's file set;
   leaves the citation path still unresolvable in a workspace.
2. **A manifest per contract file** — 14 tiny `CONTRACT.md`s, one per reference file, so
   the existing per-file refs resolve as written. Restores exactness at the price of 14
   manifests for 14 files.
3. **Stop shipping contracts as assets** — fold each contract into the `references/` of the
   skills that read it, and delete the `contract:` refs. Ends the citation problem outright
   and costs duplication where more than one skill reads a file, which is the bar
   `contracts/` exists to enforce.

Whatever the answer, `check.py` should gate it: today the script checks that a flow's
`requires:` **contract set matches what its skills cite**, so it enforces the refs are
*consistent* while nothing checks they are *resolvable*.

## Answer

**A contract is one asset, and the word `contract` now means that asset.** `contracts/CONTRACT.md`
returns as a thin manifest (`name: shared-contracts`), the thirteen documents beside it are
**contract files**, and every flow's 8-13 `contract:` refs collapse to one. Measured before and
after with `scanDirectory` over the repo: **contract 0 → 1 `["shared-contracts"]`**, skills 29 and
flows 4 unchanged.

### What killed option 2 was not its price

`ASSET_NAME_RE` is `/^[a-z0-9]+(?:-[a-z0-9]+)*$/` and `canonicalAssetName` slugifies anything else
(`walker.ts:270`, `models.ts:288-341`). An underscore is not a legal asset-name character, so
`contract:@skaile-ai/acceptance_criteria` could **never** resolve: an asset built from
`acceptance_criteria.md` indexes as `acceptance-criteria`. Option 2's headline claim — "the
existing per-file refs resolve as written" — was false before the cost was even counted. Two more
corrections to the ticket's framing, both from `walker.ts`:

- **Option 2 was never 14 files.** `CONTRACT.md` names its *whole containing directory*
  (`DIR_SCOPED_KINDS`, `:33-40`), so one asset per document means one *directory* per document.
- **Options 1 and 2 do not compose.** A top-level `contracts/CONTRACT.md` dir-scopes `contracts/`
  recursively, swallowing any per-contract subdirectory into the same asset.

Option 3 (fold into `references/`) was refused on measurement: **no contract file has fewer than
three readers**, `concept_structure.md` has **sixteen**, and it is the file `check.py` parses as
the single source of the artifact tree — sixteen copies is sixteen things for the gate to
disagree with.

A fourth option, not shipping contracts at all, is ruled out by the citation decision below: an
agent can glob for a mis-pathed file, but only one that reached the workspace.

### The exactness that was lost, and where it went instead

One asset means a flow can no longer say *which* contract files it needs — `appbuilder-mvp` ships
all thirteen while its skills read eight, and `check.py`'s set-equality check had to go. It was
replaced by a stricter gate one level down: **a skill declares
`contract:@skaile-ai/shared-contracts` in `metadata.requires` iff it cites a contract file**
(24 of 29 skills do). That is the better home for it, because the skill is the reader — and
because a skill's `requires` has **a live reader in the shipped installer** while a flow's has
none: `fromSkillMd` parses it into the catalog entry (`manifest.ts:205`) and
`AssetManager.doctor()` walks it to report a dependency that reached no workspace
(`asset-manager/src/index.ts:2575`), whereas `bundleDeps` drops a flow's list entirely
(ticket 29).

### The citation path stays repo-relative — deliberately

90 citations across 24 skills say `contracts/x.md`, which resolves in the repo and in no installed
workspace (skills deploy to `.claude/skills/<name>/`, the contract to
`.claude/contracts/shared-contracts/`). **Left alone.** The only *program* that reads these paths
is `check.py`, and it reads the repo, where they are correct; the other reader is an agent, for
which a wrong path costs a glob, not a crash. Rewriting all 90 to the deployed path would hardcode
a driver target into skill prose **and** break the existence gate — coupling bought with friction.
Recorded in the forge-concept register instead: the collection cites paths that exist only
pre-install, and no installer rewrites them.

The old collection has the same defect. It is not a `-mp` regression.

### Vocabulary

`CONTEXT.md` gains **Contract** (the asset) and **Contract file** (the document), and its `Asset`
entry drops "reference file" — a fourth kind that was never defined and does not exist. The
`Phase` entry's "machine-read contract with forge-concept" became "machine-read **interface**":
once `contract` names an asset kind, that sentence read as though `phase` were one.

Contract filenames stay underscored (`acceptance_criteria.md`). Ticket 31's hyphenation rule
governs the `_concept/` tree the collection *writes*, not this repo's own source filenames, and
under one asset nothing machine-readable depends on them — a 90-citation rename buys nothing a
reader or a program can detect.

### The gate

Four checks, each verified by breaking it and watching it fail:

1. every cited `contracts/<file>` exists (kept unchanged);
2. a skill cites contract files ⟺ it declares the contract asset — and declaring any name other
   than `shared-contracts` is an error;
3. a flow lists the ref iff one of its node skills reads a contract file, and a per-file
   `contract:` ref is rejected outright with the reason;
4. `contracts/CONTRACT.md` exists and its `name:` **slugifies** to `shared-contracts` — the rule
   ticket 29 gated for flows, applied from the other side.

`CONTRACT_REF_RE` also gained a lookbehind, so a *deployed* path (`.claude/contracts/...`) is no
longer mistaken for a citation of a repo file.

Collection green: **29 skills · 4 flows · 0 errors.**
