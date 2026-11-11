# Beside the tree

## Beside the tree

Three artifacts sit outside `_concept/`, at the project root (the directory that holds `_concept/`), and a monorepo app has its own of each, one per project:

- **`APP-DESIGN.md`** holds the project's interaction decisions and is owned by `experience-interaction`; `quality-interaction` checks code against it and writes its verdict to `_concept/11_build/interaction.sarif`, never to this file. Its node is `tree/APP-DESIGN.md` (installed at `<contracts>/shared-contracts/APP-DESIGN.md`).
- **`docs/adr/`** holds the project's decision records, one file `<NNNN>-<slug>.md` per decision, in the layout upstream `domain-modeling` also writes. It is owned by `skaileup`, which numbers and writes each record; every other skill proposes. Its node is `tree/docs/adr/README.md` (installed at `<contracts>/shared-contracts/docs/adr/README.md`).
- **`docs/agents/domain.md`** tells the upstream engineering skills where the domain docs live. Upstream `setup-matt-pocock-skills` writes the file; `skaileup` owns only its `## skaileup artifacts` section, which names every concept artifact the project has so those skills find them unmodified, and writes it before the first build-side run. Its node is `tree/docs/agents/domain.md` (installed at `<contracts>/shared-contracts/docs/agents/domain.md`).

They are the only such artifacts; `AGENTS.md` and `CLAUDE.md` are project code, not concept artifacts, and no skill lists them under `produces`. Coding agents reach `APP-DESIGN.md` and the rest of the concept through the `### Concept (skaileup)` sub-block `skaileup` writes into the `## Agent skills` block of whichever of the two upstream setup chose, which points at `docs/agents/domain.md § skaileup artifacts` (`tree/docs/agents/domain.md`). The other exception: `skaileup` writes the marked walkthrough section (`<!-- skaileup:walkthrough -->` … `<!-- /skaileup:walkthrough -->`) into the project's agent file — `AGENTS.md`, else `CLAUDE.md` — through `walkthrough.py guard --write` (`tree/01_meta/walkthrough.md`), and nothing else in it.

A second contract asset, `rulebook/` (contract `app-design-rulebook`: rules, defaults, floorplans), holds the application-design rules skills cite. It is not a `_concept/` part and has no node here.
