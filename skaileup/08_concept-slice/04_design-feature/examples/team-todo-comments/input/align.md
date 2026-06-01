---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
phase: align
tier: standard-app
created_at: 2026-05-08T12:34:56Z
last_updated: 2026-05-08T13:00:00Z
---

## Feature recap (one sentence)
Members can attach short comments to any team todo item.

## Acceptance criteria (EARS)
- WHEN a member opens a todo item, THE SYSTEM SHALL display all existing comments in chronological order.
- WHEN a member submits a comment with text length > 0 and <= 2000, THE SYSTEM SHALL persist it and broadcast to other viewers.

## Edge cases
1. Empty submission — should be rejected client-side.
2. Comment exceeds 2000 chars — show count + reject.

## Error states
- Network drop mid-submit — show retry banner; preserve draft locally.

## Permissions / roles
| Role   | View | Create | Edit own | Delete own | Moderate |
|--------|------|--------|----------|------------|----------|
| guest  | x    |        |          |            |          |
| member | x    | x      | x        | x          |          |
| admin  | x    | x      | x        | x          | x        |

## Unstated assumptions exposed
- Edit window is unlimited unless admin moderates.

## Resolved questions
- Q: Threaded replies? A: Out of scope for v1.

## Open questions blocking scope-feature
- None.
