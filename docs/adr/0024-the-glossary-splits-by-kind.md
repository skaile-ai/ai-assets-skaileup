# 0024 — The glossary splits by kind when the project keeps its own

**Status:** accepted

Amends [ADR 0014](0014-the-glossary-is-a-root-file.md): the glossary is no longer only a root
file of `_concept/`; in split mode its words live in a file outside `_concept/`. Amends
[ADR 0022](0022-shared-artifact-contracts-and-proposed-entries.md): in split mode a proposed
glossary term lands in the project glossary, not in `_concept/glossary.md`, and `concept-glossary`
writes one file outside `_concept/`. [ADR 0021](0021-the-glossary-carries-the-light-ontology.md)
stands: the ontology stays in `_concept/glossary.md`.

## Context

The ADC acceptance smoke showed a conflict that wording cannot fix. CLINICO's `CLAUDE.md:148`
declares the root `CONTEXT.md` the glossary. Project instructions outrank an installed contract,
so `experience-interaction` wrote its proposed term to `CONTEXT.md` even after it quoted the
node's rule that proposed terms go to `_concept/glossary.md`.

The collection cannot win that argument, and it should not try. `CONTEXT.md` is the file the
`domain-modeling` skill keeps: `# <Context>`, one sentence, `## Language`, then per term the bold
term, a one-to-two-sentence definition and an `_Avoid_` line; no frontmatter, no ids. Four devBench
repos keep one (CLINICO, weiterbildungsplaner, KNOWLEDGE-WORK/kgs, SKAILEdev/platform). None has a
`_concept/glossary.md` yet, and none has a `CONTEXT-MAP.md`. A project in that state keeps two
glossaries that drift, or a skill that follows the project instruction and breaks the contract.

The two files also hold different kinds of information. A definition and an `_Avoid_` list are
words; `kind`, `is-a`, `part-of`, `roles`, `purpose`, `principle`, the object axes and relations
are the ontology of [ADR 0021](0021-the-glossary-carries-the-light-ontology.md). The project file
already holds the first kind and cannot hold the second without a format change.

## Decision

**G1 — Where the words live is a fact, resolved one way.** The `glossary` key of
`_concept/01_meta/scope.yaml` — or, while it is absent, its latest `proposed` entry — is a
project-relative path (split mode, that file is the project glossary) or the value `concept`
(concept mode, everything in `_concept/glossary.md` as before). With neither, the mode is split
with `CONTEXT.md` when the project root has one, else concept mode (G6 for `CONTEXT-MAP.md`). The
key exists to override: a glossary elsewhere, or `concept` to keep everything in `_concept/`. The
common case asks nothing.

**G2 — Split by kind.** In split mode the project glossary holds term, definition and `_Avoid_`
in its own format. `_concept/glossary.md` holds, per term, `kind`, `is-a`, `part-of`, `roles`,
`purpose`, `principle`, the four object axes, and `## Relations`, with no definition and no
`_Avoid_` line, and names the project glossary in a `Words:` line under its title. Every confirmed
term of the project glossary has an ontology entry with at least `kind`. Each piece of information
has one home.

**G3 — Ids are derived, never written into the project glossary.** The id is the kebab-case slug
of the bold term: lowercased first, then ä, ö, ü and ß transliterated to ae, oe, ue and ss
(`LÄK-Punkte` → `laek-punkte`). `CONTEXT-FORMAT.md` has no id syntax, and adding one would change
the project's file format. Derived ids are unique across the project glossary: two meanings of one
word get distinct, qualified bold terms (`Order (Billing)` → `order-billing`), which
`concept-glossary` asks for. An ontology-only entry whose id matches no term is a rename or a
removal; `concept-glossary` asks which, in a batch.

**G4 — Proposed terms in split mode go to the project glossary.** That is where any agent that
follows the project's instruction puts them. The entry is appended at the end of `## Language` (or
the matching cluster heading, `##` or `###`; else the end of the file), in the project's format,
followed by the marker lines of
[ADR 0022](0022-shared-artifact-contracts-and-proposed-entries.md) (`status`, `proposed_by`,
`proposed_on`, `source`); the markers also keep an unconfirmed term visible to coding agents that
read the file. A known `kind` goes into a proposed entry of the same id in `_concept/glossary.md`.
Promotion drops the markers in both files and completes the ontology entry; rejection removes both
and records the rejection in the decision record.

**G5 — The project glossary stays the project's.** `concept-glossary` writes there only the
definitions and `_Avoid_` lines of terms it adds or moves, the promotion of a proposed entry
(dropping its marker lines) and its rejection (removing the entry). Entries written by
`domain-modeling` or by hand are kept, never reordered or reformatted, and no frontmatter is added.
`approved:` lives in `_concept/glossary.md` and covers both parts. This is the one exception to the
rule that project files outside `_concept/` are sources only; `tree/README.md § Ownership` names
it. Two writers on one file are safe only when the second preserves what the first wrote.

**G6 — A `CONTEXT-MAP.md` with no `glossary` key and no root `CONTEXT.md` is undecided.** A
`_concept/` describes one app, and a map of several contexts does not say which. Proposers file full
entries in `_concept/glossary.md` as in concept mode; `concept-glossary` asks once which context
file this `_concept/` describes and proposes the answer as a `scope.yaml` entry. A root
`CONTEXT.md` settles the mode (split) and asks nothing.

**G7 — No new node.** `tree/glossary.md` gains the section `## Where the words live`, placed after
`## Format` as node-template allows, and describes both parts. `concept-glossary` still produces
`_concept/glossary.md` only, and that file exists after every run, so gates and the project-root
artifact list stay as they are. The declared path is variable, and a node per variable path would
break the mirror rule of [ADR 0017](0017-the-instruction-tree-mirrors-the-artifact-tree.md).

## Options rejected

- **Status quo: the glossary lives in `_concept/glossary.md` only.** Projects with a root
  `CONTEXT.md` keep two glossaries that drift, or the project instruction wins and a skill writes
  where the contract says not to. The ADC smoke produced the second outcome.
- **Projects yield: the project drops its `CONTEXT.md`.** `domain-modeling` and every human reader
  of the file lose their home, and the skill then recreates the file, so the drift moves rather than
  ends.
- **Ontology fields inside `CONTEXT.md`.** It changes the project's file format and leaves
  `domain-modeling` unable to read its own file.
- **Ids written into the project glossary.** The format has no id syntax; a derived id costs a
  rename question and nothing else.
- **A node per declared path.** The path is not fixed, so no part of `_concept/` maps to it.

## Consequences

- `tree/glossary.md § Where the words live` is the one place that resolves the mode. Steps that read
  definitions, `_Avoid_` lists or term names cite it; steps that read kind, axes, relations or
  `glossary_id` targets keep `_concept/glossary.md`.
- `check_concept.py` resolves the mode and, in split mode, reports an ontology id with no term, a
  definition or `_Avoid_` line left in `_concept/glossary.md`, a stale proposal in the project
  glossary, a term whose derived id repeats an earlier one, and a declared path that does not exist.
- A project changes mode by editing the `glossary` key, or by gaining a root `CONTEXT.md`.
- A project with a `CONTEXT-MAP.md` and no `CONTEXT.md` carries one question until it answers.
- Concept mode is unchanged, so a project without a root `CONTEXT.md` sees no difference.
- A full entry left in `_concept/glossary.md` when the mode turns split — a `domain-modeling` run
  creating `CONTEXT.md`, an answered CONTEXT-MAP question, a key set later — is moved by
  `concept-glossary`: definition and `_Avoid_` go to the project glossary, the ontology lines stay.
