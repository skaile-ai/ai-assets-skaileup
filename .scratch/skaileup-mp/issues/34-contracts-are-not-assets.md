# 34: The contracts layer is not installable — 13 refs per flow name nothing

**Type:** grilling
**Blocked by:** None — surfaced by 29 on 2026-09-05
**Status:** claimed

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

_(pending)_
