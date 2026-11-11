# 0033 — GLOSSARY.md is the default project glossary

**Status:** accepted

Amends [ADR 0024](0024-the-glossary-splits-by-kind.md) G1 and G6: the project glossary is
`GLOSSARY.md` by default, a root `CONTEXT.md` is its legacy name, and a project with neither gets
split mode with a new root `GLOSSARY.md` instead of concept mode. G4 stays as amended by
[ADR 0031](0031-proposals-are-files-per-run.md). G2 (split by kind), G3 (derived ids), G5 (the
project glossary stays the project's) and G7 (no new node) stand. Amends
[ADR 0012](0012-foreign-skills-and-the-two-libraries.md) in one point: a skill that calls an
external skill declares it in `metadata.requires`.

## Context

Upstream renamed the file. The `domain-modeling` skill now keeps `GLOSSARY.md` in
`GLOSSARY-FORMAT.md` (`# <Context>`, one or two sentences, `## Language`, per term a bold term, a
one-to-two-sentence definition and an `_Avoid_` line, optional cluster subheadings), and a
`GLOSSARY-MAP.md` for repos with several contexts; `setup-matt-pocock-skills` offers a `git mv
CONTEXT.md GLOSSARY.md` to repos that still carry the old name. Under 0024 the collection only
looked for `CONTEXT.md`, so a project set up by the current upstream skills fell back to concept
mode and grew a second glossary inside `_concept/` that drifts from the one `domain-modeling`
writes.

`concept-glossary` also restated the upstream format and its interview — challenge a term against
the glossary, sharpen fuzzy words, write a resolved term at once — so every upstream change had to
be copied by hand. The skills that call `tdd`, `code-review`, `grilling` and the other external
skills named them only in prose: nothing installed them and nothing noticed when one was missing.

## Decision

**H1 — Resolution order.** The words live, in this order, in: the file the `glossary` key of
`_concept/01_meta/scope.yaml` names (or `_concept/glossary.md` itself for `concept`), or while the
key is absent its latest pending proposal entry with anchor `key:glossary`; a root `GLOSSARY.md`;
a root `CONTEXT.md`, as legacy; with a root `GLOSSARY-MAP.md` (or legacy `CONTEXT-MAP.md`) and no
root glossary, undecided as under G6; otherwise a new root `GLOSSARY.md`. Every case but `concept`
is split mode.

**H2 — The legacy name is offered a rename once.** Where the words resolve to a root `CONTEXT.md`,
`concept-glossary` offers once, as a decision batch, to `git mv CONTEXT.md GLOSSARY.md` (and
`CONTEXT-MAP.md` to `GLOSSARY-MAP.md`), as `setup-matt-pocock-skills` does. A no keeps
`CONTEXT.md` as the project glossary; nothing is asked again.

**H3 — concept-glossary adapts domain-modeling.** It calls the Skill tool with `domain-modeling`
for the words: challenging terms against the project glossary, sharpening fuzzy language and
writing resolved terms in upstream's `GLOSSARY-FORMAT.md`, which the collection cites and does not
restate. It keeps what upstream lacks: mode resolution, the ontology in `_concept/glossary.md`
(ADR 0021) with its `Words:` line, the settle pass over glossary proposal entries and id
derivation.

**H4 — External skills are declared.** Every external skill a route calls with the Skill tool, or
tells the user to run, is listed in `metadata.requires` as `skill:@mattpocock/<name>#<range>`
(today the exact `#0.1.0`: skaile's resolver finds no store version for a caret range such as
`#^0.1`), so installing a skill installs what its route calls. `check.py` rule
`external-skill-declared` fails a call with no declaration, a declaration the body never names and
a declaration with no range.

## Options rejected

- **Keep concept mode as the default.** A project with no glossary yet is the case where the two
  files are cheapest to keep apart, and the one `domain-modeling` would later split anyway.
- **Rename `CONTEXT.md` silently.** The file is the project's (G5); other tools and people read it
  by name.
- **Restate GLOSSARY-FORMAT in `tree/glossary.md`.** A copy that drifts from upstream with every
  release; citing it costs nothing.
- **Fork `domain-modeling`.** The collection would carry a second glossary interview to maintain.

## Consequences

- `tree/glossary.md § Where the words live` carries H1 and H2; `scope.md` and `scope.schema.json`
  describe the new default.
- `concept-glossary` requires `skill:@mattpocock/domain-modeling#0.1.0`; `domain-modeling` joins the
  external skills `check.py` knows.
- A project with no glossary now gets a root `GLOSSARY.md` on its first `concept-glossary` run; one
  that wants everything in `_concept/` sets `glossary: concept`.
- The demo keeps `GLOSSARY.md` at its root.
