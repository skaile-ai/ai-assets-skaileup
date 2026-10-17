---
path: _concept/11_build/
summary: slices, trace, criteria ledger, reviews, release verdict and decisions
writers: []
---

# _concept/11_build/

The build half of the tree: what was planned, built, proved and judged. Everything before
`11_build/` is design and nothing under it is. A skill here may read the whole tree and writes
only the part it owns, so each file below has one writing skill and a verdict has one place it
is decided.

| part | holds | written by |
|---|---|---|
| `slices/<slice_id>/` | one vertical slice's dossier, frozen on commit | `build-plan` (plan), `build-implement` (index) |
| `trace.yaml` | feature → slices → commits → code | `build-implement` |
| `acceptance-criteria/` | the criteria status ledger, one file per feature | `build-plan` creates, `build-implement`, `quality-e2e`, `quality-review` flip rows |
| `reviews/<feature_slug>.yaml` | one feature's code-review verdict | `quality-review` |
| `release.yaml` | the whole-app release verdict | `quality-release` |
| `decisions.md` | build-time decision records | grown inline during the build |

## Verdicts

Three skills write a verdict artifact: `ops-review` (the concept tree), `quality-review`
(one feature's code) and `quality-release` (the whole running app). Each owns only its own
dimensions, deduction tables, weights and scope-specific process; everything below applies
to all three.

### Stance

Evaluate as an independent party that was not present when the artifact was produced and has
not seen the producing conversation or code: run from a session that did not write what is
under evaluation. Approach adversarially: assume defects exist and make the artifact prove
otherwise. Infer no intent; what the artifact does not state is missing.

Every finding says in the same sentence how it was obtained: **measured** (seen in the
artifact or the running app, quoted or reproduced) or **inferred** (follows from something
measured, and names it). An absence is measured, and the quote is where the statement should
have been. A claim that is neither is not a finding: run the check that would make it one, or
leave it out.

Gather all evidence silently before scoring (read every input or exercise every flow first,
and produce no output while gathering), write the result file before reporting to the user,
and emit a passing verdict only while no blocking flag exists.

### Scoring

Each dimension starts at 100 and the skill's deduction table applies literally, every listed
deduction and no judgment discounts. `overall_score` is the weighted sum of the dimension
scores; each skill defines its weights and they sum to 1.0.

### Flag shape

Every finding carries a quote of the problematic text (or an exact reproduction) and a
specific, actionable resolution:

```yaml
- severity: critical|high|medium|low
  category: <machine-readable kind>
  location: <exact path, with a line where the artifact has lines>
  note: <quote the problematic text, against what was required>
  resolution: <the specific change that clears it>
```

Severity has four ordered levels, and `critical` or `high` is what *blocking* means: the
boundary decides the verdict and the ordering ranks the fix list, which a two-value scale
cannot do for a twenty-finding report.

| severity | blocking | what puts a finding here |
|---|:-:|---|
| `critical` | yes | data loss, an authorisation hole, a goal of the project defeated |
| `high` | yes | a stated requirement not met, or a criterion claimed met that is not |
| `medium` | no | a real defect the artifact still functions around |
| `low` | no | a nit worth recording once, never worth blocking on |

A skill may add scope-specific rules for placing a finding and never a fifth level.

### Verdict grammar

Three bands; each skill names them for its own scope, and a skill whose middle band cannot
occur maps to two. The top band and "zero blocking findings" are one statement, so a skill
states the band and not its own copy of the rule.

| band | names in use | meaning |
|---|---|---|
| top | `pass` · `approved` | every dimension at or above its pass threshold and zero blocking findings |
| middle | `needs_iteration` · `changes-requested` | any dimension in the warning band or any blocking finding |
| bottom | `fail` | any dimension below the failure floor |

### Report format

First line: `[<skill-short-name>] <scope, if any> → <verdict> (overall: <n>/100)`, with `✓`
before the bracket on a passing run and `✗` on a failing one. Second line: the dimension
scores joined with ` · `. When the run does not pass, list the blockers:

```
Blocking issues (<n>):
1. [<severity>/<category>] <location>
   "<quoted text>"
   → <resolution>
```

Close with `Re-run <skill> after resolving blocking issues.`

