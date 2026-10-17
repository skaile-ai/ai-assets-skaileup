---
path: [_concept/11_build/reviews/, _concept/11_build/reviews/<feature_slug>.yaml]
summary: one feature's code-review verdict and findings
writers: [quality-review]
---

# _concept/11_build/reviews/

`<feature_slug>.yaml` is the verdict on one feature's shipped code: the one place the
collection judges the built feature against its spec, so `build-implement`, `ops-review` and
`quality-release` do not repeat it. Forge-concept's review page reads three names from it
(`feature`, `verdict`, `findings[].severity`); spelled any other way the feature renders with
no verdict at all. Stance, severities and the blocking rule are
`tree/11_build/README.md § Verdicts`: `approved` means zero `critical` and zero `high`.

## Format

```yaml
feature: <feature_slug>          # the id the host joins trace, ledger and review on
verdict: approved | changes-requested
commits: [<sha>, ...]
files_reviewed: [<path>, ...]
findings:
  - id: F-1
    severity: high               # critical | high | medium | low
    category: security           # standards | spec | security | accessibility | criteria
    file: <path>
    line: <n>
    criterion: ""                # AC-<story-id>-<nn> when the finding is a ledger row that does not hold
    note: <what the code does, against what the spec or criterion says>
    resolution: <the specific change that clears it>
last_updated: YYYY-MM-DD
```

## Writing it

Reviews **one feature's shipped code**. How to read a diff is the global `code-review` skill's job; this procedure supplies the two inputs `code-review` otherwise asks a human for (the fixed point, from the feature's row in `tree/11_build/trace.md`, and the spec, the feature file) plus the axes a two-axis diff review does not carry. The verdict file and the ledger rows re-checked in step 5 are the only things it writes: a finding fixed during the review is a finding that never reached the ledger.

1. **Resolve the feature and its trace row.** Glob `_concept/05_features/*/<feature_slug>.md`; zero matches or two is a question for the user and not a guess. Read the feature's entry in `_concept/11_build/trace.yaml`: its slices' `commits` and `code`. A missing entry or empty `commits` stops the run and names `build-implement`, which writes the entry when a slice commits; without it there is no fixed point and a review quietly widens to the whole repository.
2. **Build and test before reading a line.** Run the project's own build and test commands. A red build makes every finding provisional, so stop there, call the Skill tool with "diagnosing-bugs" and come back once it is green; without it, hand the failure to the user with the failing command and stop.
3. **Call the Skill tool with "code-review" from a context that did not write the code.** If `code-review` is not installed, the review stops and names it. The fixed point is the parent of the earliest sha in the trace row's `commits`; the spec is the feature file. Dispatch it as a subagent, since the session that implemented the slice reads its own diff as correct. Hand it `_concept/02_grounding/standards/` alongside whatever the repo documents, where that exists: a convention this project was measured to follow outranks the generic smell baseline. Keep its two axes, Standards and Spec, apart in your own report, because merging them into one ranked list is the masking the split prevents.
4. **Add the two axes `code-review` has no eye for**, per `## Checks`: security and data integrity across every route the diff touches, and accessibility across every screen it renders. Each hit is a finding with a file and a line.
5. **Re-check the ledger** per `tree/11_build/acceptance-criteria/README.md § Reading`.
6. **Read the accepted debt before writing findings.** `_concept/11_build/slices/<slice_id>/index.md` records what the simplification pass deliberately left in place (`tree/11_build/slices/[slice_id]/index.md`). Debt recorded there is context and not a finding; re-flagging it spends the reader's attention on a decision already made.
7. **Write the verdict** to `_concept/11_build/reviews/<feature_slug>.yaml` in the shape above.
8. **Report by axis**: Standards, Spec, Security, Accessibility, Criteria, each with its findings ordered by severity inside the axis and never across axes. On `changes-requested`, call the Skill tool with "diagnosing-bugs" against the findings and name this file as the one to re-run against; without it, the findings go to the user as they stand.

## Checks

The review scope is the `commits` diffs plus the current contents of the `code` files, both from the feature's trace row. A hit is a finding only with a file, a line and the specific change that clears it; "consider reviewing auth here" is a note to nobody.

- Every finding carries a file, a line and a resolution; the verdict is `approved` only where no finding is `critical` or `high`.

### Security and data integrity

Scope: every route, handler, query and form the diff touches.

- **Injection.** User input reaching a query, a shell command or a template without parameterisation or escaping.
- **Authorisation.** Every route the diff adds or changes, checked against the feature's `permissions:` table; a route with no check is a finding even when the UI never links to it, because the UI is not the boundary.
- **Row-level scoping.** A query that filters by id but not by owner, tenant or workspace returns another user's data the moment an id is guessed.
- **Secrets.** Keys, tokens or connection strings in source, in fixtures, or in a committed `.env`.
- **Input validation at the boundary.** Types accepted from the network validated where they arrive and not three calls in.
- **XSS and unsafe deserialisation.** Raw HTML interpolation, `dangerouslySetInnerHTML`, `eval`, and object deserialisation from untrusted payloads.
- **CSRF.** State-changing requests that rely on a cookie with no token or same-site policy.

### Accessibility

Scope: every screen the diff renders or changes.

- **States.** Loading, error and empty each render something a user can read; a screen that shows nothing while it loads is indistinguishable from a broken one.
- **Keyboard.** Every interactive element reachable and operable without a mouse, in an order that matches the visual one.
- **Focus.** A visible focus indicator, and focus moved deliberately when a dialog opens or a route changes.
- **Labels.** Every input, button and icon-only control carries an accessible name.
- **Semantics.** Headings, landmarks and roles used for what they mean, so the structure survives without the styling.
- **Contrast.** Text and interactive elements against their real background, at WCAG AA.
