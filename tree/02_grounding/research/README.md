---
path: _concept/02_grounding/research/
summary: sourced findings per topic that other skills design against
writers: [concept-research]
---

# _concept/02_grounding/research/

Findings that other skills design against: the domain, the competitors, the audience, the visual
references. `concept-research` writes them after `concept-onboard` and before `concept-brief`,
so the brief, glossary and brand are written against what it found; it runs again beside any
later step that needs grounding. It writes findings only — no brief, no features, no tokens. A
claim without a source is a claim about a claim, and the stale one is the one that gets built on.

## Contents

One node per file: `tree/02_grounding/research/domain.md`, `tree/02_grounding/research/competitors.md`, `tree/02_grounding/research/audiences.md`, `tree/02_grounding/research/design-inspiration.md`, `tree/02_grounding/research/patterns.md`, `tree/02_grounding/research/colors-fonts.md`, `tree/02_grounding/research/behavioral-patterns.md`. Research run alongside one skill goes to `tree/02_grounding/research/step/README.md`. Raw material (screenshots, page saves) goes to `tree/02_grounding/findings/README.md`.

## Format

Every file carries `last_updated` (and its count where its node names one) in the frontmatter
(`tree/README.md § Frontmatter every markdown artifact carries`) and a source against every
factual claim. The default scope is four files — `domain`, `competitors`, `audiences`,
`design-inspiration`; `patterns`, `colors-fonts` and `behavioral-patterns` exist only when the
scope asked for them (`research_scope` options: `domain`, `competitors`, `audiences`, `design`,
`patterns`, `colors`, `behavioral`).

## Writing it

1. **Pick the depth before scoping.** It is `globals.research_depth` of the flow that is running
   (the value the host's onboarding depth picker shows and the user may have changed); with no
   flow running, derive it from `flow` in `tree/01_meta/scope.md` (`appbuilder-mvp` → `skip`,
   `appbuilder-standard` and `skaileup-concept-only` → `moderate`, `skaileup-concept-reverse` →
   `light`); with neither, `moderate`. The four values are the whole vocabulary, and the depth sets
   breadth, not rigour — every claim still names a source:

   | depth | files written | agents dispatched |
   |---|---|---|
   | `skip` | none — report that research was skipped; a user who invokes the skill directly has overridden the sizing, so run it at `light` | none |
   | `light` | `design-inspiration.md` and `domain.md`, plus any topic `research_scope` names | one per file written |
   | `moderate` | the four default files, plus any topic `research_scope` names | one per topic |
   | `deep` | all seven files, `research_scope` or not | one per topic, and one per competitor or persona inside `competitors` and `audiences` |

2. **Scope against what the project has said.** Read `02_grounding/onboarding/answers.json`. On a
   first run there is no brief, so domain, audience segments and named products come from the
   answers; on a re-run `brief.md` (its `## Comparables` section included) and `goals.md` exist
   and override the answers where they differ. The user's own comparables go on the list before
   anything found. Present the plan as who and what will be investigated and let the user add
   or cut — research nobody asked for spends the same tokens as research that matters.
3. **Dispatch one background agent per topic** (see § Subagent dispatch) and keep working while
   they read. Each is pointed at primary sources — official documentation, the product itself,
   first-party pricing and changelogs, the spec — follows every claim back to whoever owns it,
   and returns findings with a source against every factual claim.
4. **Write one file per topic** from the returned findings, each following its own node. A
   competitor feature that could not be verified is written as not publicly available rather
   than filled in.
5. **Always write `design-inspiration.md`.** `design-brand`, `experience-shell` and both
   mockup renderers read it, and it is the file that most often goes unwritten because the
   competitor work ran long.
6. **Catalogue the raw material** in `tree/02_grounding/findings/README.md`, with
   `step: concept-research` on each row.
7. **Report what changed the picture**, not what was collected: the competitor gap, the
   persona nobody had in mind, the regulation that constrains the data model; and point at the
   skills that should now be re-run or run for the first time.

### Subagent dispatch

When a flow node has `"subagent": true`, the dispatching skill creates a fresh agent context
holding only the skill's `SKILL.md`, the tree nodes it cites and the input `_concept/` folders.
The subagent gets the task text verbatim and nothing of the conversation — paste the full task
into its prompt rather than pointing it at a plan file. It runs to completion and ends with
this block, and the dispatching skill acts on the status and collects the output artifacts:

```
STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED

[If DONE_WITH_CONCERNS]  Concerns: <trade-offs, deviations, debt incurred>
[If NEEDS_CONTEXT]       Missing:  <what is absent>
                         Question: <single specific question for the user or the dispatching skill>
[If BLOCKED]             Reason:   <what cannot be resolved>
                         Route:    context | escalate-model | decompose
```

| Status | Meaning | Dispatching skill's action |
|---|---|---|
| `DONE` | All requirements met, tests pass | Accept output, advance flow |
| `DONE_WITH_CONCERNS` | Implemented but with trade-offs or notes | Accept, log concerns in `_concept/11_build/decisions.md`, advance |
| `NEEDS_CONTEXT` | Missing information or ambiguous requirement | Put the question to the user; resume when answered |
| `BLOCKED` | Cannot proceed — see route | Follow the route below |

| Route | When to use | Dispatching skill's response |
|---|---|---|
| `context` | A specific question can unblock the task | Put the question to the user; re-dispatch with the answer |
| `escalate-model` | Task exceeded model capability | Note in `_concept/11_build/decisions.md`; re-dispatch on a higher-tier model |
| `decompose` | Task is too large to execute atomically | Break into smaller tasks; re-dispatch each |

A partial output with no status leaves the dispatching skill guessing; a code makes it act.

## Checks

- Every file the scope asked for exists, and every factual claim in them names its source.
- `02_grounding/findings/index.md` accounts for the raw material.
