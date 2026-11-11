# 0034 — The tree's protocol lives beside it in `tree/protocol/`

**Status:** accepted

Amends [ADR 0017](0017-the-instruction-tree-mirrors-the-artifact-tree.md): `tree/` holds one
directory that mirrors no `_concept/` part.

## Context

Every skill route opened with "Read `tree/README.md` once per session". The file had grown to
27.8 KB, the largest thing any run read. Most of it was not about the artifact tree:
ownership and proposed entries, how a skill runs, the delegation protocol and the artifacts
beside the tree were cross-cutting rules that every run loaded whole, whether it delegated,
proposed or did neither.

## Decision

`tree/README.md` keeps what describes `_concept/` itself: the rule, the generated tree fence,
numbering, naming, the universal frontmatter, the arc42 map and the fixed `_concept/README.md`
pointer. The cross-cutting rules move, verbatim, to `tree/protocol/`:

| file | holds |
|---|---|
| `ownership.md` | owners, `may_propose`, proposed entries |
| `running.md` | how a skill runs, rules 1–8 |
| `delegation.md` | the status block, the interview relay, parallel runs |
| `beside-the-tree.md` | `APP-DESIGN.md` and the other root artifacts, the rulebook |

A route names only the protocol files and rules it uses
(``Read `tree/protocol/running.md` (rules 1, 2, 8), then these nodes in order``). `protocol/` is
shipped with the `shared-contracts` asset, carries no node frontmatter and is exempt from the
mirror rule, as `CONTRACT.md` is. Its `§` citations are checked like any other tree citation.

## Options rejected

- **One protocol file.** Cuts the read for no route: every route needs `running.md`, few need
  delegation.
- **Protocol as nodes with `path:`.** They mirror nothing in `_concept/`; a fake path would
  break the resolution rule.

## Consequences

- `tree/README.md` shrinks to ~16 KB, of which the generated fence is ~9.5 KB.
- `check_tree` skips `tree/protocol/`; `_check_tree_citations` resolves its `§` citations.
- A new cross-cutting rule goes into one protocol file and is cited, never restated.
