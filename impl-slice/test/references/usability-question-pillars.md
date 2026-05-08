# Usability question pillars

The four pillars of the per-slice usability interview. Each interview question
is its own STANDALONE assistant message (Iron Law § 9). Send one, wait, then
the next.

## The 4 default prompts

1. **Friction.** "Did the flow feel awkward — too many clicks, too much text, hidden state?"
2. **Surprise.** "Was anything surprising — buttons in wrong places, naming inconsistent with the rest of the app?"
3. **Onboarding.** "Would a new user get stuck anywhere?"
4. **Density.** "Does any screen have too much going on?"

## Alternative phrasings (substitute when one of the pillars doesn't fit)

- Friction alternates:
  - "Where did your hands hesitate? What screen made you read twice?"
  - "Is anything noisy — animations, banners, microcopy that competes for the eye?"
- Surprise alternates:
  - "What did you expect that didn't happen?"
  - "What labels lie — promising more than the action delivers?"
- Onboarding alternates:
  - "What would a 5-year-old not get?"
  - "Imagine someone who has never seen the app. Where would they pause?"
- Density alternates:
  - "Which screen has the most going on? Could anything be moved or removed?"
  - "Does this slice add a 'noisy' surface to a previously quiet flow?"

## Tone

- Friendly, curious, and SHORT. The user has just finished implementing — long
  questions test patience, not usability.
- NOT leading. Don't ask "is anything broken?" — that prompts a defensive
  "no, looks fine." Ask "what would surprise a new user?" — that prompts
  reflection.
- Single concrete frame per question. Avoid "is anything friction-y, surprising,
  or noisy?" That's three pillars in one and the user will pick whichever is
  easiest to answer.
- Allow "nothing" as a valid answer. If the user says "nothing felt off,"
  record that verbatim — it IS a usability observation.

## What the answers feed into

- Each answer becomes a bullet in `## Usability observations`.
- If the user flags a concrete issue, the skill promotes it to `## Outstanding
  issues` with a tag (`[BLOCKER]`, `[SHOULD-FIX]`, or `[NICE-TO-HAVE]`).
- The default tag for a user-flagged issue is `[SHOULD-FIX]`. Only promote to
  `[BLOCKER]` if the user uses words like "this is broken," "I can't ship this,"
  or "this is wrong." Demote to `[NICE-TO-HAVE]` only on explicit user override.
