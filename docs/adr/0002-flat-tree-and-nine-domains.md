# 0002 — Flat tree; the domain lives in the name

**Status:** accepted

## Context

17 numbered domain folders, names up to five segments deep, and a renumbering ritual on
every insert. Given ADR 0001 — that `name:` is the identity — the folder hierarchy was
carrying cost without carrying meaning.

## Decision

`skills/<name>/SKILL.md`, flat, with **the directory name equal to `name:` character for
character**. No `NN_` prefixes anywhere: order lives in the flow graph, which is the actual
source of order. Root hoists to `skills/` · `flows/` · `contracts/` · `docs/`.

Nine domains, carried as the name's first segment:
**`concept · design · experience · spec · mockup · architecture · build · quality · ops`**.

- `discovery` → `concept` (the sub-part shouldn't split from `_concept/`, the tree it writes)
- `product-spec` → `spec`
- `concept-slice` → **`spec`** — it authors feature and screen specs
- `impl-plan` + `impl-slice` → **`build`**
- The `quality`/`ops` line is **the artifact under inspection**: `quality` checks `src/`,
  `ops` checks `_concept/`.

Names are `domain-skill`: 2 segments by default, 3 for a genuine sub-cluster, never 4.
Separator `-`, never `_` (a `_` directory could never equal its `name:`).

Absorbed general-purpose skills all take a domain prefix. The argument is collision, not
taste: a bare `research` installs to the same path as the global install and clobbers it.

## Consequences

- `spec-` and `build-` are not in forge-concept's name-prefix fallback list, so those lanes
  break unless flows declare `data.phase` — which ADR 0001 requires anyway. Accepted.
- The `skillOwnsSubfolder` rule (a renderer skill's name must end with its output subfolder)
  is reached only through the unreachable `artifacts.yaml`, so it constrains nothing.
