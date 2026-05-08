# impl-plan-align — Grill Style Reference

The implementation-readiness grill is adversarial but constructive. The user
voiced their dream in `concept-slice/brainstorm`; surfaced edges in
`concept-slice/align`; locked screens in `concept-slice/scope-feature`. By
the time `impl-plan-align` runs, the user thinks the feature is well-defined.

This grill checks that assumption.

## Tone

- Pointed, never rude. "What happens when X?" not "You forgot X."
- One question at a time (iron_laws § 9). Bundling questions reads as a
  checklist; users skim checklists and miss the trap question.
- Wait for the answer before sending the next. If the answer is vague, ask
  the same question with a different angle, not a fresh pillar.
- Quote the user's own words back when their answer contradicts a screen
  spec or a brainstorm bullet. Don't accuse — just read it back.

## The 9 Pillars

| Pillar | Good question | Weak question |
|---|---|---|
| State transitions | "If the user starts the flow but doesn't complete it, where does state go — saved, discarded, half-saved?" | "What about partial state?" |
| Boundary inputs | "What's the max length here? What does the system do at zero, one char, max-1, max, max+1?" | "Are there input limits?" |
| Concurrency | "Two members hit save at the same instant on the same row. What's the rule — last-write-wins, optimistic locking, conflict UI?" | "What if there are concurrent edits?" |
| Permissions | "Walk me through the role × action matrix. Guest? Member? Admin? Owner? Fill in every cell." | "Who can do what?" |
| Persistence and offline | "User closes the tab mid-action. What's saved? When they re-open, where do they land?" | "Does it work offline?" |
| Errors | "Network drop, validation error, 500 — what does the user see for each, and what's their next action?" | "What about errors?" |
| Cross-feature data | "Does this read or write any entity owned by another feature? Who owns the contract?" | "Any cross-feature stuff?" |
| Performance | "Worst case: 10 rows, 1k rows, 100k rows. Pagination at what threshold?" | "Will it scale?" |
| Test seam | "How do we know it works without manual clicking? Smallest automated test — unit, integration, e2e?" | "How do we test this?" |

## Anti-patterns

- **Asking the same question the brainstorm already answered.** Read brainstorm.md
  first; if a P1 was answered there, skip the grill question and cite the answer
  in `## Decisions made`.
- **Inventing edge cases the user didn't confirm.** Every bullet in
  `## Edge cases to handle` must trace to a Q/A in `## Decisions made` or a
  feature.md/screen line.
- **Bundling 3 questions into one paragraph.** Ask one question, wait, then ask
  the next. The MUST line at the top of SKILL.md exists for a reason.
- **Re-authoring acceptance criteria.** EARS lines live in feature.md. Copy
  them VERBATIM into `## Acceptance handoff`. Do not rewrite, "improve," or
  fold them into prose.
- **Calling it done without a P1 or P2.** If the grill produces only P3
  questions, the grill was too soft. The validator will fail the file.

## Signals the grill is working

- The user says "huh, I hadn't thought of that" at least once.
- A `## Decisions made` Q/A entry contradicts a brainstorm bullet — and the
  user confirms the new decision.
- The `## Constraints ### Scope` deferred list has 1+ items the user
  originally wanted in v1 but agreed to push back.
- At least one EARS line in `## Acceptance handoff` got tightened during the
  grill (the validator can't catch this — it's a quality signal).
