# 0030 — The data model is two YAML files, checked by `@skaile/model`

**Status:** accepted

Amends [ADR 0016](0016-published-formats-where-one-exists.md) decision 2 for the data model only:
its two schemas are owned by the npm package `@skaile/model`, not by `tree/`. Supersedes
[ADR 0026](0026-the-mockup-stage-is-one-vue-storybook-package.md) D2 (the data model authored in
TypeScript and generated to JSON); the rest of 0026 stands. The proposal mechanism of
[ADR 0022](0022-shared-artifact-contracts-and-proposed-entries.md) is unchanged: a proposed entry
is still a `proposed: { by, on, source }` key in the model, promoted by deleting it.

## Context

Under ADR 0026 every project carried nine files in `_concept/10_blueprint/datamodel/`: the
authored `model.ts` and `seed.ts`; the tool files `skaile-model.ts` and `gen.ts`, copied from the
skill; two schema copies `gen.ts` refused to run without; the generated `model.json` and
`seed.json` every reader took; and a generated `model.dbml` nothing read. Each fact existed three
times (`.ts`, `.json`, `.dbml`) and each schema in three places (`tree/`, the skill's references,
every project). A hand edit of `model.ts` without a `gen.ts` run left `model.json` stale, and
nothing detected it: forge, `build-database` and the end-to-end tests read the stale file without
a word. Forge drew the model only on its own page, never from the file tree, and drew no enums.

What ADR 0026 bought with TypeScript was one thing: a seed row or a mockup prop that no longer
fits the model fails `tsc`. That detector survives without TypeScript as the source (below).

## Decision

**1. Two authored files, nothing generated in `_concept/`.** `10_blueprint/datamodel/` holds
`model.yaml` (entities, fields, enums, relations, proposed entries) and `seed.yaml` (the named
scenarios, every row checked against the model) and nothing else. Seed stays a file of its own
because it is example data: hundreds of rows would bury the model. The format is the shape of the
old DSL written as data — a field is a type name or an options object, a relation is a field of
type `m2o` and the loader derives the relationship and its inverse. Format:
`tree/10_blueprint/datamodel/README.md § Format`, `model.md` and `seed.md`.

**2. One package reads, checks and serves the files: `@skaile/model`.** It ships the two JSON
Schemas, the loader (`loadModel`, `loadSeed`) returning the normalized model and seed every reader
used to take from `model.json` and `seed.json`, every check `gen.ts` ran, the CLI
(`check`, `json`, `types`, `migrate`) and a Vite plugin that serves the model to the mockup
package and writes its row types. A reader that needs data runs `bunx @skaile/model json`
(`npx` without Bun) or imports the loader; nothing can be stale, because nothing is generated.

**3. The datamodel schemas live in the package, not in `tree/` — the exception to ADR 0016.**
ADR 0016 placed each machine file's schema beside its node in `tree/` and made `check.py`
validate the demo against it. These two schemas have a loader that must agree with them on every
key; a copy in `tree/` would be a second definition that drifts from the code checking it. So the
package holds the one copy, versioned with its loader, and the files point at the published copy
by URL in their first line
(`# yaml-language-server: $schema=https://cdn.jsdelivr.net/npm/@skaile/model@1/schema/model.schema.json`,
`seed.schema.json` for the seed), which editors with YAML-schema support use to complete and flag
while the file is typed. `tree/10_blueprint/datamodel/` names the package and the URL and holds no
schema file; `check.py` holds the demo's two files to `bunx @skaile/model check`.

**4. Layout is editor state.** The entity `position` and the `editor` block (canvas viewport) of
the old `model.json` are dropped. Where the cards sit is the host's state per user (forge keeps
it in its own database), not a fact of the model.

**5. Old projects migrate with one command.** `bunx @skaile/model migrate` turns an existing
`model.json` + `seed.json` into `model.yaml` + `seed.yaml`, checks them and deletes the nine
legacy files. `architecture-datamodel` runs it when it finds `model.ts` or `model.json` without
`model.yaml`.

## Options rejected

**Keep TypeScript as the source, generate on save.** Fixes neither the three copies of each fact
nor the stale JSON when the generator is not run; it only moves the moment it is forgotten.

**One file holding model and seed.** The rows of four scenarios outnumber the model's lines many
times over, and the person reviewing the model would scroll past them.

**Schemas stay in `tree/`, the package copies them at build time.** Two copies with a build step
between them is the drift this record removes; `tree/` would still be the copy no code reads.

**Keep `model.dbml` as a readable render.** Nothing read it. Forge draws the model from the YAML,
and the YAML itself is the readable form.

## Consequences

- **Projects lose seven files.** `_concept/10_blueprint/datamodel/` goes from nine files to two.
  `model.ts`, `seed.ts`, `skaile-model.ts`, `gen.ts`, `datamodel-model.schema.json`,
  `datamodel-seed.schema.json`, `model.json`, `seed.json` and `model.dbml` are legacy; a project
  that still has them works after `migrate`.
- **The `tsc` detector moves into the mockup package.** The Vite plugin writes the row types
  (`TaskRow`, …) into a gitignored folder of the Storybook package, so renaming a field in
  `model.yaml` still fails `vue-tsc` in every story that uses it. Seed rows are no longer typed
  while they are written; `check` and the schema in the editor cover them.
- **Readers call the package.** `build-database`, `quality-test`, `quality-e2e`, `ops-review` and
  `mockup-feedback` read the model through `@skaile/model json` or `check`; a model the checker
  rejects stops them with its issues. Running them needs Bun or Node on the machine.
- **A schema change is a package release.** Changing a key of the format means a new
  `@skaile/model` version; the URL pins the major version (`@1`), so files written for 1.x keep
  validating in editors until a 2.0 says otherwise.
- **`check.py` validates the demo through the package.** The demo's `model.yaml` and `seed.yaml`
  pass `bunx @skaile/model check` (or `npx`); a machine with neither runner fails the rule with a
  message saying so, rather than skipping it.
- **Layout resets once.** A model whose `model.json` carried positions shows its cards on a grid
  until the user arranges them; the host keeps that arrangement from then on.
