---
path: _concept/11_build/release.yaml
summary: "the whole-app release verdict: goals, seven scores, findings, improvements"
owner: [quality-release]
may_propose: []
---

# _concept/11_build/release.yaml

The last gate: whether the thing that exists is the thing the project set out to build.
`quality-release` is the only skill that reads `brief.md` and `goals.md` against the running
application; everything upstream checks a part against its own spec, which is how a product
ships with every criterion green and none of its goals met. The verdict grades and refuses
and never edits code. Stance, flag shape, severities and the report format are
`tree/11_build/README.md § Verdicts`; here the evaluator walks the app as a user and does not
read what it was supposed to do.

## Format

```yaml
verdict: pass | needs_iteration | fail
goals:
  - { goal: <one line from the grading sheet>, status: achieved | partial | not_achieved, evidence: <what you did in the app> }
design:                          # 0-10 each, scored per the rubrics below
  quality:       { score: <n>, evidence: <screens and elements behind the number> }
  originality:   { score: <n>, evidence: <...> }
  craft:         { score: <n>, evidence: <...> }
  functionality: { score: <n>, evidence: <...> }
technical:
  performance:   { lcp: <seconds>, cls: <n>, first_interaction: <ms> }
  accessibility: <0-100>
  mobile:        <0-100>          # at 375px
findings: []                      # flag shape, tree/11_build/README.md § Verdicts
improvement_priorities:           # ranked by impact on the goals, not by ease of fix
  - { item: <what to change>, owner: <skill that owns the fix> }
last_updated: YYYY-MM-DD
```

## Writing it

1. **Refuse on an incomplete trace or ledger.** Read `_concept/11_build/trace.yaml`, the build loop's machine-read record and this skill's one hard input (an empty trace means `build-implement` has recorded no slice, which the refusal says). Every feature under `_concept/05_features/` needs an entry with commits, and every slice in it a frozen dossier (its `index.md` exists); list each feature that falls short and refuse the release. Then read each feature's ledger under `_concept/11_build/acceptance-criteria/` (`tree/11_build/acceptance-criteria/README.md § Reading`): a `FAIL` or untested row is the same refusal, listed by criterion id with its evidence. Then read `_concept/11_build/reviews/*.yaml`; a feature still at `changes-requested` is the same refusal.
2. **Extract the intent.** From `brief.md` and `goals.md`, list every goal, success metric, constraint and stated non-goal, one line each. Without `goals.md`, the brief's problem statement and hero flow are the goal set. Without `brief.md` too, derive the goal set from `_concept/02_grounding/findings/brief-seeds.md` (`concept-reverse` scoped `brief` fills it from the code) and ask the user to confirm or correct it, in one batch (`tree/README.md § How a skill runs`, rule 1); `concept-brief` writes the brief. This list is the grading sheet and is written down before the app is opened, so the app cannot supply it.
3. **Walk the whole product, not the features.** Enter where a new user enters (`_concept/04_journeys/stories.yaml` says where people start) and pursue each goal from step 2 through the app in the order a person would, without jumping straight to a route. Each journey's own verdict is already in the ledger rows, so this walk does not re-run their steps; it catches what is only visible from the seams: a journey that works but leaves the user with no idea what to do next, two features that each pass and contradict each other, a dead end between them.
4. **Score goal achievement.** For each goal from step 2, `achieved`, `partial` or `not_achieved`, with what you did in the app as the evidence. Criteria status comes from the ledger rows read in step 1; re-testing them here is duplicated work.
5. **Score the four design axes** (quality, originality, craft, functionality), 0-10 each, strictly, per `### Design rubrics`. Read the rubric before scoring and not afterwards, cite the exact screens and elements behind every number, and check the surface against `_concept/03_brand/brand.tokens.json` (`tree/03_brand/brand.tokens.md`) where it exists. "Looks clean" is the absence of a score.
6. **Score the three technical axes**, banded per `### Release thresholds`:
   - **Performance**, from the browser's own tooling: LCP, CLS and first interaction.
   - **Accessibility**, 0-100: every journey completable without a mouse, interactive elements labelled, text and controls meeting contrast against their real background.
   - **Mobile**, 0-100, at 375px: all content reachable, no horizontal scroll, touch targets at least 44px.
7. **Write the verdict** to `_concept/11_build/release.yaml`: goals with their evidence, the seven scores, the blocking findings, and `improvement_priorities` ranked by impact on the goals. The verdict is read off `### Release thresholds` and not recomputed from impression.
8. **Report** the verdict, the goal tally, the seven scores on one line and the ranked improvements, each naming the skill that owns the fix so the verdict routes somewhere instead of ending the run.

### Design rubrics

Four axes, 0-10 each. Mediocre work is a 5-6, not a 7-8. A score with no cited screens and elements is an impression that cannot be argued with or acted on.

**Quality of design**: is this one coherent experience, or a set of screens that happen to share a domain?

| score | |
|---|---|
| 9-10 | Every screen is designed as part of a whole. Visual hierarchy guides attention; navigation feels inevitable. |
| 7-8 | Coherent, with minor inconsistencies. |
| 5-6 | Coherent in sections, with visible disconnects: settings looks like a different product. |
| 3-4 | Mostly disconnected; sections read as different apps. |
| 0-2 | No coherence. Layout decisions look independent of each other. |

**Originality**: does this look like a product with an identity, or like generated output? Generation converges on the same defaults, and each one present is a deduction: a purple or blue gradient as the primary brand colour; a centred hero (big headline, subtext, one CTA); cards for every content type regardless of the content; the default grey palette with a single accent; Inter or Roboto with no typographic decision behind it; "clean and minimal" as the stated goal and not an achieved effect. A score above 7 needs named distinctive choices, or it is a generic app graded politely.

| score | |
|---|---|
| 9-10 | Distinctive identity. You would recognise this product from one screenshot. |
| 7-8 | Real choices, with defaults surviving in secondary areas. |
| 5-6 | Mostly defaults, one or two decisions of its own. |
| 3-4 | Heavy defaults throughout. |
| 0-2 | Indistinguishable from placeholder UI. |

**Craft**: typography, spacing, colour harmony, consistency; whether the details were looked at.

| score | |
|---|---|
| 9-10 | Font pairing works, spacing is rhythmic and consistent, no rough edges. |
| 7-8 | Polished, with a few rough edges. |
| 5-6 | Functional but unpolished: uneven spacing, inconsistent type scale. |
| 3-4 | Inconsistencies throughout. |
| 0-2 | No evidence anyone looked. |

**Functionality**: does every element earn its place?

| score | |
|---|---|
| 9-10 | Nothing decorative. Interactions are obvious without explanation. |
| 7-8 | Purposeful, with minor gratuitous elements. |
| 5-6 | Several components exist for looks and do nothing. |
| 3-4 | Decoration outweighs function in places that matter. |
| 0-2 | Elements that actively get in the user's way. |

### Release thresholds

The skill scores; this section decides what a score means. A **good** value leaves the verdict alone, a **warn** value is reported in the improvement list, and a **block** value refuses the top band where the verdict table names that metric.

| metric | good | warn | block |
|---|---|---|---|
| Largest contentful paint (LCP) | under 2.5s | 2.5–4s | over 4s |
| Cumulative layout shift (CLS) | under 0.1 | 0.1–0.25 | over 0.25 |
| First interaction | under 100ms | 100–300ms | over 300ms |
| Accessibility (0–100) | 70 or more | — | under 70 |
| Design average (0–10) | 7 or more | — | under 7 |
| Goals `achieved` or `partial` | two thirds or more | — | under two thirds |

| verdict | holds when |
|---|---|
| `pass` | goals, design average, accessibility and LCP are all outside the block band, and there is no blocking finding |
| `needs_iteration` | any goal `not_achieved`, or design average, accessibility or LCP in the block band, or any blocking finding |
| `fail` | most goals `not_achieved`, or LCP and CLS both in the block band |

CLS on its own, first interaction and Mobile (0–100) are reported and ranked in `improvement_priorities`; none of them moves the verdict alone.

## Checks

- `release.yaml` is on disk, every goal in it carries evidence from the running app, every design score cites the elements behind it, and the verdict follows `### Release thresholds`.
