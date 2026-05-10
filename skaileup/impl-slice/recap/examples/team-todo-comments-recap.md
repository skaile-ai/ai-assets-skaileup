---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
feature_path: _concept/product-spec/features/team-todo/team-todo-comments.md
phase: recap
tier: standard-app
created_at: 2026-05-08T16:45:00Z
last_updated: 2026-05-08T16:45:00Z
---

## Slice goal recap (1-2 lines)
Team members can list, create, edit-own, and delete-own short comments on a team todo item.

## What was built (1-3 sentences)
Team members can now open a todo and see its comments in chronological order, post new comments that other members see within ~1.5 seconds, and edit or soft-delete their own comments while preserving any replies. Drafts survive a network drop via localStorage so a user can keep typing offline and submit when reconnected.

## ASCII diagram

```
+-----------------+    submit    +------------------+    insert     +--------------+
| Composer modal  | -----------> | comments.create  | ------------> | comments     |
| (todo detail)   | <----------- |  tRPC mutation   | <------------ |  table       |
+--------+--------+   201 + row  +--------+---------+   row back    +------+-------+
         |                                |                                 |
         |                                v                                 |
         |                         +------+-------+                         |
         |                         |  Pusher      |                         |
         |                         |  broadcast   |                         |
         |                         +------+-------+                         |
         |                                |                                 |
         |                                v                                 |
         |                         +------+--------+                        |
         |                         | Member B's    |                        |
         |                         | live list     | <----------------------+
         |                         +---------------+    listForTodo
         |
         | network drop
         v
+--------+----------+
| localStorage      |
| comments.draft.<id> |
+-------------------+
```

## Files touched
- src/components/CommentList.tsx (new)
- src/components/CommentComposer.tsx (new)
- src/server/api/routers/comments.ts (new)
- src/server/db/schema/comments.ts (new)
- migrations/20260508_add_comments.sql (new)
- src/components/TodoDetailPanel.tsx (modified)

## Outcome vs. plan
### Met expectations
- All vertical rows complete end-to-end (UI + Logic + Data wired).
- All 5 automated tests in plan.md "### Automated tests" pass.
- All 5 manual checks verified by user.
- Soft-delete preserves reply rows and renders body as `[removed]` (matches plan row 3).

### Deviated
- Pusher broadcast SLA observed at ~1.5s instead of strict 2s budget; well within tolerance, no plan change required.

### Carried over
- [P3] Emoji reactions deferred to a later slice.
- [P2] Edit-window cap revisited if abuse appears (no v1 enforcement).
