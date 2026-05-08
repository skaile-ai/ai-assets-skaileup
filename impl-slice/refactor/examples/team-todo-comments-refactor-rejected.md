---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
feature_path: _concept/product-spec/features/team-todo/team-todo-comments.md
phase: refactor
tier: standard-app
created_at: 2026-05-08T17:00:00Z
last_updated: 2026-05-08T17:45:00Z
---

## Slice goal recap (1-2 lines)
Team members can list, create, edit-own, and delete-own short comments on a team todo item.

## Smallest improvement candidates

### 1. Remove unused `formatComment()` helper
**Type:** subtraction
**Files:** src/components/CommentList.tsx
**Rationale:** The helper is defined but never called.
**Risk:** low — purely a deletion; no call sites exist.
**Behavior preservation:** no behavior to preserve — it's dead code.

## What I considered but rejected (1-3 items)

1. Considered: extract a `<CommentItem>` presentational component out of `<CommentList>`. Rejected: only one caller; not yet a pattern.

## User approval gate
Approval status: rejected

## Applied changes
_(none — user declined refactor)_
