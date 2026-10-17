# Decision records

The decisions this collection was built from. Each one was worked as a ticket on the
migration map (`.scratch/skaileup-mp/` in the old repo); these are the durable form, kept
here once the map ends. 0001–0014 are carried over from `ai-assets-skaileup-mp`; 0015 is
where this variant departs from it.

A decision earns a record here when it passes three tests: it constrains future work, it
was expensive to reach, and reversing it would cost more than reading it.

| ADR | Decision |
|---|---|
| [0001](./0001-skill-name-is-the-identity.md) | A skill's `name:` is its whole identity |
| [0002](./0002-flat-tree-and-nine-domains.md) | Flat tree; the domain lives in the name |
| [0003](./0003-skill-body-shape.md) | 140-line ceiling, no `MUST`/`NEVER` block — superseded by 0015 |
| [0004](./0004-contracts-earn-their-place.md) | A contract survives only if it is read in-body — superseded by 0015 |
| [0005](./0005-warm-and-cold-session-boundaries.md) | Two session boundaries, warm and cold; no slash commands |
| [0006](./0006-the-slice-loop-composes.md) | The slice loop is four skills that compose global ones |
| [0007](./0007-one-numbered-artifact-tree.md) | One numbered artifact tree under `_concept/` |
| [0008](./0008-gates-live-at-the-step-they-bind.md) | A gate lives at the step it binds; no file collects gates |
| [0009](./0009-stack-knowledge-lives-in-templates.md) | Stack-specific knowledge lives in a template, not a skill |
| [0010](./0010-no-plan-file-and-no-status-file.md) | The build side keeps no plan file and no status file |
| [0011](./0011-the-machine-layer-sits-under-metadata.md) | The machine layer sits under `metadata:`; paths carry `_concept/` |
| [0012](./0012-foreign-skills-and-the-two-libraries.md) | Five foreign skills stay global, called one gate-checked way; what came from pstack and Pocock |
| [0013](./0013-a-skill-declares-what-it-produces.md) | A skill declares what it produces; no registry is generated |
| [0014](./0014-the-glossary-is-a-root-file.md) | The glossary is a root file; `comparable.md` folds into the brief |
| [0015](./0015-the-instruction-tree-mirrors-the-artifact-tree.md) | The instruction tree mirrors the artifact tree; a skill is a route |
