# 0001 — A skill's `name:` is its whole identity

**Status:** accepted

## Context

The old collection encoded identity in four places at once: the directory path (with `NN_`
run-order prefixes), the flow node's `data.skill`, `artifacts.yaml`'s `produced_by`, and the
grounding input path. All 95 skills had a `name:` that differed from their parent directory,
so the nesting did not merely fail to carry identity — it drifted from it.

## Decision

One string, `name:`, fills every role: install path (`.claude/skills/<name>/`), flow node
reference, and grounding key. Directory paths and domain foldering carry no meaning and are
free to change.

The live machine contracts are: the flow contract (`<id>.flow.yaml` in a directory named
`<id>`, kept only with `id` + `nodes` + `edges`; top-level `requires:` drives transitive
install) and the frontmatter fields forge-concept actually reads — `version`,
`artifacts.requires[].id`, `prerequisites.*`, `requires`. Everything else in frontmatter is
documentation. (Where those fields sit is narrowed by
[ADR 0011](0011-the-machine-layer-sits-under-metadata.md): under `metadata:`, paths prefixed
`_concept/`.)

## Consequences

- `artifacts.yaml` is **unreachable as deployed** — it is read only under `--link`, and the
  default copy install leaves the recursive search finding nothing, with forge-concept
  silently falling back to session completion. It does not come across (see ADR 0004).
- `skaile.yaml`'s `assets:` block is dead, and newer `@skaile/workspaces` throws on it.
  `-mp` ships none.
- forge-concept's lane assignment keys off `data.phase` first and skill-name prefixes only
  as a fallback, so `-mp` flows declare `phase` on every node.
