---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
feature_path: _concept/product-spec/features/team-todo/team-todo-comments.md
phase: refactor
tier: appbuilder-standard
created_at: 2026-05-08T17:00:00Z
last_updated: 2026-05-08T17:30:00Z
---

## Slice goal recap (1-2 lines)
Team members can list, create, edit-own, and delete-own short comments on a team todo item.

## Smallest improvement candidates

### 1. Remove unused `formatComment()` helper
**Type:** subtraction
**Files:** src/components/CommentList.tsx
**Diff sketch:**
```diff
-function formatComment(c: Comment): string {
-  return `${c.body} (${c.author})`;
-}
-
 export function CommentList({comments}: Props) {
   return <ul>{comments.map(c => <CommentItem c={c} />)}</ul>;
 }
```
**Rationale:** The helper is defined but never called — `CommentItem` renders the body directly. Dead code only confuses the next reader.
**Risk:** low — purely a deletion; no call sites exist (verified via grep).
**Behavior preservation:** no behavior to preserve — it's dead code. Test suite passes unchanged.

### 2. Rename `handle()` to `submitComment()` for clarity
**Type:** clarification
**Files:** src/components/CommentComposer.tsx
**Diff sketch:**
```diff
-  const handle = async (e: FormEvent) => {
+  const submitComment = async (e: FormEvent) => {
     e.preventDefault();
     await comments.create.mutate({todoId, body});
   };

-  return <form onSubmit={handle}>...</form>;
+  return <form onSubmit={submitComment}>...</form>;
```
**Rationale:** `handle` is a generic name that hides intent. `submitComment` matches what the function does and aligns with the surrounding `comments.create` vocabulary.
**Risk:** low — pure rename; TypeScript catches stale references at compile time.
**Behavior preservation:** test suite passes unchanged; manual smoke check confirmed composer still submits.

## What I considered but rejected (1-3 items)

1. Considered: extract a `<CommentItem>` presentational component out of `<CommentList>`. Rejected: only one caller; not yet a pattern, and the inline JSX is 6 lines.
2. Considered: extract `formatTimestamp()` utility used by `CommentItem` and `TodoDetailPanel`. Rejected: the two call sites format slightly differently — extracting now would force a premature unification.

## User approval gate
Approval status: approved

## Applied changes
- src/components/CommentList.tsx — removed `formatComment()` helper (1 hunk, -4 lines).
- src/components/CommentComposer.tsx — renamed `handle` → `submitComment` (1 hunk, 2 references updated).
