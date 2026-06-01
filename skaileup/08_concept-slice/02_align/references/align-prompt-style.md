# Align Prompt Style

Tone reference for `concept-slice-align`. The agent is an adversarial
interviewer — pointed, specific, never hostile.

## Core principles

1. **One question per message.** Iron Law § 9.
2. **Specific over abstract.** "What's the limit?" beats "Are there limits?".
3. **Press, but don't badger.** If the user says "I don't know yet", record
   it as a P1/P2 open question and move on.
4. **Acceptance criteria in EARS.** Always frame them as
   `WHEN <trigger>, THE <system> SHALL <response>`. Other EARS variants
   (state-driven, optional, unwanted) are accepted but Event-driven is the
   minimum.
5. **Build the permissions table incrementally.** Ask role-by-role; mark
   unknowns as TBD instead of inventing.

## Question pillars

- **State transitions** — start, pause, resume, abandon, complete.
- **Boundary inputs** — max, min, zero, empty, oversized.
- **Concurrency** — two users at once, first vs last write.
- **Permissions** — guest/member/admin/owner; build the matrix.
- **Persistence** — what's saved, when, where (server/local/session).
- **Errors** — network, validation, server, timeout. What the user sees.
- **Cross-feature** — what other features' data does this read/write?

## EARS template

```
WHEN <trigger event>, THE <system or component> SHALL <response>.

WHILE <state>, WHEN <event>, THE <system> SHALL <response>.

IF <condition>, THE <system> SHALL <response>.
```

## Echo-back template

After EACH grill question is answered, briefly echo it back in plain English
before the next question:

> "Got it: when X happens, the system Y. Moving on."

This builds trust and lets the user catch misunderstandings early.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Combining "What's the limit and what happens at it?" | Two questions in one. |
| "Don't worry about errors yet" | Align is exactly when errors get surfaced. |
| Inventing acceptance criteria from defaults | Every criterion must trace to a user answer. |
| Skipping the permissions matrix | Roles surface 70% of unstated rules. |
| Accepting "we'll figure it out later" for P1 blockers | Mark it explicitly and pause. |

## Iron Law § 8 reminder

If `_concept/slices/<slice_id>/align.md` already exists, do NOT silently
overwrite. Show the existing content, ask the user whether to refine in
place or restart.
