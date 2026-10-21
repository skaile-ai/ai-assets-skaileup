---
path: _concept/glossary.md
summary: the project's ubiquitous language — terms, definitions, _Avoid_ lists
owner: [concept-glossary]
may_propose: []
---

# _concept/glossary.md

The project's ubiquitous language, term to definition, with the words each term beat listed under `_Avoid_`. Every journey, feature, screen, entity and test names things from it; without a glossary each coins its own words ("account" in one feature, "user" in a screen, "customer" in code). It has one writer, `concept-glossary`, and every other skill reads it and never appends — a file with several writers is a file nobody owns. It holds words and nothing else: no fields, types, paths or API shapes, which live in `tree/10_blueprint/datamodel/README.md` and the code.

## Format

```markdown
---
last_updated: YYYY-MM-DD
approved: YYYY-MM-DD     # only after the user's yes
---

# Glossary — <App Name>

<One or two sentences: what this product's domain is.>

## <Optional cluster heading, e.g. Ordering>

**Order**:
A confirmed request from a Customer for one or more Items.
_Avoid_: Purchase, transaction, cart
```

- **Be opinionated.** When several words mean one concept, pick the best and list the rest under `_Avoid_`; that list is the anti-drift mechanism, so it names every word the sources used for the same concept.
- **Tight definitions.** One or two sentences saying what the thing *is*, not what it does.
- **Only project-specific terms.** A general programming word (timeout, retry, cache, DTO) stays out however heavily the product uses it.
- **One glossary.** When subsystems give one word different meanings, keep one entry per meaning under a cluster heading naming the subsystem, and only when a term genuinely collides.

## Writing it

1. **Read the ground.** `_concept/brief.md` (pitch, audience, problem, hero flow, `## Comparables`), `_concept/02_grounding/research/{domain,competitors,audiences}.md` where research ran — the field's own words are there — and `_concept/02_grounding/findings/` where a repository was reverse engineered, whose names each carry a grade. `answers.json` may already hold terms the user gave. When `glossary.md` exists this is a re-entry: go to step 6.
2. **List the candidates.** Every noun the product keeps, every role of a person, every event or state a user would name aloud, each marked with where it came from. A name taken from code findings goes in as a candidate, never settled, because code names drift from what people say.
3. **Grill the words**, one per message, each with your recommended term and a one-line reason. Two words for one concept: ask which wins and list the loser under `_Avoid_`. One word for two concepts: split it and name both. A word that came from neither the user nor a cited source goes in only on a yes. Depth follows the `flow` in `_concept/01_meta/scope.yaml`: `appbuilder-mvp` settles the ten or so terms the hero flow needs in one pass; the other three flows work the list until the user stops correcting.
4. **Write `glossary.md`** with `last_updated` and no `approved:` yet, the domain sentence, then the entries grouped under cluster headings where clusters are natural.
5. **Show it and wait for a yes in words.** Apply corrections, show again, ask again; on the yes write `approved: <date>` in the same write. An edit after that clears the key until the user says yes again.
6. **Re-enter for a missing term.** A later step (`spec-feature`, `architecture-datamodel`, `experience-journeys`) that meets a concept with no term stops, names the concept and hands back; the flow re-enters here with that concept as input. Grill only that term, add it in place under the right cluster, and leave every other entry alone unless the user asks. A changed existing definition ripples into the artifacts that quote it, so name which ones and let the user decide before the edit. Stamp `approved:` again on the yes and return to the step that handed back.

The globally installed `domain-modeling` skill is the sharpen-later tool: a standalone grill that challenges the glossary against the code, stress-tests terms with edge cases and captures decisions, run any time the model has drifted. This collection ships no skill for that job; `concept-glossary` keeps the glossary current and `domain-modeling` deepens it.

## Checks

- Every entry has a definition and an `_Avoid_` line (or says there is none).
- No entry carries implementation detail, and `approved:` records the user's yes.
