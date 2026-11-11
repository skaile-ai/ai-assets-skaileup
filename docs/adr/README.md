# Decision records

The decisions this collection was built from. Each one was worked as a ticket on the
migration map (`.scratch/skaileup-mp/` in the old repo); these are the durable form, kept
here once the map ends. 0001–0016 are carried over from `ai-assets-skaileup-mp`; 0017 is
where this variant departs from it; 0018–0023 are the app-design clean slate; 0024 splits the
glossary by kind; 0025 adds archetypes as an optional declared default; 0026 replaces the
mockup surfaces with one Vue Storybook package and authors the data model in TypeScript; 0027
adds eight agents (a lead and seven delegates) and gives decision records a level and a kind; 0028 adds generated feature pages to the mockup;
0029 walks the concept top-down in four stages the build skills gate on; 0030 replaces the TypeScript data model with two YAML
files checked by the package `@skaile/model`; 0031 moves proposed entries out of the owners'
artifacts into one proposal file per run; 0032 moves the decision logs to one ADR file per
decision under `docs/adr/`; 0033 makes `GLOSSARY.md` the default project glossary; 0034 moves the
tree's protocol into `tree/protocol/`; 0035 has skaileup write a guidance section the upstream
skills read; 0036 rebuilds `build-plan` and `build-implement` as adapters on upstream
`to-tickets` and `implement-spec`, with issue ↔ PR links as the trace.

A decision earns a record here when it passes three tests: it constrains future work, it
was expensive to reach, and reversing it would cost more than reading it.

| ADR | Decision |
|---|---|
| [0001](./0001-skill-name-is-the-identity.md) | A skill's `name:` is its whole identity |
| [0002](./0002-flat-tree-and-nine-domains.md) | Flat tree; the domain lives in the name |
| [0003](./0003-skill-body-shape.md) | 140-line ceiling, no `MUST`/`NEVER` block — superseded by 0017 |
| [0004](./0004-contracts-earn-their-place.md) | A contract survives only if it is read in-body — superseded by 0017 |
| [0005](./0005-warm-and-cold-session-boundaries.md) | Two session boundaries, warm and cold; no slash commands |
| [0006](./0006-the-slice-loop-composes.md) | The slice loop is four skills that compose global ones; amended by 0036 (one pass per spec, on `to-tickets` and `implement-spec`) |
| [0007](./0007-one-numbered-artifact-tree.md) | One numbered artifact tree under `_concept/` |
| [0008](./0008-gates-live-at-the-step-they-bind.md) | A gate lives at the step it binds; no file collects gates |
| [0009](./0009-stack-knowledge-lives-in-templates.md) | Stack-specific knowledge lives in a template, not a skill |
| [0010](./0010-no-plan-file-and-no-status-file.md) | The build side keeps no plan file and no status file; superseded by 0036 where it concerns slice dossiers and the trace |
| [0011](./0011-the-machine-layer-sits-under-metadata.md) | The machine layer sits under `metadata:`; paths carry `_concept/` |
| [0012](./0012-foreign-skills-and-the-two-libraries.md) | Five foreign skills stay global, called one gate-checked way; what came from pstack and Pocock; amended by 0035 and 0036 |
| [0013](./0013-a-skill-declares-what-it-produces.md) | A skill declares what it produces; no registry is generated |
| [0014](./0014-the-glossary-is-a-root-file.md) | The glossary is a root file; `comparable.md` folds into the brief |
| [0016](./0016-published-formats-where-one-exists.md) | Published formats where one exists: DTCG tokens, JSON Schema for machine files, SARIF, OpenAPI/AsyncAPI, MADR, C4; amended by 0030 |
| [0017](./0017-the-instruction-tree-mirrors-the-artifact-tree.md) | The instruction tree mirrors the artifact tree; a skill is a route |
| [0018](./0018-the-rulebook-is-a-second-contract-asset.md) | The rulebook is a second contract asset; amends 0015, supersedes part of 0017 |
| [0019](./0019-scoped-fact-resolution.md) | Skills resolve facts, not files; hard gates only for machine-read formats; demand-driven router; amended by 0029 and 0030 |
| [0020](./0020-screens-are-independent-artifacts.md) | Screens are independent artifacts under `07_screens/` |
| [0021](./0021-the-glossary-carries-the-light-ontology.md) | The glossary carries the light ontology — supersedes 0014's "words only" |
| [0022](./0022-shared-artifact-contracts-and-proposed-entries.md) | `owner` + `may_propose`, proposed entries, one decision record; amended by 0024, 0031 and 0032 |
| [0023](./0023-two-advisory-flows.md) | Two advisory flows; tier becomes `depth`; supersedes the tier-as-flow part of 0002/0007; its `decisions.md` paragraph amended by 0032 |
| [0024](./0024-the-glossary-splits-by-kind.md) | The glossary splits by kind when the project keeps its own: words in the project glossary, ontology in `_concept/glossary.md`; amends 0014 and 0022; G4 and G5 amended by 0031; amended by 0033 |
| [0025](./0025-archetypes-are-an-optional-declared-default.md) | Archetypes are an optional declared default: one table in `rulebook/archetypes.md`, `archetype:` in `APP-DESIGN.md`, cards stay research; extends 0015 and 0018 |
| [0026](./0026-the-mockup-stage-is-one-vue-storybook-package.md) | The mockup stage is one Vue Storybook package; the data model is authored in TypeScript and generated to JSON; notes go through the annotation inbox; amends 0020 and 0022; D2 superseded by 0030 |
| [0027](./0027-agents-and-levelled-decisions.md) | Eight agents, a lead and seven delegates, with the interview relay; expectations first; decision records carry a level and a kind, patterns included; a similarity check before the grill; ideas in the roster; amends 0022; K7 amended by 0031; K4 and K5 amended by 0032; K1 amended by 0036 |
| [0028](./0028-feature-pages-are-generated-from-the-specs.md) | Feature pages are generated from the specs: one `Features/<featureset>/<feature>` story per spec, screen stories bind via `screenDocs`, triage routes feature notes to the spec; amends 0026 |
| [0029](./0029-the-concept-is-walked-top-down.md) | The concept is walked top-down: four stages (frame, look, data, features) each ending on the user's yes, one state file `_concept/01_meta/walkthrough.yaml`, the four build skills gate on it, no silent completion, `depth` thins and never removes; amends 0019 and 0023 for those four skills; W4 amended by 0031; W5 amended by 0032 |
| [0030](./0030-the-data-model-is-two-yaml-files-checked-by-skaile-model.md) | The data model is two authored YAML files, `model.yaml` and `seed.yaml`, nothing generated in `_concept/`; `@skaile/model` owns their schemas (an exception to 0016), loader, checks and CLI; layout is editor state; amends 0016, 0019 and 0026 (supersedes its D2); its inline `proposed:` key amended by 0031 |
| [0031](./0031-proposals-are-files-per-run.md) | Proposals are files, one per run: `_concept/proposals/<date>-<skill>-<scope>.yaml`, entries name `target`, `anchor`, `payload`; only the target's owner settles; no proposal markers in owner artifacts; rejections stay in the file; parallel runs need disjoint owned paths; amends 0022, 0024 G4, 0027 K7, 0029 W4 and 0030; amended by 0032 |
| [0032](./0032-one-decision-log-under-docs-adr.md) | One decision log under `docs/adr/`: one file per decision, cited by slug `adr:<slug>`, owned by `skaileup`, which numbers and writes it; every other skill proposes it; levels, kinds and patterns unchanged; build concerns go to the spec's parent issue; supersedes both `decisions.md` logs; amends 0022, 0023, 0027 K4/K5, 0029 W5 and 0031 |
| [0033](./0033-glossary-md-is-the-default-project-glossary.md) | `GLOSSARY.md` is the default project glossary; amends 0024 |
| [0034](./0034-the-tree-protocol-lives-beside-it.md) | The tree's cross-cutting protocol lives beside it in `tree/protocol/` (ownership, running, delegation, beside the tree); routes cite only the files they use; amends 0017; amended by 0035 |
| [0035](./0035-skaileup-writes-a-guidance-section-for-upstream-skills.md) | skaileup writes the `## skaileup artifacts` section of `docs/agents/domain.md`, a third root artifact, on the first build-side demand after running upstream `setup-matt-pocock-skills`; `build-scaffold` writes no `AGENTS.md` pointer; external skills gain the `user-followed` axis; amends 0012 and 0034 |
| [0036](./0036-build-adapters-on-to-tickets-and-implement-spec.md) | `build-plan` follows the installed `to-tickets` on the spec's parent issue (`tracker.issue`) and `build-implement` the installed `implement-spec`, on integration branch `spec/<featureset>-<feature>` with a draft PR closing the parent; slice dossiers and `trace.yaml` removed, issue ↔ PR links are the trace; the lead composes `build-implement`; amends 0006, 0012 and 0027 K1; supersedes 0010 where it concerns slice dossiers and the trace |
