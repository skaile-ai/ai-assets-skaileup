# 0013 — A skill declares what it produces

**Status:** accepted; amended by [0019](0019-scoped-fact-resolution.md) — the flow-walking producer check becomes "every hard gate is produced or a root prerequisite"

Extends [ADR 0004](0004-contracts-earn-their-place.md)'s rule that machine-read data lives in
`SKILL.md` frontmatter. Builds on [ADR 0011](0011-the-machine-layer-sits-under-metadata.md)'s
`metadata:` placement.

## Context

A skill declares what it **needs** — `prerequisites.files[]` with a gate strength, and
`artifacts.requires[].id` — but nothing declares what it **writes**. The only record of a
skill's output is prose in its `Done when` list. Three things follow from that.

- **`check.py` cannot see a gate nothing satisfies.** A `hard` prerequisite on
  `_concept/04_journeys/stories.yaml` in a flow where no upstream node writes that file passes
  every rule, because there is no producer list to compare it against. Three of four flows
  contained exactly that gate.
- **`artifacts.requires[].id` points at ids nobody defines.** ADR 0011 left `requires[]` as
  `{id}` only, "for cycle detection over edges whose targets are artifact ids". The ids are
  conventions; no declaration says which skill owns one, so a typo resolves to nothing and
  raises nothing.
- **The editor's done-state is read from a file this repo dropped.** The host forge derives a
  node's done state from `contracts/artifacts.yaml`: `artifact-contract.ts:150-152` loads each
  entry's `path` and takes `produced_by[0]` as the canonical producer. ADR 0004 deleted that
  registry, so the editor has nothing to read.

## Decision

**Every skill that writes under `_concept/` declares `metadata.artifacts.produces: [{ id,
path }]`.**

- `id` is the artifact id other skills name in `metadata.artifacts.requires[].id`. The two
  lists now close over each other: every `requires[].id` resolves to some skill's
  `produces[].id`.
- `path` starts with `_concept/` (ADR 0011) and appears in the tree fence of
  `contracts/concept_structure.md`. A directory path matches by prefix; a file path matches
  exactly. `scripts/check.py` already parses that fence.
- `scripts/check.py` validates all three: `produces` is present and non-empty for every skill
  that writes under `_concept/`, each `path` is in the tree, each `requires[].id` resolves.
  The key needs its own rule because `check.py` has no allowlist of `metadata` keys — an
  undeclared key passes silently today.

**No registry is generated.** There is no `contracts/artifacts.yaml`, and none is built from
the frontmatter. ADR 0004 stands: machine-read data lives where forge-concept already reliably
looks, and the frontmatter is the single source.

**The host's `produced_by` read is a named external dependency.** The host will derive done
state from `produces` only when `artifact-contract.ts` is changed to read it; until then the
editor's done-state stays as it is, and this record does not claim to fix it. The dependency is
tracked rather than remembered: a `scripts/host_facts.py` row on the `produced_by` read in
`artifact-contract.ts`, checked by `scripts/verify_host.py`. It reports `HOLDS` while the host
still reads the registry. The day the host switches, it reports `EXPIRED`, and that is the
signal that the editor can be pointed at `produces`.

## Alternatives

**Generate `contracts/artifacts.yaml` from the frontmatter.** It would give the editor its
done-state today without a host change. Rejected: ADR 0004 dropped the registry because a
second copy of machine data drifts, and a generated copy needs its own freshness rule — a
check that the file matches the frontmatter, and a step that regenerates it — to remain
honest. That trades a missing feature for a standing maintenance obligation, and the host has
to change eventually either way.

## Consequences

- **The host's done-state stays broken** until the host reads `produces`. The `host_facts` row
  keeps that visible; it does not close it.
- A skill that writes an artifact must also declare it, and the declaration is the place the
  artifact's id is born. Renaming an id is a repo-wide edit that `check.py` now catches.
- `produces` makes flow-level checking possible: walking a flow's edges and accumulating
  `produces[].path` answers "does any upstream node write this hard gate?". That rule lands
  as its own check after the flows are reordered.
- `docs/skill-template.md` gains the block. Skills that write nothing under `_concept/`
  (the build and quality skills that touch only `src/` and git) declare none and are exempt
  from the presence rule.
- No second source of artifact paths exists: `concept_structure.md` owns the tree, and each
  `produces` entry is validated against it rather than restating it.

---

**`produces` paths amended by [ADR 0015](0015-interaction-decisions-live-in-app-design.md)**
(2026-10-17). A `produces` path need not start with `_concept/` when it is named in
`check.py`'s `PROJECT_ROOT_ARTIFACTS` — today `APP-DESIGN.md` at the project root, written by
`experience-interaction`. A host that reads `produces` must join that path to the project
root, not to `_concept/`.

**Host dependency resolved** (2026-10-18). skaile-forge reads `produces` directly:
`server/utils/skill-produces.ts` (`isNodeFileComplete`) counts a node as done when every
non-templated path in its skill's list exists, and joins `APP-DESIGN.md` to the project root.
`artifact-contract.ts` and its `produced_by` read are gone. The `host_facts.py` row is now
`host:node-done-from-produces`, anchored on the new read. The change was made on forge's
`feat/cfc-concept-formats-cutover` branch; the row is correct for forge `main` once that
branch is merged.
