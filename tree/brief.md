---
path: _concept/brief.md
summary: the pitch, with its comparables — what the user said, no more
owner: [concept-brief]
may_propose: []
---

# _concept/brief.md

The pitch: who the product serves, what problem it solves, the primary journey, and the comparables it positions against. Journeys, features, screens, brand and stack all read it, so a brief that guesses sets the whole concept guessing. It records what the user actually said; pinning the words they settled is `concept-glossary`'s job.

## Format

```markdown
---
elevator_pitch: "One sentence"
audience: "Who it's for"
problem: "What it solves"
hero_flow: "The most important user action"
last_updated: YYYY-MM-DD
approved: YYYY-MM-DD     # only after the user's yes
---

# <App name>

<Vision in plain language: who it serves, what problem it solves, the primary journey.>

## Comparables

<Three to six products; each with a concrete borrow and a concrete avoid; closes on the positioning gap.>
```

`## Comparables` is the last section and there is no separate comparables file; where research produced `_concept/02_grounding/research/competitors.md` (`tree/02_grounding/research/README.md`), the section cites it for the analysis behind a product instead of restating it.

## Writing it

### Drafting the brief

1. **Read what exists.** `_concept/02_grounding/onboarding/answers.json` for answers a dialog collected, and `_concept/02_grounding/research/{domain,competitors,audiences}.md` where research ran — that set is the deep pass, and this skill distils it rather than re-running it. `depth` in `_concept/01_meta/scope.yaml` (format: `tree/01_meta/scope.md`) sets the depth of the pitch, the comparables and the goals: `sketch` takes one pass at each, `standard` and `exhaustive` work them until the user stops correcting. Absent, `depth` is a question in the step 3 batch, recorded as a `proposed` entry in `scope.yaml`.
2. **Seed from findings, deriving them when the code holds them.** When `_concept/02_grounding/findings/brief-seeds.md` exists, seed the pitch, goals and comparables from it and show each graded value as a proposal: `extracted` is what the repository says, `inferred` and `needs_review` are guesses only the user can settle, and none is a decision yet. Where a repository exists and the file does not, or its `source_sha` differs from HEAD, run `concept-reverse` scoped to `brief` first (`tree/README.md § How a skill runs`, rule 1).
3. **Get the pitch.** With a free-form description, mine it for name, pitch, audience, problem, hero flow, comparables and success criteria, and carry on with the gaps — the approval review fills one more cheaply than an interview. Otherwise ask, as one decision batch (`tree/README.md § How a skill runs`): what it does in a sentence, who the primary user is, the single most important problem, the one action every user must take, similar apps, what success looks like. Write the frontmatter and the vision, without `approved:`.
4. **Study the comparables** as `## Comparables`: three to six products, at least one direct competitor, one indirect, one adjacent. Each gets a borrow and an avoid named as a specific pattern ("good UX" is not one), and the section closes on the positioning gap tied to the audience. When the user named none and no research exists, write that; a fabricated competitor looks real by the time features are cut against it, and an unverifiable claim about a real one is marked `unverified`.

The goals are drafted from this brief by `tree/goals.md`; approval comes only after both drafts exist.

### Approving both files

5. **Show `_concept/brief.md` and `_concept/goals.md` together and wait for a yes in words.** Apply changes, show them again, ask again — an unapproved root propagates its mistakes into work that costs far more to redo. On the yes, write `approved: <date>` into the frontmatter of both in the same write, per `tree/README.md § Frontmatter every markdown artifact carries`.
6. **Leave the words to the glossary.** A term the user corrected you on is used in their wording throughout and named in the completion summary, so `concept-glossary` pins it while the correction is fresh; glossary entries written here would put a second owner on a file that has one.

## Checks

- Frontmatter carries the four fields above, and `approved:` records the user's yes to the brief and the goals together.
- `## Comparables` closes the body with three to six products and a positioning gap.
