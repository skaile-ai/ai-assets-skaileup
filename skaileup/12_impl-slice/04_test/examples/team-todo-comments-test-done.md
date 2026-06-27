---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
feature_path: _concept/product-spec/features/team-todo/team-todo-comments.md
phase: test
tier: appbuilder-standard
created_at: 2026-05-08T15:00:00Z
last_updated: 2026-05-08T16:30:00Z
---

## Slice goal recap (1-2 lines)
Team members can list, create, edit-own, and delete-own short comments on a team todo item.

## Manual checks done
- [PASS] Open a todo, verify all existing comments render in chronological order. — list renders correctly.
- [PASS] Post a comment as Member A; confirm it appears for Member B (open in second browser) within 2 seconds. — observed ~1.2s broadcast.
- [PASS] Edit own comment; verify body updates and `last_updated` bumps. — body updates; timestamp ticks.
- [PASS] Delete own comment that has replies; verify body shows "[removed]" and replies remain. — soft-delete fixed; replies survive.
- [PASS] Delete a todo with comments; verify the comments are no longer visible (cascade). — works as expected.

## Automated tests run
- [PASS] [unit] `comments.listForTodo` returns rows ordered by `created_at` ASC. — ran `bun test comments.list`; exit 0.
- [PASS] [unit] `comments.create` rejects body length 0 and body length > 2000. — ran `bun test comments.create`; exit 0.
- [PASS] [integration] Member A posts → Pusher broadcast received by Member B's session within 2s. — ran `bun test comments.broadcast`; exit 0.
- [PASS] [integration] Soft-deleting a comment with replies preserves the reply rows; body returned as `[removed]`. — ran `bun test comments.softDelete`; exit 0.
- [PASS] [e2e] Cascade delete: deleting a todo removes its comments from the detail panel and the DB. — ran `bun test e2e.todoDelete`; exit 0.

## Usability observations
- Composer modal opens fast; nothing surprising.
- Header label "Comments (N)" was reworded to "N comments" per prior round; reads cleanly now.
- Esc-to-close hint added to composer; new users picked it up immediately.
- Density on todo detail panel is fine.

## Outstanding issues
_(none)_

## Decision
Decision: Done
