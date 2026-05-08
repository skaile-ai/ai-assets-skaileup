# Anti-addition rules

Long-form expansion of "AI defaults to adding complexity." Read this before
generating candidates in `impl-slice-refactor`.

## Why the LLM adds

Three reinforcing biases push the model toward additions:

1. **Pattern matching from training data.** Training corpora over-represent
   "extract a helper", "split into container + presentational", "introduce a
   utility". Those patterns are useful at scale and harmful at one caller.
2. **Reward for cleverness.** A new abstraction looks like insight ("see, I
   spotted the pattern"), while a deletion looks like clean-up ("just removed
   dead code"). The former feels more impressive — but only the latter
   reduces the future reader's load.
3. **Aversion to confronting smell.** When a file is messy, adding a layer
   of indirection feels like "fixing" it without actually doing the work of
   removing the mess. The mess is still there; now there's a wrapper around
   it too.

The schema in `impl-slice-refactor` deliberately omits an "addition" Type.
If you cannot fit an idea into `subtraction | simplification | clarification`,
it is OUT OF SCOPE for this skill.

## Three counter-examples

These are refactors that LOOK like simplifications but are additions in
disguise. Surface them in `## What I considered but rejected (1-3 items)`,
not in the candidate list.

### 1. "Extract a useFormState hook from one form"

- **Looks like:** simplification — removes inline state from the component.
- **Actually:** adds a new abstraction with one caller.
- **Future cost:** every reader of the component now also has to read
  `useFormState`. Net mental load went UP, not down.
- **Fix:** if there were 3 callers and a clear pattern, the extraction would
  pay for itself. With 1 caller, leave the inline state alone.

### 2. "Split <UserList> into <UserListContainer> + <UserListPresentational>"

- **Looks like:** clarification — separates concerns.
- **Actually:** adds a layer with no concrete benefit yet (no second
  presentational caller, no testing pain that demands the split).
- **Future cost:** reader now has to navigate two files for one screen.
- **Fix:** keep `<UserList>` as a single component until a real second
  caller appears.

### 3. "Introduce a validateUser() utility"

- **Looks like:** subtraction — collapses 3 inline validation lines into a
  function call.
- **Actually:** addition — the function lives somewhere new, and the call
  site still needs to know what it does.
- **Future cost:** net code increase (the inline 3 lines → 1 call site +
  the new function definition + the export).
- **Fix:** if the same validation appears at 4 call sites, extract.
  At one call site, leave it inline.

## Healthy refactor types

- **Subtraction:** delete dead code, dead branches, dead exports, dead
  imports. The ideal candidate. Risk is "low" by default.
- **Simplification:** collapse 2 paths into 1; remove a flag whose only
  value is the default; replace a multi-step transform with a single
  expression. Always verify behavior preservation.
- **Clarification:** rename a function whose name lies; rename a variable
  whose role is misleading; add a one-line comment that explains an
  irreducible "why".

## Decision tree

```
Tempted to add? STOP.
  └── Re-read the candidate from a code-deletion perspective.
        ├── Could this be removed instead?              YES → propose subtraction
        ├── Could two paths collapse into one?          YES → propose simplification
        ├── Is the issue a misleading name?             YES → propose clarification
        └── Otherwise                                          → record in "## What I considered but rejected"
```
