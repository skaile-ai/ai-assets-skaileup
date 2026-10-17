# The node template — the instruction for one `_concept/` part

`tree/` mirrors `_concept/` entry for entry. A node is the one place that says what a part
is, how it is written, and when it is done. Skills are routes through nodes (see
[`skill-template.md`](./skill-template.md)); nothing else holds instructions.
[ADR 0015](./adr/0015-the-instruction-tree-mirrors-the-artifact-tree.md) has the reasoning.

## Where a node lives (R1)

| `_concept/` thing | node file, relative to the tree root `tree/` |
|---|---|
| directory `X/` | `X/README.md` (also the node of `X/README.md` if that artifact exists) |
| file `X/name.ext` | `X/name.md` — extension always `.md` (`tokens.json` → `tokens.md`, `stories.yaml` → `stories.md`) |
| placeholder segment `<x>` | `[x]` in the node path, e.g. `05_features/[featureset]/[feature].md` |
| several siblings sharing a stem, or placeholder children a directory README covers | one node whose frontmatter `path:` is a **list** |

Resolution of a `_concept/` path: first a literal match against any node's `path:` entries
(`<x>` placeholders match any one segment), then the location rule for directories only (a
directory resolves to its `README.md`; a file resolves only through a `path:` entry, which every
file node carries). A path below a directory entry of a list-form `path:` resolves to that README. Nothing else
resolves. Node names are lowercase; every directory under `tree/` has a `README.md`.

## The shape (R2)

Frontmatter, then these sections in this order, empty sections omitted. Between `## Format`
and `## Writing it` a node may carry further named `##` sections (see below):

```markdown
---
path: _concept/03_brand/identity.md      # string or list; every entry is under this node's directory
summary: colours, fonts, tone of voice and copy guidelines     # ≤ 80 chars; rendered into the tree listing
writers: [design-brand]                  # skills whose `produces` resolve here; [] when nothing generates it
---

# _concept/03_brand/identity.md

<One paragraph: what this is, who reads it, what breaks downstream when it is wrong.>

## Format
<Frontmatter fields, body sections or schema, one minimal example.>

## <Reference section, e.g. Naming>
<Optional. Reference material other nodes cite by `§`.>

## Writing it
<Numbered procedure. Multi-writer nodes: one `### <role> (<skill>)` subsection per writer.>

## Checks
<What "done" means for this part; validator commands if any.>
```

- A directory README titles itself `# _concept/<dir>/`; its first `path:` entry is the
  directory with a trailing slash. `## Contents` lists the children that have no node of
  their own, one line each. `## Writing it` appears only when the directory is produced as a
  whole (`findings/`, `walkthrough/`).
- **Named reference sections.** A node may carry additional `##` sections between
  `## Format` and `## Writing it`. Each holds reference material that other nodes or skills
  cite by `§` — for example `## Naming` (`10_blueprint/datamodel/README.md`), `## Verdicts`
  (`11_build/README.md`), `## Manifest schema` (`09_mockup/walkthrough/README.md`). Name the
  section for what it holds, so the `§` citation reads as a sentence. Procedure for a
  skill-specific use stays in `## Writing it`.
- `writers` is exactly the set of skills whose `produces` resolve to this node, and every
  writer has a `produces` entry that resolves here (or sits above or below it); `[]` means
  nothing generates the part.
- Cite another node by its repo-relative path under `tree/`, optionally followed by
  ` § <heading>` for one `##`/`###` heading of it, one citation per line. Cite a skill's own
  tooling as `skills/<name>/…`.

## Compression policy

Every node and every skill body follows it. The aim is the shortest text that leaves the
agent doing exactly the same thing.

**Keep, always:** every path, key, enum value, schema, command, gate and its hard/soft kind,
step order, every branch ("when X exists… otherwise…"), every hand-off naming another skill,
every `Call the Skill tool with "…"` sentence and its absent-skill fallback, every
"Done when".

**Per rule, keep at most one consequence clause** — the one naming what breaks downstream
("…or the walkthrough renders a bland default").

**Drop:** a second example; history ("the old collection…", ticket numbers, ADR references
inside nodes); Wrong/Right dialogue samples; text that restates another node; `MUST`/`NEVER`
lists — rewrite those as positive sentences at the step they bind.

A sentence whose removal would change what the agent *does* is never dropped. When unsure,
keep it and note the node path and sentence for review.

**Expected size:** nodes of 40–150 lines are typical. Verbatim schemas and the generated
tree fence in `tree/README.md` are excluded from the count, so the nodes that carry them may
run longer — `tree/README.md`, `tree/09_mockup/walkthrough/README.md`,
`tree/09_mockup/feedback/patches/README.md`, and `tree/07_screens/README.md` (the
`elements:` block). A node over 150 lines after that exclusion is a sign it holds two parts.
