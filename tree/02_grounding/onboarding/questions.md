---
path: _concept/02_grounding/onboarding/questions.md
summary: open questions routed to someone who is not in the room
owner: [concept-onboard]
may_propose: []
---

# _concept/02_grounding/onboarding/questions.md

Questions whose answer needs a person who is not in the session — a compliance owner, whoever
holds the integration credentials, the client. Writing them here keeps onboarding moving
instead of guessing or stalling. The file is sent out and answered asynchronously, usually in
one pass, so a compound question comes back half-answered.

## Format

A markdown file with the universal frontmatter (`tree/README.md § Frontmatter every markdown artifact carries`). One `##` section per question, most important first:

```markdown
## 1. <the question, one idea>

Decision riding on it: <what this answer changes>

Answer:
```

## Writing it

1. Name the gap: aim each question at the difference between what that person knows and what
   this project needs.
2. State the decision riding on the answer.
3. Order the questions most-important-first, one idea per question.
4. Leave a blank `Answer:` stub under each.

## Checks

Every question for someone outside the room that came up during onboarding is in this file, and
each carries its decision and an answer stub.
