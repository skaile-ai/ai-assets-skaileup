# Verification Protocol — ts-build-error-after-refactor

## Bug Summary

After renaming `UserService.findById` to `UserService.getById` across the codebase, `bun run build`
fails with `TS2339: Property 'findById' does not exist on type 'UserService'` at five call sites
the rename missed. See `_debug/ts-build-error-after-refactor/context.md` § Symptom.

## Hypothesis Under Test

Hypothesis-specific (confidence: high). The user's hypothesis is that the rename was incomplete —
a few files import `UserService` indirectly through a re-export barrel and were missed by the IDE
rename action. The protocol verifies that ALL `findById` references in `src/**/*.ts` have been
converted to `getById` AND that the build and typecheck pass cleanly.

## Verification Steps

Each step is independently executable. Steps are ordered cheap-to-expensive.

### Step 1: No leftover `findById` callers in source

- **Command:** `git grep -nE '\.findById\s*\(' -- 'src/**/*.ts' 'src/**/*.tsx' || echo NO_MATCHES`
- **Expected output (success):** `/^NO_MATCHES$/`
- **Expected output (still-broken):** `/src\/.*\.tsx?:\d+:.*\.findById\s*\(/`
- **Pass criterion:** stdout is exactly `NO_MATCHES` (no callers remain)

### Step 2: TypeScript typecheck passes

- **Command:** `bun run typecheck`
- **Expected output (success):** `/exit code 0/`
- **Expected output (still-broken):** `/TS2339|TS2551|Property 'findById' does not exist/`
- **Pass criterion:** exit code 0 AND stderr contains no `TS2339` or `TS2551` lines

### Step 3: Production build succeeds

- **Command:** `bun run build`
- **Expected output (success):** `/(✓ built|Compiled successfully|build complete)/`
- **Expected output (still-broken):** `/error during build|Build failed|TS2339/`
- **Pass criterion:** exit code 0 AND stdout matches the success regex

### Step 4: Smoke test the renamed method (unit)

- **Command:** `bun run test -- user.service.test.ts -t "getById"`
- **Expected output (success):** `/Tests\s+\d+ passed/`
- **Expected output (still-broken):** `/Tests\s+\d+ failed|getById is not a function/`
- **Pass criterion:** exit code 0 AND at least one `getById` test passed

## Success Criteria

The bug is verified fixed when ALL of the following hold:

- [ ] Step 1 pass criterion met (no `findById` callers in source)
- [ ] Step 2 pass criterion met (typecheck clean)
- [ ] Step 3 pass criterion met (build succeeds)
- [ ] Step 4 pass criterion met (renamed method covered by passing test)

## Failure Exit Conditions

If any of these occur, STOP the protocol and escalate (typically to `impl-quality/debug-handoff`):

- A step's command errors with a setup failure — `bun: command not found`, `tsconfig.json` missing,
  `node_modules/` not installed.
- A step's output matches neither expected-success nor expected-broken — the build pipeline or test
  runner has changed shape since the protocol was authored.
- Step 1 succeeds (zero callers in `src/`) but Step 2 still fails with `TS2339` — this means the
  hypothesis is wrong: the leftover caller is in a path the grep does not cover (likely
  `tests/**`, `scripts/**`, or a JS file). Switch to a hypothesis-agnostic protocol.

## Notes for Future Re-runs

- The grep in Step 1 covers `src/**/*.ts` and `src/**/*.tsx` only. If the project later adds
  `.mts`, `.cts`, or `.svelte` files using the same service, broaden the glob.
- Step 4 assumes a unit test named `user.service.test.ts` exists. If that test was deleted as part
  of the refactor, replace Step 4 with a typecheck of an explicit smoke file you author for this
  protocol.
- If the codebase uses re-export barrels (`src/services/index.ts` re-exporting `UserService`), the
  IDE rename action will miss callers that import via the barrel. Step 1's grep catches them.
