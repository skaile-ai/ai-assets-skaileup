# 04: Naming scheme and the domain set

**Type:** grilling
**Blocked by:** None (01 resolved)
**Status:** resolved

## Question

Lock the shape of the tree before anything is ported into it.

**What ticket 01 settled, so don't re-litigate it:** skill identity is the `SKILL.md` `name:`
field and nothing else — directory paths, `NN_` prefixes and domain foldering are **free**.
`name` must match `/^[a-z0-9]+(?:-[a-z0-9]+)*$/`, and one `name` fills four roles at once:
install path (`.claude/skills/<name>/`), a flow node's `data.skill`, an `artifacts.yaml`
`produced_by` value, and the grounding input path `_concept/_grounding/<name>/input.json`.

**The one real constraint on this ticket:** forge-concept assigns sidebar lanes by **name
prefix** — `concept-` / `design-` / `experience-` / `product-spec-` / `mockup-` / `impl-` /
`quality` — and by `data.phase` ∈ {conceptualization, implementation, review}. Renaming a
domain prefix silently breaks its lane. Since cutover is out of scope this isn't fatal, but
the choice should be deliberate: keep the seven prefixes, or accept the breakage and record it.

- **Ordering prefixes.** Today every domain and skill folder carries `NN_`, with `name:`
  derived by stripping it — an invention that keeps alphabetical listing in flow order but
  costs a renumbering ritual on every insert. mp is flat. Keep `NN_`, drop it, or keep it on
  domains only?
- **The ~9 domains.** Proposed: `discovery · design · experience · product-spec · mockup ·
  architecture · build · quality · ops`. Are those the right nine, are those the right names,
  and where do the three slice clusters land?
- **`featureset`.** Named as a wanted concept. Today it's the `NN_group/` folders inside
  `product-spec/features`. Is it a level in the vocabulary, a domain, or just a folder?
- **Skill naming.** `domain-skill` (`concept-brief`, `impl-slice-implement`) is today's
  scheme, and ticket 01 says how much of it is load-bearing. Keep it, or go flat like mp?
- **Where the absorbed mp skills sit** — do they get a domain of their own, or join existing ones?

## Answer

**The tree is flat; the domain lives in the name, not the filesystem.**

### 1. Layout — flat, `dir == name:`

```
skills/<name>/SKILL.md     # one dir per skill, no nesting, no NN_
flows/<id>/<id>.flow.yaml
contracts/
docs/
```

The `skaileup/` container is hoisted away (redundant level inside a repo already
called `ai-assets-skaileup`); flow discovery walks for `<id>/<id>.flow.yaml` at
arbitrary depth (`flow-manager.ts:165`), so moving flows is safe.

**Directory name equals the `name:` field, character for character.** Today
**95/95 skills have `name:` != parent dir** — the nesting doesn't merely fail to
carry identity, it drifts from it. Flat collapses four strings into one: dir,
install path (`.claude/skills/<name>/`), flow `data.skill`, and grounding input
path (`_concept/_grounding/<name>/input.json`).

Separator is `-`, not `_`: `name:` must match `/^[a-z0-9]+(?:-[a-z0-9]+)*$/`, so a
dir with `_` could never equal its name. `-` groups and sorts identically in a flat
listing, so `_` buys nothing and costs the invariant.

**`NN_` prefixes are dropped everywhere.** Ordering lives in the flow graph, which
is the actual source of order; the renumbering ritual on every insert was pure cost.

### 2. The nine domains

`concept · design · experience · spec · mockup · architecture · build · quality · ops`

Two renames off the charting proposal: `discovery` -> **`concept`** (naming a sub-part
"discovery" splits the word from `_concept/`, the tree it writes) and `product-spec`
-> **`spec`**.

The three slice clusters land by what they produce:

- `08_concept-slice` (brainstorm/align/scope-feature/design-feature) -> **`spec`**.
  It is per-feature spec authoring: it writes feature.md and screen specs.
- `11_impl-plan` (4) + `12_impl-slice` (8) -> **`build`**.

The **`quality` / `ops` line is drawn at the artifact under inspection**: `quality`
checks the built **code** (tests, standards, code review); `ops` operates on the
**concept repo itself** (sync, cross-ref integrity, trace, reverse-engineer,
multi-product overview). Reviewing `_concept/` is `ops`; reviewing `src/` is `quality`.

### 3. Skill naming — `domain-skill`, 2 segments, ceiling 3

Every skill carries its domain as the first segment. Depth is **2 by default, 3 only
where a domain has a genuine sub-cluster** (`mockup-storybook-components`,
`build-slice-implement`), **never 4**. Today's depth histogram is 1x1 / 12x2 / **53x3**
/ 28x4 / 1x5 — the 4-segment names exist because domains were over-nested, and the
consolidation removes the cause. A hard ceiling of 3 is checkable.

### 4. `featureset` is a level in the vocabulary

Not a domain, not a skill boundary, not just a folder: a **named grouping of features**
that `spec` writes and the slice loops iterate over. It earns a glossary entry
(ticket 05) and a stable path convention, nothing more.

### 5. Where the absorbed mp skills sit — all prefixed, no exceptions

The deciding argument is **collision, not taste**: a bare `research` or `grilling`
installs to `.claude/skills/research/`, the same path as the global mattpocock install,
and the two clobber each other.

- `to-spec` -> `spec-*`
- `to-tickets` -> `build-*`
- `grilling`, `research` -> `concept-*` (`concept-research` is nearly free today; only
  `concept-grounding-research` exists)
- the `ask-matt`-style router -> keeps the bare `skaileup` orchestrator name it has

### 6. The lane constraint was weaker than this ticket assumed

`forge-concept/shared/flow-phases.ts:35-41` — `phaseForNode` takes an explicit
`data.phase` **first**; the name-prefix list (`CONTEXT_PREFIXES`, `:18`) is only a
**fallback** for flows that omit it. 11 of 19 current flows already emit `phase:`.
Sidebar *domain* grouping is separate again: it comes from `flow.metadata.category`
(`flow-manager.ts:145-151`), and today's categories in the wild (`full-stack`,
`incremental`, `maintenance`) match none of its three cases, so every flow already
falls into one bucket.

**Decision: `-mp` flows declare `data.phase` on every skill node or group container.**
That is ~1 line per node and it converts the ticket's "one real constraint" into a
non-constraint — the domain set is chosen on merit. Five of the seven old lane
prefixes (`concept-`, `design-`, `experience-`, `mockup-`, and `quality` by substring)
survive anyway as belt-and-braces; `spec-` and `build-` deliberately do not, and
that breakage is accepted and recorded here.

**One naming rule this ticket did not list, now dead:** `skillOwnsSubfolder`
(`flow-manager.ts:412-422`) requires a renderer skill's name to *end with* its output
subfolder name. It is reached only via `getArtifactsProducibleBySkill` ->
`artifacts.yaml`, which ticket 01 found unreachable as deployed. It constrains nothing
unless ticket 09 revives the registry — relevant to ticket 06 making the renderer a
parameter rather than five sibling skills.
