# 0014 — The glossary is a root file

**Status:** accepted; partly superseded by [0021](0021-the-glossary-carries-the-light-ontology.md) (the glossary is no longer words only) and [0022](0022-shared-artifact-contracts-and-proposed-entries.md) (other skills may append `proposed` entries)

Amends the root-file list in [ADR 0007](0007-one-numbered-artifact-tree.md).

## Context

The ubiquitous-language glossary sat at `10_blueprint/glossary.md`, written last and by three
skills: `concept-brief` seeded it, `spec-feature` appended terms as features appeared, and
`architecture-datamodel` appended entity names. It was the artifact every earlier step needed
and the last one pinned.

That placement encodes the wrong dependency. The words come first: journeys, features,
behaviors and the data model all name things, and each coins its own names when no glossary
exists to read. With three writers none of them owns it, and with the file under
`10_blueprint/` it reads as architecture output rather than as the language the whole concept
is written in.

The root has a second problem. `comparable.md` is the third root file, but it is a view of
competitors — material `02_grounding/research/competitors.md` already holds and
`concept-brief` already cites. It earns a section of the brief, not a file of its own.

## Decision

**The root list becomes `brief.md · goals.md · glossary.md`.**

```
_concept/  brief.md · goals.md · glossary.md
  01_meta/ 02_grounding/ 03_brand/ 04_journeys/ 05_features/ 06_behaviors/
  07_screens/ 08_dossiers/ 09_mockup/ 10_blueprint/ 11_build/
```

- **`glossary.md` has one writer: a new skill, `concept-glossary`**, which runs right after
  `concept-brief` in every flow. It leaves `10_blueprint/`. `spec-feature` and
  `architecture-datamodel` read it and use its terms; they never append to it. A concept with
  no term is handed back to `concept-glossary`, which is re-enterable the way `spec-feature`
  is.
- **`comparable.md` folds into `brief.md`** as a `## Comparables` section that cites
  `02_grounding/research/competitors.md` rather than restating it. `concept-brief` writes it.
- **The root-file count stays three.** The freed slot is the one `glossary.md` takes. The
  rest of ADR 0007 stands: the root files stay files and stay unnumbered, and the first level
  stays eleven numbered directories, contiguous.

ADR 0010's rule holds unchanged: no twelfth top-level entry and no new root file beyond these
three. This record swaps one root file for another; it does not grow the root.

## Consequences

- `contracts/concept_structure.md`'s tree fence loses `comparable.md` and
  `10_blueprint/glossary.md` and gains `glossary.md` at the root; its read-direction table
  follows. `contracts/domain_model.md` names the new path and the single-writer rule.
- Artifacts get read earlier than they were written: `experience-journeys`,
  `architecture-datamodel`, `spec-featuresets` and `spec-feature` may now declare
  `glossary.md` as a prerequisite, which they could not while it was a late blueprint output.
- **Existing `_concept/` trees are not migrated.** A project that has `comparable.md` and
  `10_blueprint/glossary.md` keeps them; there is no migration tool. `ops-review` reports the
  old paths as unowned, which is the intended signal to move the content by hand.
- The root file `comparable.md` ceases to be an id anything declares; its path leaves the
  tree, and `check.py` rejects a skill that still names it.
