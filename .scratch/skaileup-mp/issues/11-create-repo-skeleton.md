# 11: Create the repo and its skeleton

**Type:** task
**Blocked by:** None (03, 04 resolved)
**Status:** ready

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

_(pending)_

## Note from ticket 05

- **`CONTEXT.md` is ready** — `.scratch/skaileup-mp/CONTEXT.md`, 139 lines. Drop it into
  the skeleton verbatim; ticket 05 is no longer a dependency.
- **No `DOMAIN.md` files** in the skeleton — all 16 are ruled out.
- **Add `docs/adr/`**, seeded from tickets 01–04, which all clear the 3-test gate. This
  is where the map's decisions live once the map itself ends.
- The onboarding artifacts to lay down are **one `onboarding.yaml`**, not
  `profile.yaml` + `decisions.yaml`.
