---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
phase: scope-feature
tier: standard-app
created_at: 2026-05-08T12:34:56Z
last_updated: 2026-05-08T13:30:00Z
---

## In scope
- Plain-text comments up to 2000 chars — covers the primary use case.
- Member edits and deletes their own comments — basic affordance.

## Out of scope
- Threaded replies — adds complexity not needed for v1.

## Deferred
- @mentions — revisit after observing first 50 comments in production.

## Owned by another feature
- User profile rendering — owned by experience/features/users/profile.md.

## Acceptance criteria (final)
- WHEN a member opens a todo item, THE SYSTEM SHALL display all existing comments in chronological order.
- WHEN a member submits a comment with text length > 0 and <= 2000, THE SYSTEM SHALL persist it and broadcast to other viewers.

## Required entities
- Comment
- Todo
- User

## Required screens
- team-todo-comments/list
- team-todo-comments/detail
