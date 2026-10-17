---
path: _concept/goals.md
summary: success criteria, KPIs, constraints and explicit non-goals
writers: [concept-brief]
---

# _concept/goals.md

What "working" means for the product, and what it deliberately will not do. Journeys, plans and reviews are checked against it, so every entry has to be settleable; a goal nobody can settle gives nothing downstream to check against.

## Format

```markdown
---
success_criteria: []            # what "working" means, one line each
kpis: []                        # the measurable ones
constraints: []                 # budget, deadline, platform, compliance
non_goals: []                   # explicitly out, so nobody re-proposes them
last_updated: YYYY-MM-DD
approved: YYYY-MM-DD            # written with the brief's approval
---
```

The body restates the lists as prose sections: the one outcome that would mean this worked, the measurable signals behind it, the hard constraints, and the non-goals — what people will expect and this deliberately will not do.

## Writing it

1. **Turn the vision into goals** after the pitch in `_concept/brief.md` exists, using the same depth and the same one-question-per-message rule. Write the draft without `approved:`.
2. **Tie each criterion to the brief.** Every criterion traces to the brief's problem or hero flow, and each is a number, a threshold or a yes/no condition.
3. **Write `TBD` for what the user never implied.** A deadline or budget the user did not give is `TBD`; an invented one gets planned around.
4. **Leave approval to the brief's.** The goals are shown with the brief and approved by the same yes (`tree/brief.md § Approving both files`), which writes `approved:` here.

## Checks

- Each of `success_criteria`, `kpis`, `constraints`, `non_goals` is filled or says it has none.
- No criterion is unsettleable ("fast", "good UX").
