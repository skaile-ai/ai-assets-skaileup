---
path: _concept/brief.md
summary: the pitch, with its comparables — what the user said, no more
writers: [concept-brief]
---

# _concept/brief.md

The pitch: who the product serves, what problem it solves, the primary journey, and the comparables it positions against. Journeys, features, screens, brand and stack all read it, so a brief that guesses sets the whole concept guessing. It records what the user actually said; pinning the words they settled is `tree/glossary.md`'s job, right after.

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

`## Comparables` is the last section and there is no separate comparables file; where `tree/02_grounding/research/README.md` produced `competitors.md`, the section cites it for the analysis behind a product instead of restating it.

## Writing it

1. **Read what exists.** `_concept/02_grounding/onboarding/answers.json` for answers a dialog collected, and `_concept/02_grounding/research/{domain,competitors,audiences}.md` where research ran first — that set is the deep pass, and this skill distils it rather than re-running it. The `flow` in `_concept/01_meta/scope.yaml` sets the depth of steps 3 and 4: `appbuilder-mvp` takes one pass at each, `appbuilder-standard` and `skaileup-concept-only` work them until the user stops correcting.
2. **Seed from findings when they exist.** When `_concept/02_grounding/findings/brief-seeds.md` exists (the reverse flow), seed the pitch, goals and comparables from it and show each graded value as a proposal: `extracted` is what the repository says, `inferred` and `needs_review` are guesses only the user can settle, and none is a decision yet.
3. **Get the pitch.** With a free-form description, mine it for name, pitch, audience, problem, hero flow, comparables and success criteria, and carry on with the gaps — step 5 fills one more cheaply than an interview. Otherwise ask, one question per message: what it does in a sentence, who the primary user is, the single most important problem, the one action every user must take, similar apps, what success looks like. Write the frontmatter and the vision.
4. **Study the comparables** as `## Comparables`: three to six products, at least one direct competitor, one indirect, one adjacent. Each gets a borrow and an avoid named as a specific pattern ("good UX" is not one), and the section closes on the positioning gap tied to the audience. When the user named none and no research exists, write that; a fabricated competitor looks real by the time features are cut against it, and an unverifiable claim about a real one is marked `unverified`.
5. **Show the brief and wait for a yes in words.** Apply changes, show it again, ask again — an unapproved root propagates its mistakes into work that costs far more to redo. On the yes, write `approved: <date>` into the frontmatter of the brief and of `tree/goals.md` in the same write; an edit after that clears the key until the user says yes again.
6. **Leave the words to the glossary.** A term the user corrected you on is used in their wording throughout and named in your hand-off, so `concept-glossary` pins it while the correction is fresh; glossary entries written here would put a second writer on a file that has one.

## Checks

- Frontmatter carries the four fields above, and `approved:` records the user's yes.
- `## Comparables` closes the body with three to six products and a positioning gap.
