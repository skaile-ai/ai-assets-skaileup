# 11: Create the repo and its skeleton

**Type:** task
**Blocked by:** None (03, 04 resolved)
**Status:** resolved

## Question

Nothing to decide — work that unblocks the port. Do it once the tree shape (ticket 04) and
the skill template (ticket 03) are settled.

- Create `github.com/skaile-ai/ai-assets-skaileup-mp` (private, matching the existing repo's
  visibility and settings).
- Add it as a submodule under `ai-assets/` in the `SKAILEdev` super-repo, per the super-repo
  workflow in the root `CLAUDE.md` (commit and push the submodule first, then the pointer;
  no PRs, direct to `main`).
- Lay down the empty domain tree from ticket 04 and the skill template from ticket 03
  (`prototype/TEMPLATE.md` on branch `prototype/skill-body-shape`, with two worked ports
  beside it), plus a
  `README.md`, a `CLAUDE.md`, and `CONTEXT.md` (populated by ticket 05 if it has landed).
- Ticket 03 found `prerequisites.inputs_optional` is an input-dialog spec living in prose
  frontmatter — 8 fields, and almost all of `concept-brief`'s remaining frontmatter. If
  ticket 09 moves those specs into the machine layer, the skeleton needs somewhere to put
  them; if it does not, skills carry them and frontmatter stays ~15 lines rather than ~4.
- Port the machine spine unchanged to start: `contracts/artifacts.yaml`, the flow YAMLs, iron
  laws and golden principles. They get pruned later by tickets 09 and 10; this is just the
  starting point so the port has somewhere to land.
- `skaile.yaml` with sources and dependencies — but **do not mirror the existing repo's
  `assets:` block**. Ticket 01 proved it is dead (no `skaile.manifest.yaml` means glob mode wins;
  it declares `impl-slice-finish` while the file is `impl-slice-git-finish`, and discovery yields
  the latter), and newer `@skaile/workspaces` *throws* on those keys. Ship a real
  `skaile.manifest.yaml`, or nothing and let glob discovery do it.
- Flow layout must satisfy the contract ticket 01 documented: `<id>.flow.yaml` inside a directory
  named `<id>`, with `id: <id>` inside; the loader keeps a flow only if it has `id`, `nodes` and
  `edges`. Top-level `requires:` drives transitive install and bakes in publisher `@skaile-ai`.
- Decide and record: does `.github/` CI come across now or wait for ticket 09's answer on
  what validation survives?

Record in the answer: repo URL, submodule path, the super-repo commit, and anything that
had to differ from the plan.

## Answer

**The repo exists and the super-repo points at it.**

- **Repo:** https://github.com/skaile-ai/ai-assets-skaileup-mp — **public, not private.**
  The ticket said "private, matching the existing repo's visibility"; the existing repo is
  in fact public, so matching reality won over matching the ticket text. Consumers install
  without auth, exactly as they do today.
- **Submodule path:** `ai-assets/ai-assets-skaileup-mp` in `SKAILEdev`.
- **Skeleton commit:** `93e9d0e` on `main`. **Super-repo commit:** `cb629fb`, pushed
  straight to `main` per the super-repo workflow (submodule pushed first).

### What landed

```
skills/README.md           empty; dir name == name:, the rule stated in place
flows/README.md            empty on purpose (see below)
contracts/                 the 14 survivors + flow.schema.json
profiles/                  6 project-type files, hoisted out of contracts/
docs/skill-template.md     ticket 03's TEMPLATE.md
docs/examples/             both worked ports + WHY.md (ticket 03's FINDINGS.md)
docs/adr/                  0001-0004 + index
CONTEXT.md                 ticket 05's file, verbatim, 139 lines
README.md · CLAUDE.md · skaile.yaml · .gitignore
```

### Differences from the plan, and why

1. **The spine did not come across unchanged.** The ticket predates ticket 09, which has
   since pruned contracts 28 → 14 and killed `artifacts.yaml`. Laying down the old spine
   would have meant re-doing 09's deletions as a cleanup pass, so the skeleton starts at
   09's answer: 13 surviving contracts, `frontmatter.md` renamed **`artifact_frontmatter.md`**,
   `README.md` in place as the merge target for `CONTRACT.md`, `profiles/` moved to the root.
   **No `artifacts.yaml`**, no `schemas/`, no `tests/`, no `scripts/`.
2. **The three fold-ins are content work, not skeleton work, and are still pending.**
   `preview_compatibility.md` → `walkthrough_renderer.md`, `subagent_dispatch.md`
   (`10_impl-build/contracts/`) → `agent_patterns.md`, `CONTRACT.md` → `contracts/README.md`.
   The survivors were copied verbatim; the sources stay in the old repo, which is the
   retrieval point until the rewrite tickets grow them.
3. **`flows/` is empty.** Ticket 10 owns the flow set and is still blocked. The 19 old flow
   YAMLs reference old skill names, so porting them verbatim would have put 19 stale,
   non-loading files in a repo whose acceptance test is "flows load green". `flows/README.md`
   states the contract (`<id>/<id>.flow.yaml`, `id`+`nodes`+`edges`, `requires:`, `data.phase`
   on every node) so the shape is fixed before the first flow is written.
4. **`.github/` did not come across — deferred to ticket 16**, which owns what validation
   survives the DSL validators. There is nothing to gate yet: no skills, no flows.
5. **Nothing was laid down for `onboarding.yaml`.** Ticket 05's merged file is a *project*
   artifact (`_concept/_grounding/`), not a collection file, and ticket 09 deleted both
   schemas that described it. Nothing belongs in the skeleton for it.
6. **The two worked ports live in `docs/examples/`, not `skills/`.** Their final names and
   boundaries belong to tickets 08 and 14 — `mockup-walkthrough-astro` in particular is not
   a final skill name under ticket 06's one-skill-plus-`references/<renderer>/` shape. Nothing
   installs from `docs/`.
7. **`skaile.yaml` ships no `assets:` block and no `skaile.manifest.yaml`** — glob discovery,
   with the reasoning recorded as a comment in the file itself.
8. **No `DOMAIN.md` anywhere**, per ticket 05.

### The frontmatter question the ticket raised

Ticket 09 answered it: **`inputs_optional` stays in frontmatter.** Moving the input-dialog
specs to a sibling `inputs.yaml` costs a forge-concept edit, which the map rules out. So the
skeleton needs nowhere to put them and concept-side frontmatter stays ~15 lines.

### ADRs seeded

`0001` name-is-identity · `0002` flat tree + nine domains · `0003` skill body shape ·
`0004` contracts earn their place — from tickets 01/04, 04, 03 and 09 respectively. Tickets
05 and 06 have not been turned into ADRs yet; they are glossary and domain-shape decisions
that the port tickets will exercise first.

### Unblocked

**14: Port the mockup domain** — the only ticket that was waiting on this one.

## Note from ticket 05

- **`CONTEXT.md` is ready** — `.scratch/skaileup-mp/CONTEXT.md`, 139 lines. Drop it into
  the skeleton verbatim; ticket 05 is no longer a dependency.
- **No `DOMAIN.md` files** in the skeleton — all 16 are ruled out.
- **Add `docs/adr/`**, seeded from tickets 01–04, which all clear the 3-test gate. This
  is where the map's decisions live once the map itself ends.
- The onboarding artifacts to lay down are **one `onboarding.yaml`**, not
  `profile.yaml` + `decisions.yaml`.
