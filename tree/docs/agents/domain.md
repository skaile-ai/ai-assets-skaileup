---
path: docs/agents/domain.md
summary: the guidance section that points upstream engineering skills at the concept
owner: [skaileup]
may_propose: []
---

# docs/agents/domain.md

The file upstream `setup-matt-pocock-skills` writes at the project root to tell the engineering skills (`to-tickets`, `implement-spec`, `tdd`, `code-review`, `diagnosing-bugs`, `domain-modeling`, `triage`) where the domain docs live; those skills read only this folder and the `## Agent skills` block of `CLAUDE.md` or `AGENTS.md`, never `_concept/` or the tree. `skaileup` owns one section of it, `## skaileup artifacts`, which names every concept artifact the project has, so those skills find the specs, decisions, glossary and contracts unmodified (`tree/protocol/beside-the-tree.md`). The rest of the file is upstream's and skaileup never edits it. A missing or stale section means a build run plans and codes against the code alone, and a `status: proposed` entry or a superseded record gets built as if it were settled.

## Format

The section, appended after upstream's content, with fixed headings, one bullet per artifact, only the artifacts that exist in the project, and every path relative to the project root:

```md
## skaileup artifacts

This project's concept lives in `_concept/` (skaileup). Read before working on a feature:

- **Specs**: `_concept/05_features/<featureset>/<feature>.md`; `tracker.issue` in its frontmatter is the spec's parent issue.
- **Glossary**: `GLOSSARY.md` (words); `_concept/glossary.md` (ontology: kinds, is-a, relations).
- **Decisions**: `docs/adr/` (frontmatter `level`/`kind`; a `pattern` binds every later feature it `applies_when`).
- **Interaction rules**: `APP-DESIGN.md`.
- **API contracts**: `_concept/10_blueprint/openapi.yaml`, `asyncapi.yaml`.
- **Data model**: `_concept/10_blueprint/datamodel/model.yaml`, `seed.yaml`.
- **Instruction nodes**: `<contracts>/shared-contracts/` (the node at the same path as a `_concept/` file says its format and owner).
- **Pending proposals**: `_concept/proposals/` — a `status: proposed` entry is not yet true; do not build on it.
```

A bullet whose artifacts are all absent is left out; a bullet with one of two files names only the one that exists. `<contracts>` is written out as the harness's contract directory (`.agents/contracts` or `.claude/contracts`, whichever exists). The **Glossary** bullet names the glossary files the project has (`tree/glossary.md § Where the words live`).

**The sub-block.** In the `## Agent skills` block of whichever of `CLAUDE.md` and `AGENTS.md` upstream setup chose, one sub-block after upstream's own:

```md
### Concept (skaileup)

Specs, decisions, glossary and contracts from the skaileup concept. See `docs/agents/domain.md § skaileup artifacts`.
```

That file is project code, like the walkthrough section `skaileup` keeps there (`tree/01_meta/walkthrough.md`): the sub-block is written by this node's procedure and listed under no skill's `produces`.

## Writing it

### Setting it up (`skaileup`)

1. **On the first build-side demand.** When the want resolves to a `build-*`, `quality-review` or `quality-test` skill as the next run and `docs/agents/domain.md` has no `## skaileup artifacts` section, this procedure runs before that skill. A section already present skips to step 4.
2. **Run upstream setup.** Read the installed `setup-matt-pocock-skills` skill and follow it, taking the recommended answer for each of its sections: the GitHub tracker when the remote is GitHub, the default triage labels, single-context domain docs. The lead asks the user only where `_concept/01_meta/expectations.md` says the user decides (`tree/01_meta/expectations.md § Reading it`); every other recommended answer is taken without a batch, because the concept already settled what setup would ask. Where the skill is not installed, name it to the user and write steps 3 and 4 into a `docs/agents/domain.md` of its own, so the section exists when setup runs later.
3. **Write the section.** Build it from what exists on disk per `## Format` and append it to `docs/agents/domain.md`, after upstream's content.
4. **Write the sub-block** into the `## Agent skills` block per `## Format`, once; a sub-block already there is replaced in place, so a rerun leaves one.

### Refreshing it (`skaileup`)

Every `skaileup` run that leaves a different set of artifacts on disk than the section lists — a first `GLOSSARY.md`, a first record in `docs/adr/`, the contracts or the data model arriving — rewrites the whole section from `## Format`. The rewrite is idempotent: the same artifacts give the same section, and nothing outside the section changes.

## Checks

- `docs/agents/domain.md` holds exactly one `## skaileup artifacts` section, after upstream's content, with the intro line and bullets of `## Format` in its order.
- Every path the section names exists in the project; every artifact of `## Format` that exists is named.
- The `## Agent skills` block of the chosen agent file holds exactly one `### Concept (skaileup)` sub-block.
- Nothing outside the section and the sub-block changed in a skaileup run.
