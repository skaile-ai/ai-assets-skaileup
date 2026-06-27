---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
feature_path: _concept/product-spec/features/team-todo/team-todo-comments.md
phase: plan
tier: appbuilder-standard
created_at: 2026-05-08T14:00:00Z
last_updated: 2026-05-08T14:30:00Z
---

## Slice scope
Team members can list, create, edit-own, and delete-own short comments on a team todo item.

## Vertical decomposition

| # | UI | Logic | Data | Notes |
|---|----|-------|------|-------|
| 1 | Comment list on todo detail panel (`screens/team-todo-comments/list.md`) | `comments.listForTodo(todoId)` tRPC query | `comments` table read; FK→`todos` | Cascade delete confirmed during align. |
| 2 | Composer modal (`screens/team-todo-comments/composer.md`) | `comments.create({todoId, body})` mutation; broadcast via Pusher | `comments` row insert; `deleted_at = NULL` | 2-second broadcast SLA from EARS line 2. |
| 3 | Edit-own + delete-own affordances on each comment row | `comments.update(id, body)`, `comments.softDelete(id)` | `comments.body` update; `deleted_at` soft-delete | Soft-delete preserves replies per Decision Q5. |
| 4 | Network-drop retry banner with localStorage draft restore | Draft persistence service in composer modal | localStorage key `comments.draft.<todoId>`; cleared on success | Justifies offline edge case from align. |

## Testing strategy

### Manual checks
- Open a todo, verify all existing comments render in chronological order.
- Post a comment as Member A; confirm it appears for Member B (open in second browser) within 2 seconds.
- Edit own comment; verify body updates and `last_updated` bumps.
- Delete own comment that has replies; verify body shows "[removed]" and replies remain.
- Delete a todo with comments; verify the comments are no longer visible (cascade).

### Automated tests
- [unit] `comments.listForTodo` returns rows ordered by `created_at` ASC.
- [unit] `comments.create` rejects body length 0 and body length > 2000.
- [integration] Member A posts → Pusher broadcast received by Member B's session within 2s.
- [integration] Soft-deleting a comment with replies preserves the reply rows; body returned as `[removed]`.
- [e2e] Cascade delete: deleting a todo removes its comments from the detail panel and the DB.

### Exit criteria
- all rows in `## Vertical decomposition` complete end-to-end
- all 5 automated tests above pass
- all manual checks above verified by user
- `_concept/product-spec/features/team-todo/team-todo-comments.md` § Acceptance Criteria all green

## Anti-horizontal nudge

> **DO NOT build all UI first, then all logic, then all data.**
>
> The default LLM failure mode for implementation planning is horizontal layering: "first scaffold every screen, then wire every handler, then run every migration." This produces N half-finished slices and zero working ones.
>
> Instead: pick ONE row from `## Vertical decomposition` and complete it end-to-end (UI renders → handler responds → data round-trips → test green) BEFORE starting the next row.
>
> If you find yourself thinking any of the following, **stop**:
> - "I'll come back and wire the data after I've built all the screens."
> - "Let me get the UI looking right across the whole feature first."
> - "I'll batch the migrations and run them at the end."
> - "I'll add tests once everything is hooked up."
>
> A row is **not done** until: UI renders real data, the handler is callable from the UI, the data layer persists round-trips, and the test for that row is green. Then — and only then — start the next row.

## Definition of done
- [ ] All vertical rows complete end-to-end (UI + Logic + Data wired)
- [ ] All tests in § "Automated tests" pass
- [ ] All manual checks in § "Manual checks" verified by user
- [ ] No row left half-implemented (no "UI built but data not wired", etc.)
- [ ] `_concept/product-spec/features/<group>/<feature_slug>.md` § Acceptance Criteria all green

## Open carry-overs
- [P3] Emoji reactions deferred to a later slice.
- [P2] Edit-window cap revisited if abuse appears (no v1 enforcement).
