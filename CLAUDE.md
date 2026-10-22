# ai-assets-skaileup-tree

The skaileup collection as a **mirror tree**: the same ~9 domains as
[`ai-assets-skaileup-mp`](https://github.com/skaile-ai/ai-assets-skaileup-mp), 31 skills, but the
instructions live in `tree/` — a directory that mirrors `_concept/` one node per part — and
a skill is only the route through those nodes. `-mp` stays live and untouched; projects opt
in via `skaile.yaml`.

## The invariants

- **`skills/<name>/SKILL.md`, flat.** The directory name equals the `name:` field
  character for character. That one string is the install path, the flow node's
  `data.skill`, and the grounding input path. No `NN_` prefixes, no domain folders — the
  domain is the name's first segment.
- **Nine domains:** `concept · design · experience · spec · mockup · architecture ·
  build · quality · ops`. `quality` inspects `src/`; `ops` inspects `_concept/`.
- **Names are `domain-skill`** — 2 segments by default, 3 for a real sub-cluster, never 4.
  Separator `-`, never `_`.
- **Order is advisory.** Flows are recipes whose edges suggest an order and gate nothing
  ([ADR 0023](./docs/adr/0023-two-advisory-flows.md)); no skill's prose restates one. Which
  skill to run and what it still needs is resolved on demand by `skaileup`, the router, never
  by the filesystem.
- **The tree mirrors `_concept/` and holds all instruction.** Every `_concept/` part has one
  node under `tree/`: directory `X/` → `X/README.md`, file `X/name.ext` → `X/name.md`,
  placeholder `<x>` → `[x]`; the one project-root artifact, `APP-DESIGN.md`, has the node
  `tree/APP-DESIGN.md`. Purpose, format, procedure and checks live in
  that node and nowhere else; the one cross-cutting asset is `rulebook/` — the app-design
  rules, defaults and floorplans, a second contract
  ([ADR 0018](./docs/adr/0018-the-rulebook-is-a-second-contract-asset.md)). Resolution rules:
  [ADR 0017](./docs/adr/0017-the-instruction-tree-mirrors-the-artifact-tree.md) and
  `tree/README.md`.
- **A skill is a route.** Its body is the ordered list of nodes it visits — at most 60 lines
  including frontmatter; the five skills with `produces: []` keep a compressed `## Steps`, at
  most 100. See [`docs/skill-template.md`](./docs/skill-template.md).
- **A node follows one shape**: frontmatter `path` / `summary` / `owner` / `may_propose`, then intro,
  `## Format`, `## Writing it`, `## Checks`. No `MUST`/`NEVER` block — constraints are stated
  positively at the step they bind, one consequence clause per rule. See
  [`docs/node-template.md`](./docs/node-template.md).
- **Frontmatter carries only what a machine reads**: `version`, `artifacts.requires[].id`,
  `prerequisites.*`, `requires`. Everything else is documentation and belongs in the body.
  The machine layer sits **under `metadata:`** and its paths start with **`_concept/`** —
  that is where the readers look, and neither failure raises ([ADR 0011](./docs/adr/0011-the-machine-layer-sits-under-metadata.md)).
- **Flow nodes declare `data.phase`** rather than relying on forge-concept's name-prefix
  fallback.
- **Two `CONTRACT.md` manifests**: `tree/CONTRACT.md` (`shared-contracts`) and
  `rulebook/CONTRACT.md` (`app-design-rulebook`). `@skaile/workspaces` discovers each recursively
  and ships its whole directory as one asset; a third is rejected.

## The gate

**Green means `python scripts/check.py`, and that is the whole gate.** It checks the
collection and then runs its own fixtures; nothing else needs running, and a run with
`--no-tests` is not a green one. This repo has no build and no runtime, so that script is
the only thing that can tell you the collection still hangs together — forge-concept
validates no flow at all and reports a missing skill as `satisfied: true`.

`python scripts/check.py --print-tree` prints the artifact tree generated from the nodes'
`path:` entries. Paste it into the fence in `tree/README.md` when a node is added or moved;
the gate fails while the two differ.

**A push is not finished until its run is green.** The failure mail arrives, but it arrives
in an inbox rather than in the session that caused it — two red runs once sat on `main` for
~13 hours that way.

Pin the watch to your own commit. A bare `gh run watch` takes the latest *registered* run,
which is still the previous commit's for the first seconds after a push, and then reports
that one's green as yours:

```sh
SHA=$(git rev-parse HEAD)
until RUN=$(gh run list --limit 5 --json databaseId,headSha \
      -q ".[] | select(.headSha==\"$SHA\") | .databaseId" | head -1); [ -n "$RUN" ]; do sleep 3; done
gh run watch --exit-status "$RUN"
```

## The vocabulary

[`CONTEXT.md`](./CONTEXT.md) is the collection's glossary and nothing else — no paths, no
process. Use its words; don't redefine them locally. Where a thing *lives* is `tree/README.md`'s
job.

Two words that are easy to get wrong: an **asset** is shipped by this repo; an **artifact**
is written into a project. A **slice** is a vertical slice, implementation-side only — the
concept-side per-feature thing is a **feature dossier**.

## Decisions

[`docs/adr/`](./docs/adr/) holds the decision records this collection was built from.
Read them before re-litigating shape questions. ADR 0017 supersedes 0003 and 0004.
