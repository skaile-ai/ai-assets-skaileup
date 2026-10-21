# Handoff: app-design clean slate (ADC)

Date: 2026-10-21. Plan: `.omp/plans/ADC_APP_DESIGN_CLEAN_SLATE_PLAN.md` (local, untracked). Tickets: `.scratch/app-design-clean-slate/issues/i-adc-*.md` (local, untracked).

## What landed

| ticket | commit |
|---|---|
| i-adc-ownership-foundations | `aeb903a` |
| i-adc-rulebook-contract | `b756393` |
| i-adc-floorplan-catalogue | `93e66ac` |
| i-adc-glossary-ontology | `5002e53` |
| i-adc-app-design-artifact | `f9d48c6` |
| i-adc-independent-screens | `6b269af` |
| i-adc-demand-router, i-adc-quality-design | `d87b6df` |
| code-review fixes (two-axis review over `aeb903a^..d87b6df`) | `83e49c4` |
| i-adc-acceptance-smoke (smoke-driven node fixes + this file) | the commit that adds this file |

The collection now has 33 skills and 2 advisory flows (`skaileup-greenfield`, `skaileup-reverse`). `rulebook/` is the second contract asset (rules P1–P31, heuristics H1–H12, defaults DF1–DF15, 16 floorplans with `preview.html`). `skaileup` is a demand-driven router. Screens are flat (`07_screens/<screen>.md`) and carry a floorplan, posture, density and region bindings. `quality-design` is the discovery loop. Gates are soft except where a machine-read input is consumed.

## Acceptance smoke

Each scenario ran `omp -p --model sonnet` in a throwaway `git archive` copy of the real repo under `/tmp/adc-smoke/`, with the collection installed in `.omp/skills` and `.omp/contracts/{shared-contracts,app-design-rulebook}`. None of the copies had `_concept/`. The runs were non-interactive, so each one printed the batches it would have sent and took every recommendation as the answer.

| # | scenario | repo | result | largest batch |
|---|---|---|---|---|
| 1 | `experience-screen` describes a built screen from the middle (no brief, scope or feature) | herdr-dashboard | `07_screens/inbox.md`, glossary with proposed terms, and a stub `APP-DESIGN.md` holding 8 `(proposed by …)` entries | 7 |
| 2 | `concept-glossary` infers the ontology | weiterbildungsplaner | `glossary.md` with `## Relations` triples and proposed entries | 7 |
| 3 | `experience-screen` builds two floorplan prototypes without journeys or brand | herdr-dashboard | `09_mockup/prototypes/explorer/{a,b}.html` (master-detail and list-report) and the spec against a | 7 |
| 4 | read-only central object (Eingang) | CLINICO | object-map row with no editor, create or delete; Open rows Q25+ | 7 |
| 5 | refine one policy without re-interview | weiterbildungsplaner | MSG-1 alone changed plus a Changelog line; no batch | 0 |

No run stopped with "run X first". Screenshots of scenario 3's prototypes are in `.scratch/app-design-clean-slate/smoke/` (local).

The smoke found three defects, which are fixed in the commit that adds this file:

- **Glossary batch size.** The glossary's confirm-or-reject step said "one batch", so it produced batches of 9, 11 and 14. Step 7 now settles entries seven at a time, step 4 splits long gap lists, and § Checks counts questions per message. Scenario 2's re-run peaked at 7.
- **Glossary proposals.** A proposed glossary term could land in a project's `CONTEXT.md`. The ADC fix kept project files as sources only; the GLS effort below replaced it with a split by kind.
- **No owner file yet.** When the owner's file did not exist yet, the proposal had nowhere to go. The protocol now has the proposer create the owner's file holding only its proposed entries; scenario 1's re-run shows the stub `APP-DESIGN.md`.

## Decisions settled after the smoke (2026-10-21)

- **Hard-gate check:** removed from `ops-review`. The collection gate already has it as `hard-gate-has-producer`, and `ops` inspects `_concept/`.
- **`mockup-feedback`:** stays a patcher, not an owner of screens (`tree/07_screens/[screen].md § Patching (mockup-feedback)`).
- **`scope.yaml`:** keeps its seven proposers (ADR 0023).
- **Local working files:** `.omp/` and `.scratch/` are ignored. The research handoff is not committed, because `rulebook/rules.md § Sources` carries its citations.

## Glossary split (GLS, 2026-10-21)

The open decision on the project's glossary versus `_concept/glossary.md` was settled as option (a), split by kind ([ADR 0024](../adr/0024-the-glossary-splits-by-kind.md)). Plan `.omp/plans/GLS_GLOSSARY_SPLIT_PLAN.md`, tickets `.scratch/glossary-split/issues/` (local).

| ticket | commit |
|---|---|
| i-gls-split-contract | `85bac44` |
| i-gls-proposers-follow | `463cb89` |

- **Rule.** `scope.yaml` key `glossary` names the project glossary; absent, a root `CONTEXT.md` is it (split mode), else everything stays in `_concept/glossary.md` (concept mode). In split mode the words (term, definition, `_Avoid_`) live in the project glossary and the ontology (kind, axes, relations) in `_concept/glossary.md`, keyed by the term's derived id. `tree/glossary.md § Where the words live` is the one place every proposer and reader cites.
- **Checker.** `check_concept.py` reports an ontology entry with no term, words left in `_concept/glossary.md`, a confirmed term with no entry, stale proposals in the project glossary and a declared path that does not exist.

Smoke, same setup as above under `/tmp/gls-smoke/`:

| repo | run | result | max batch |
|---|---|---|---|
| CLINICO | `experience-interaction` records the Eingang | Eingang and Eingang-Eintrag appended to `CONTEXT.md` with the four marker lines; `_concept/glossary.md` created with the `Words:` line and two proposed entries carrying `kind`. `check_concept` reports the 15 older `CONTEXT.md` terms as waiting for `concept-glossary` (medium), as designed | 6 |
| weiterbildungsplaner | `concept-glossary` | split mode inferred with no question; `CONTEXT.md` +64 lines, 0 changed or removed (8 proposed terms); `_concept/glossary.md` ontology-only for every term; `check_concept` clean | 7 |
| herdr-dashboard | `concept-glossary` (no `CONTEXT.md`) | concept mode as before: 17 full entries with definitions and `_Avoid_`; `check_concept` clean | 7 |

## Caveats

- The smoke used one model (sonnet), one run per scenario and no real dialogue, so batch discipline under a live user is not measured.
- In scenario 4, `frontend/` is an empty submodule in the archive copy, so the T44 code references were copied from neighbouring entries and not opened.
