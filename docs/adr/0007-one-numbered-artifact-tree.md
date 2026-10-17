# 0007 — One artifact root, numbered at the first level only

**Status:** accepted

## Context

A project grew two roots: `_concept/` (design) and `_implementation/` (build). Inside
`_concept/`, thirteen top-level entries sat on four different organizing axes at once — by
producing domain (`discovery/`, `experience/`, `blueprint/`), by artifact kind (`testing/`,
`prototype/`), by tool (`mockup-walkthrough/`, `mockup-component/`), and by machinery
(`_grounding/`, `_meta/`, `_standards/`, `_seeds/`, `_feedback/`). The mockup family alone
owned five of the thirteen. The leading underscore was applied inconsistently: `_grounding/`
is authored by a skill and read by eleven, while `prototype/` and `testing/` are pure derived
output and carried no prefix.

Two external facts decided most of it.

**`_concept/` is a host contract.** forge-concept resolves the literal string in four source
sites — `server/utils/project.ts:112` (`getConceptDir()`), `artifact-contract.ts:187-188` and
`:208-209` (strips and prepends the `_concept/` prefix), `api/concepts/[...name].post.ts:43`
(git-commits `_concept/${relPath}`). It is the directory the editor serves artifacts from,
live regardless of `artifacts.yaml` being unreachable (ADR 0001). A neutral root — `.skaile/`,
`_project/` — costs an edit inside forge-concept, which the map rules out.

**The sidebar has no ordering mechanism but the filename.** `AppSidebar.vue:332-338` sorts
`localeCompare` on the raw on-disk name, directories before files. Unnumbered, a reader opening
the tree gets *behaviors, blueprint, brand, brief, build, dossiers, grounding, meta, mockup,
screens*. And the host already implements the other half of the convention: `NN_` is stripped
before display in three components (`SidebarFileItem.vue:204`, `AppHeader.vue:194`,
`GroundingBrowser.vue:376`), and `review-coverage.ts:103` matches feature names with or
without it.

## Decision

**One root: `_concept/`.** `_implementation/` is absorbed as `11_build/`. The root keeps its
underscore because there it marks pipeline-owned against app-owned, next to `src/` and
`package.json` — a different distinction from the one rejected inside the tree.

**The first level is numbered; nothing below it is.**

```
_concept/  brief.md · goals.md · comparable.md
  01_meta/ 02_grounding/ 03_brand/ 04_journeys/ 05_features/ 06_behaviors/
  07_screens/ 08_dossiers/ 09_mockup/ 10_blueprint/ 11_build/
```

Number what the collection fixes; leave what the project grows unnumbered. The eleven
top-level entries are the same in every project and change only when this repo changes.
Featuresets and feature slugs are project-grown: their set and priority move as the project
does, priority already lives upstream as the story stage, and renaming a featureset folder
mid-project rewrites every cross-reference to it.

**The sequence is dependency order, not the flows' current order.** `05_features` precedes
`06_behaviors` and `07_screens` because both read features. Where `appbuilder-complex`
disagrees — it runs `behaviors` at line 179 and `features` at line 190, while `behaviors`'
own gate reads *"when features are approved"* — the flow is wrong.

**Contiguous numbers, no gaps.** A gap buys cheap insertion by making the number stop meaning
position, which is the only thing it is for.

**The three root files stay files and stay unnumbered.** Directories sort before files
unconditionally, so a prefix on `brief.md` cannot change its position — only its order among
the other two.

## Consequences

- This reverses, at one level, what ADR 0002 did to the collection tree. Not a contradiction:
  ADR 0002 removed `NN_` because the flow graph carried order, making the path redundant. The
  artifact tree has no flow graph, and its only ordering structure is the filename, which the
  host reads. Same principle — order lives in the strongest structure available — landing
  opposite because the available structures differ.
- The old collection already migrated numbered → unnumbered once (`1_discovery/1_overview/` →
  `discovery/`). What is restored here is one numbered level, not the second and third that
  migration removed.
- The prefix enters artifact ids and `/concepts/…` URLs, because `artifact-contract.ts` strips
  only the `_concept/` prefix. Display strips it; addresses do not.
- The build half becomes visible in the forge-concept editor, which serves everything under
  the root.
- `concept.yaml` dies. It was a manifest of artifact slots and their status — the same object
  ADR 0004 deleted one level up, and status is derivable from whether the file is there.
- `_seeds/` and `_standards/` become `02_grounding/seeds/` and `02_grounding/standards/`:
  grounding is defined by where a thing came from (outside), machinery by what reads it (the
  pipeline itself).
- `prototype/`, `mockup-component/`, `mockups/` and `mockup-walkthrough/<renderer>/` collapse
  into `09_mockup/`. The renderer leaves the path — it is recorded once, in onboarding.
- `CONTEXT.md` gains one line: the root directory name is fixed by the host and is not the
  vocabulary word.
- A validator earns its place: every path a skill writes resolves to a real top-level entry.

---

**Root list amended by [ADR 0014](0014-the-glossary-is-a-root-file.md)** (2026-10-16). The
three root files are now `brief.md · goals.md · glossary.md`; `comparable.md` folds into
`brief.md`. The tree and every other decision here stand.
