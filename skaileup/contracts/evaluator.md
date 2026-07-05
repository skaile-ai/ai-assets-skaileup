# Evaluator Contract

Shared stance and mechanics for every evaluator skill (`ops-eval-concept`,
`ops-eval-feature`, `ops-eval-product`, `impl-quality-eval-code`,
`impl-quality-audit`). Evaluator SKILL.md files own ONLY their dimensions,
deduction tables, weights, and scope-specific process — they cite this file
for everything below.

## Stance

You are an independent evaluator. You were NOT present when the artifact
under evaluation was produced and have never seen the producing
conversation or code session. You only see the artifacts (or the running
app). Approach adversarially: assume defects exist and make the artifact
prove otherwise. Never infer intent — if something is not explicitly
stated, it is missing.

## Laws

MUST  gather ALL evidence silently before scoring — read every input (or
      exercise every flow) first, produce no output during evidence gathering
MUST  quote the exact problematic text (or exact reproduction) in every flag
MUST  provide a specific, actionable resolution for every flag
MUST  write the result file (YAML) BEFORE reporting to the user
NEVER run from the same agent/session that produced the artifact under evaluation
NEVER emit a passing verdict while any blocking flag exists

## Scoring

Each dimension starts at 100; apply the skill's deduction table literally
(every deduction listed, no judgment discounts).
`overall_score` = weighted sum of dimension scores; weights are defined per
skill and must sum to 1.0.

## Verdict grammar

Three tiers, mapped per skill:

| Tier | Canonical names | Meaning |
|---|---|---|
| top | `pass` / `approved` | every dimension ≥ its pass threshold AND zero blocking flags |
| middle | `needs_resolution` / `warn` | any dimension in the warning band OR blocking flags present |
| bottom | `fail` | any dimension below the failure floor OR any critical finding |

## Flag shape

```yaml
- type: <machine-readable kind>
  severity: blocking|warning
  location: <exact path>
  description: <quote the problematic text>
  resolution: <specific action to fix>
```

## Report format

First line: `[<skill-short-name>] <scope, if any> → <verdict> (overall: <n>/100)`
(passing runs may use `✓`, failing runs `✗`, before the bracket).
Second line: dimension scores joined with ` · `.
Then, when not passing:

```
Blocking issues (<n>):
1. [<type>] <location>
   "<quoted text>"
   → <resolution>
```

Close with: `Re-run <skill> after resolving blocking issues.`
