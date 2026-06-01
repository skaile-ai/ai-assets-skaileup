---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
feature_path: _concept/product-spec/features/team-todo/team-todo-comments.md
phase: test
tier: standard-app
created_at: 2026-05-08T15:00:00Z
last_updated: 2026-05-08T15:30:00Z
---

## Slice goal recap (1-2 lines)
Team members can list, create, edit-own, and delete-own short comments on a team todo item.

## Manual checks done
- [PASS] Open a todo, verify all existing comments render in chronological order. — list renders 4 fixtures correctly.
- [PASS] Post a comment as Member A; confirm it appears for Member B (open in second browser) within 2 seconds. — observed ~1.4s broadcast.
- [PASS] Edit own comment; verify body updates and `last_updated` bumps. — body updates; timestamp ticks.
- [FAIL] Delete own comment that has replies; verify body shows "[removed]" and replies remain. — replies vanish; soft-delete cascade is wrong.
- [PASS] Delete a todo with comments; verify the comments are no longer visible (cascade). — works as expected.

## Automated tests run
- [PASS] [unit] `comments.listForTodo` returns rows ordered by `created_at` ASC. — ran `bun test comments.list`; exit 0.
- [PASS] [unit] `comments.create` rejects body length 0 and body length > 2000. — ran `bun test comments.create`; exit 0.
- [PASS] [integration] Member A posts → Pusher broadcast received by Member B's session within 2s. — ran `bun test comments.broadcast`; exit 0.
- [FAIL] [integration] Soft-deleting a comment with replies preserves the reply rows; body returned as `[removed]`. — ran `bun test comments.softDelete`; exit 1 (replies cascaded).
- [PASS] [e2e] Cascade delete: deleting a todo removes its comments from the detail panel and the DB. — ran `bun test e2e.todoDelete`; exit 0.

## Usability observations
- Composer modal opens fast; nothing surprising about the open-close flow.
- "Comments (3)" header label confused tester until they saw the count update — could be "3 comments" for clarity.
- New users would not know the modal can be closed with Esc; consider a hint.
- Density on the todo detail panel is fine; comment list does not crowd the description.

## Outstanding issues
1. [BLOCKER] Soft-delete cascade incorrectly removes replies when parent comment is deleted (manual check #4 + integration test). Trace to `comments.softDelete` deletion semantics.
2. [SHOULD-FIX] Header label "Comments (3)" reads awkwardly; consider "3 comments".
3. [NICE-TO-HAVE] Add Esc-to-close hint on composer modal.

## Decision
Decision: Needs more work
