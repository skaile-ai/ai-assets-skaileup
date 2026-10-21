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
- **Glossary proposals.** A proposed glossary term could land in a project's `CONTEXT.md`. `tree/README.md § Ownership` now keeps project files outside `_concept/` as sources, and `tree/APP-DESIGN.md` step 8 names `_concept/glossary.md`.
- **No owner file yet.** When the owner's file did not exist yet, the proposal had nowhere to go. The protocol now has the proposer create the owner's file holding only its proposed entries; scenario 1's re-run shows the stub `APP-DESIGN.md`.

## Open decisions for the owner

1. **The project's glossary versus `_concept/glossary.md`.** CLINICO's `CLAUDE.md:148` says "one root `CONTEXT.md` is the glossary". In scenario 4, `experience-interaction` quoted the node's `_concept/glossary.md` rule, then followed the project instruction and appended its proposed term to `CONTEXT.md`. Project instructions outrank the collection, so the nodes cannot win this. Decide whether the collection should adopt a project's declared glossary path, for example a `glossary:` key in `scope.yaml`, or leave it as is.
2. **The hard-gate check in `ops-review` was kept.** The plan's line on ops-review asks for it, but the T7 ticket body omits it. It now behaves like `check.py`'s `hard-gate-has-producer`.
3. **`mockup-feedback` is not an owner of screens.** It applies human-approved patches under `tree/07_screens/[screen].md § Patching (mockup-feedback)`. Making it an owner would force a `decisions.md` produce onto it.
4. **`scope.yaml` takes proposed entries from seven skills.** The plan table listed none. The reason is recorded in ADR 0023: `depth` and `project_type` are asked lazily by the first skill that needs them.
5. **`docs/handoffs/2026-10-21-handoff-app-design-research.md` is still untracked.** As its own caveat says, decide whether it belongs in version control.

## Caveats

- The smoke used one model (sonnet), one run per scenario and no real dialogue, so batch discipline under a live user is not measured.
- In scenario 4, `frontend/` is an empty submodule in the archive copy, so the T44 code references were copied from neighbouring entries and not opened.
