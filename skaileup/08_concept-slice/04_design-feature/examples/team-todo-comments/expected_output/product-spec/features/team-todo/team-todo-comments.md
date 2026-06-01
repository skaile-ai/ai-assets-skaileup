---
priority: must-have
roles: [guest, member, admin]
permissions:
  guest: [view]
  member: [view, create, edit_own, delete_own]
  admin: [view, create, edit_own, delete_own, moderate]
story_refs: []
agent_notes: |
  Members can attach short comments to any team todo item. Plain text only,
  up to 2000 chars. Members may edit/delete their own; admins may moderate.
  Threaded replies and @mentions are out of scope for v1.
screens:
  - path: experience/screens/team-todo-comments/list.md
  - path: experience/screens/team-todo-comments/detail.md
data_entities: [Comment, Todo, User]
last_updated: 2026-05-08
---

# Comments on team todo items

## Acceptance Criteria

- WHEN a member opens a todo item, THE SYSTEM SHALL display all existing comments in chronological order.
- WHEN a member submits a comment with text length > 0 and <= 2000, THE SYSTEM SHALL persist it and broadcast to other viewers.

## Notes

Edit window is unlimited unless admin moderates. Network drop mid-submit
shows a retry banner and preserves the draft locally.
