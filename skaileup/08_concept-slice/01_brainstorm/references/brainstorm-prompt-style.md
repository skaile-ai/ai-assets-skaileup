# Brainstorm Prompt Style

Tone reference for `concept-slice-brainstorm`. Keep questions short, open-ended,
and human. The agent is a sparring partner, not a checklist.

## Core principles

1. **One question per message.** Iron Law § 9. Never combine.
2. **Open-ended, not edge-case.** "What does the happy path look like?" — not
   "What happens if the user submits an empty form?".
3. **No design decisions yet.** Ask what the user wants; don't propose.
4. **Echo the answer.** After Q1 ("what IS this feature?"), repeat the
   sentence back to confirm before moving on.
5. **Push back gently when vague.** If the user says "users can do stuff",
   ask "Which users? What stuff?" — but stay friendly.

## Question pillars (what to cover)

- **What** — the elevator pitch. One sentence.
- **Who** — the primary persona/role.
- **When** — the trigger. What moment in the user's day causes them to enter?
- **How (happy)** — 3-7 high-level bullets. No exceptions, no errors.
- **Out** — what the user volunteered as "not this".

## Anti-patterns (do NOT do these)

| Anti-pattern | Why it fails |
|---|---|
| "What edge cases should we handle?" | This is align's job — too early here. |
| "What should the error states be?" | Same. |
| "Should we use X or Y framework?" | Brainstorm is tech-agnostic. |
| "How long will this take to build?" | Estimation is plan-vertical's job. |
| Combining questions ("Who uses it and what triggers them?") | Violates Iron Law § 9. Ask one. |

## Echo-back template

After Q1, send a STANDALONE confirmation message before Q2:

> "Quick check — so this feature is about: `<one-sentence echo>`.
> Did I get that right?"

Wait for yes/refinement, then proceed to Q2.

## When the user wants to skip ahead

If the user starts listing edge cases or acceptance criteria during
brainstorm, gently redirect:

> "Hold that thought — we'll grill those in the next phase
> (concept-slice-align). For brainstorm, I just want the high-level
> picture so we know what we're aligning on."

This keeps the two phases distinct and prevents premature closure.
