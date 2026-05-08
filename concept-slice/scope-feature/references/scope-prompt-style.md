# Scope-Feature Prompt Style

Tone reference for `concept-slice-scope-feature`. The agent is a
budget-keeper — friendly but firm.

## Core principles

1. **One question per message.** Iron Law § 9.
2. **Three-way decision, never two.** Always offer IN / OUT / DEFER —
   binary IN/OUT collapses too much nuance and pushes "later" items into
   "out forever".
3. **Force a rationale.** Every decision gets a one-sentence "why".
   This is the artifact future you will thank present you for.
4. **Cite-only.** Don't invent edge cases here. If it isn't in align.md,
   it doesn't get a vote in scope.
5. **Required screens use group form.** `<group>/<screen>` matches the
   `experience/screens/` directory layout. Group is usually the slice's
   feature slug.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Skipping rationales because the user's busy | The rationale IS the artifact's value. |
| Inventing new edge cases mid-scope | That's align's job — go back if needed. |
| Accepting "let's just put it all IN" | Defer is for "we want it but not now". |
| Bare screen slugs (e.g. `login` not `auth/login`) | Breaks the directory mapping. |
| Marking items DEFER with no follow-up note | Deferred items vaporize on slice commit. |

## DEFER follow-up template

Each DEFER bullet needs a "next-revisit" note:

```
- Threaded comments — DEFER. Revisit after first 50 comments observed.
```

Note: deferred items do NOT survive the slice commit. They are visible
during the slice (in `_slice/concept/<id>/scope-feature.md`) and lost
afterward. This is intentional (matches `impl-slice/commit`'s scratch
deletion). If the user wants persistence, they should put it in product
backlog tooling, not the slice scratch.

## The "owned by another feature" bucket

If an edge case surfaces and aligns with a sibling feature already in
`_concept/experience/features/`, mark it as Owned-by-another-feature
and cite the path. This keeps slices from claiming each other's
territory.
