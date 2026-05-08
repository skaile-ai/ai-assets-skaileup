# Verification Protocol — login-test-flaky

## Bug Summary

The Vitest unit test `auth/login.test.ts > should redirect after login` fails approximately 1 in 5
CI runs with a timeout, even though the same test passes locally on every run. See
`_debug/login-test-flaky/context.md` § Symptom for the full observation log.

## Hypothesis Under Test

Hypothesis-agnostic. The protocol checks only that the symptom (intermittent failure) is gone — it
does not assume a specific cause. The user has no high-confidence hypothesis yet, so we verify by
brute-force pass rate.

## Verification Steps

Each step is independently executable. Steps are ordered cheap-to-expensive so the protocol bails
early on the first signal of failure.

### Step 1: Lint and typecheck still clean

- **Command:** `bun run lint && bun run typecheck`
- **Expected output (success):** `/exit code 0/`
- **Expected output (still-broken):** `/error TS\d+|✖ \d+ problems/`
- **Pass criterion:** exit code 0 AND stderr contains no `error TS` lines

### Step 2: Single run of the targeted test

- **Command:** `bun run test -- auth/login.test.ts -t "should redirect after login"`
- **Expected output (success):** `/Tests\s+1 passed/`
- **Expected output (still-broken):** `/Tests\s+1 failed|TimeoutError/`
- **Pass criterion:** exit code 0 AND stdout matches `Tests\s+1 passed`

### Step 3: Twenty-run pass-rate gate (the actual flakiness check)

- **Command:** `for i in $(seq 1 20); do bun run test -- auth/login.test.ts -t "should redirect after login" --reporter=basic >/tmp/login-flaky-$i.log 2>&1 && echo PASS || echo FAIL; done | sort | uniq -c`
- **Expected output (success):** `/^\s*20 PASS$/` (twenty PASS lines, zero FAIL lines)
- **Expected output (still-broken):** `/FAIL/` (any FAIL line at all)
- **Pass criterion:** stdout shows exactly `20 PASS` and no `FAIL` lines — pass rate must be 20/20, not just 19/20, because one flake means the bug is still latent

### Step 4: CI parity — run with the same env vars CI uses

- **Command:** `CI=true TZ=UTC bun run test -- auth/login.test.ts -t "should redirect after login"`
- **Expected output (success):** `/Tests\s+1 passed/`
- **Expected output (still-broken):** `/Tests\s+1 failed|TimeoutError/`
- **Pass criterion:** exit code 0 AND stdout matches `Tests\s+1 passed`

## Success Criteria

The bug is verified fixed when ALL of the following hold:

- [ ] Step 1 pass criterion met (lint and typecheck clean)
- [ ] Step 2 pass criterion met (single run passes)
- [ ] Step 3 pass criterion met (20/20 pass rate)
- [ ] Step 4 pass criterion met (CI-parity run passes)

## Failure Exit Conditions

If any of these occur, STOP the protocol and escalate (typically to `impl-quality/debug-handoff`):

- A step's command errors with a setup failure — `bun: command not found`, missing `node_modules/`,
  or `auth/login.test.ts` missing.
- A step's output matches neither the expected-success nor the expected-broken regex — the protocol
  is stale and the test or framework has changed shape.
- Step 3 retried with `N=3` reruns and at least one cohort still showed any FAIL line.

## Notes for Future Re-runs

- Step 3 is by far the most expensive (~20 × test runtime). If it fails fast on the first FAIL, you
  do not need to wait for all 20 — stop and escalate.
- The 20/20 threshold is deliberate. Earlier protocols allowed 19/20 and we shipped a "fix" that
  reduced flake rate from 1/5 to 1/20 without addressing the root cause.
- If `TZ=UTC` matters for reproduction, capture which timezone the user's local was in — past
  flakes correlated with `TZ=Europe/Berlin` on Sundays during DST transitions.
