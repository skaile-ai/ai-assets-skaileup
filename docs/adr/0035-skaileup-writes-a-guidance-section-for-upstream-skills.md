# 0035 — skaileup writes a guidance section for the upstream skills

**Status:** accepted

Amends [ADR 0012](0012-foreign-skills-and-the-two-libraries.md) with a third axis for external
skills, and [ADR 0034](0034-the-tree-protocol-lives-beside-it.md) by adding a third artifact to
`tree/protocol/beside-the-tree.md`.

## Context

The build side hands work to upstream engineering skills — `to-tickets`, `implement-spec`,
`tdd`, `code-review`, `diagnosing-bugs`, `domain-modeling`, `triage` — and keeps them
unmodified (ADR 0012, "absorb, don't fork"). Those skills read only the `## Agent skills` block
of `CLAUDE.md` or `AGENTS.md` and the files under `docs/agents/` that upstream
`setup-matt-pocock-skills` writes. Nothing there named `_concept/`: an upstream run saw neither
the feature specs and their parent issues, nor the levelled records in `docs/adr/`, the API
contracts, the data model, or the pending proposals it must not build on. The only pointer the
collection left was one `AGENTS.md` line `build-scaffold` wrote to `APP-DESIGN.md`, and only in a
project it created.

Three of those skills — `setup-matt-pocock-skills`, `to-tickets`, `implement-spec` — carry
`disable-model-invocation: true`. ADR 0012's two axes had no place for them: the Skill tool
cannot call them, yet an agent, not the human, is meant to run them.

## Decision

1. **A third root artifact, `docs/agents/domain.md`.** Its node is `tree/docs/agents/domain.md`.
   Upstream setup writes the file; `skaileup` owns only its `## skaileup artifacts` section —
   fixed headings, one bullet per concept artifact that exists, project-relative paths — and
   adds one `### Concept (skaileup)` sub-block to the `## Agent skills` block that points at it.
   The sub-block is project code, like the walkthrough section, and no skill's `produces` lists
   it. `skaileup` produces `{ id: agent-guidance, path: "docs/agents/domain.md" }`.
2. **Written on the first build-side demand.** When the router resolves a `build-*`,
   `quality-review` or `quality-test` skill as next and the section is missing, `skaileup` runs
   upstream setup with its recommended answers (the lead asks the user only where
   `expectations.md` says the user decides), then writes the section and the sub-block. A later
   `skaileup` run that changes which artifacts exist rewrites the section whole.
3. **`build-scaffold` writes no `AGENTS.md` line.** The section's **Interaction rules** bullet
   is the pointer to `APP-DESIGN.md`, and it reaches every project, not only a scaffolded one.
4. **The `user-followed` axis.** `EXTERNAL_SKILLS` gains a third value for the three
   `disable-model-invocation` skills. A route reaches one with the phrase
   ``Read the installed `<name>` skill and follow it`` (optionally `, with <inputs>`); a
   Skill-tool call to one is an error, and so is the phrase for a `model` skill. The phrase
   counts as a use for `external-skill-declared`, and every external skill a skill uses is
   declared in `metadata.requires` as `skill:@mattpocock/<name>#0.1.0`.

## Options rejected

- **Fork the upstream skills to read `_concept/`.** Breaks ADR 0012's premise and drifts from
  upstream on every release.
- **A file of skaileup's own under `docs/agents/`.** Upstream reads only the files its setup
  names; a new file would be read by nothing.
- **Keep the `AGENTS.md` pointer in `build-scaffold`.** Covers only `APP-DESIGN.md` and only a
  project the collection created.
- **Call the three skills through the Skill tool.** The host refuses it for
  `disable-model-invocation` skills.

## Consequences

- `PROJECT_ROOT_ARTIFACTS` in `scripts/check.py` holds three entries; `tree/README.md`'s
  `_concept/README.md` pointer names three nodes.
- `skaileup` requires `skill:@mattpocock/setup-matt-pocock-skills#0.1.0`; a project without it
  installed still gets the section, written into a file of its own.
- `docs/skill-template.md` documents the three axes and the phrase.
