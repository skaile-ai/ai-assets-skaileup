---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
feature_path: _concept/product-spec/features/team-todo/team-todo-comments.md
phase: align
tier: standard-app
created_at: 2026-05-08T12:34:56Z
last_updated: 2026-05-08T13:30:00Z
---

## Feature recap (1-2 lines)
Members can attach short comments to any team todo item. Comments
appear in chronological order and broadcast to other viewers.

## Concept summary
The comments feature surfaces on the todo item detail panel
(`_concept/experience/screens/team-todo-comments/list.md`) and on the
inline composer modal (`_concept/experience/screens/team-todo-comments/composer.md`).
List view shows author, timestamp, body. Composer accepts plain text up to 2000 chars.
Both screens reuse the existing app shell and are gated behind the team-membership
guard already implemented.

## Open questions surfaced by the grill
1. [P1] When a todo is deleted, what happens to its comments — cascade or orphan?
2. [P2] Is there an edit window after which a comment is locked?
3. [P3] Are emoji reactions in or out of v1?

## Edge cases to handle
- Empty submission: rejected client-side with inline error (traces to Decision Q1).
- Comment > 2000 chars: counter goes red at 1900; submit disabled (traces to feature.md § Constraints).
- Network drop mid-submit: draft preserved in localStorage with retry banner (traces to Decision Q4).
- Two members post simultaneously on the same todo: last-write-wins for ordering; both rows appear (traces to Decision Q3).
- Author deletes own comment after others have replied: replies remain; deleted body shows "[removed]" (traces to Decision Q5).

## Constraints

### Technical
- Stack: Next.js 14 + Postgres + Pusher for broadcast.
- Comment list paginated at N=50 per request; infinite scroll on the panel.
- All mutations through the existing tRPC layer; no new transport.

### Scope
- IN: list, create, edit-own, delete-own.
- DEFERRED to a later slice: moderation by admin, threaded replies, emoji reactions.

### Deadline / supervision
- Tier supervision: mostly autonomous (per scope.yaml.tier=standard-app).
- HITL checkpoint at plan-vertical approval; no HITL during implementation.

## Decisions made
- Q1 (cascade): Yes — comments cascade on todo delete. FK ON DELETE CASCADE.
- Q2 (edit window): Decided to leave edit window unlimited for v1; revisit if abuse appears.
- Q3 (concurrency): Last-write-wins; no conflict UI in v1.
- Q4 (offline draft): localStorage-backed draft per todo; cleared on successful post.
- Q5 (deleted-with-replies): show "[removed]" placeholder, preserve thread integrity.

## Acceptance handoff
- WHEN a member opens a todo item, THE SYSTEM SHALL display all existing comments in chronological order.
- WHEN a member submits a comment with text length > 0 and <= 2000, THE SYSTEM SHALL persist it and broadcast to other viewers within 2 seconds.
- WHEN a member edits their own comment, THE SYSTEM SHALL replace the body and bump last_updated.
- WHEN a member deletes their own comment, THE SYSTEM SHALL replace the body with "[removed]" and preserve replies.
- WHEN a todo item is deleted, THE SYSTEM SHALL cascade-delete all attached comments.
