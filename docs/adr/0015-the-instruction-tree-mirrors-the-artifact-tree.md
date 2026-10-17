# 0015 — The instruction tree mirrors the artifact tree; a skill is a route

**Status:** accepted

Supersedes [ADR 0003](0003-skill-body-shape.md) (skill body shape) and
[ADR 0004](0004-contracts-earn-their-place.md) (contracts earn their place). Builds on
[ADR 0007](0007-one-numbered-artifact-tree.md): the artifact tree stays as it is; the
instructions for it now take its shape.

## Context

`ai-assets-skaileup-mp` keeps its instructions in two places: ~90-line `SKILL.md` bodies,
about half of it rationale, and thirteen cross-cutting contract files that several skills
cite. A rule about one `_concept/` part is therefore spread over a skill, a contract, and
sometimes a second contract. Three things in `-mp` show what that costs:

- The contract on golden principles demands `01_` prefixes on featureset folders and
  `snake_case` filenames; the contract on the canonical tree says no prefixes below the first
  level and hyphenated names. Both are "contracts"; a skill reading the wrong one writes a
  path the checker rejects.
- `quality-release` produces `_concept/11_build/release.yaml`, a file the canonical tree
  fence never lists. The fence is hand-written and nothing derived it from what skills write.
- Two sections of the agent-patterns contract (standalone mode, completion summary) have no
  citing skill — a rulebook can hold a rule nothing reads.

Cross-cutting rulebooks drift because no single part owns them. A rule that lives at the part
it binds cannot drift away from that part.

## Decision

**R1 — Mirror.** A directory `tree/` mirrors `_concept/` entry for entry. The node for a
`_concept/` directory `X/` is the file `X/README.md` inside it; for a file `X/name.ext` it is
`X/name.md` (extension always `.md`); a placeholder segment `<x>` becomes `[x]` in the
node path. Several siblings that share a stem, or placeholder children a directory README
covers, share one node whose frontmatter `path:` is a list. Resolution of any `_concept/` path
is a literal match against the nodes' `path:` entries first (`<x>` matches one segment), then
the location rule above; nothing else resolves.

**R2 — Node.** Every node is markdown with frontmatter `path`, `summary` (≤ 80 chars) and
`writers` (the skills whose `produces` resolve to it), then in order: an intro paragraph,
`## Format`, `## Writing it`, `## Checks`, empty sections omitted. All format, procedure and
check text for a part lives in its node and nowhere else. Rationale is compressed to at most
one consequence clause per rule. See [`../node-template.md`](../node-template.md).

**R3 — Route.** A `SKILL.md` keeps its machine-layer frontmatter unchanged and its body
becomes a route: the ordered list of nodes it visits, at most 60 lines in all. The six skills
with `produces: []` have no node of their own to point at, so they keep a compressed
`## Steps`, at most 100 lines. See [`../skill-template.md`](../skill-template.md).

The tree is the one dir-scoped contract asset, `shared-contracts`: hosts and flows see the
same asset as in `-mp`, with different contents. `scripts/check.py` derives the canonical
`_concept/` tree from the nodes' `path:` entries (`--print-tree`) instead of a hand-written
fence, and fails when `tree/README.md`'s copy of it is stale. It also requires every skill
`produces` path to resolve to a node that lists the skill as a writer, and every node writer
to have a matching `produces` entry.

## Consequences

- A rule lives once, at the part it binds. Adding a `_concept/` entry means adding a node;
  nothing else holds the list.
- Cross-cutting rulebooks cannot exist: a topic that spans parts is stated at each part it
  binds, in one clause, or lives in `tree/README.md` when it is about the tree itself.
- The `release.yaml` class of drift becomes a gate failure: a produced path with no node, or
  a node whose writer does not declare it, fails the check.
- Skill bodies shrink to the order of work. A skill's behaviour is only fully readable
  together with its nodes; the route's citations are checked to resolve.
- ADR 0003's 140-line ceiling and ADR 0004's "read in-body" bar no longer apply. Their
  positive-constraints rule survives as the compression policy in the node template.
- Profiles become a table in the scope node; the per-type data has no readers at runtime, so
  no behaviour is lost.
