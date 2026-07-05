---
feature_ref: _concept/experience/features/02_tasks/team-todo-comments.md
screen_refs:
  - _concept/experience/screens/02_tasks/task-detail.md
story_refs: [collaborate_on_task]
derived_from:
  - requirements: 3
  - screen_states: 2
  - behavior_rules: 0
last_updated: 2026-07-05
---

# Acceptance Criteria: Team Todo Comments

## AC-1: Member posts a comment

**Given** a signed-in member viewing a task with 0 comments
**When** they submit "Looks good" in the comment box
**Then** the comment appears in the thread without a page reload

- Assert: thread shows exactly 1 comment with text "Looks good"
- Assert: comment shows the member's display name from seed scenario `populated`

**Test type:** assertion
**Seed scenario:** populated

## AC-2: Empty comment is rejected

**Given** a signed-in member viewing a task
**When** they submit an empty comment
**Then** the form shows exactly "Comment cannot be empty" and no comment is created

- Assert: error text equals "Comment cannot be empty"
- Assert: comment count is unchanged

**Test type:** assertion
**Seed scenario:** populated

## AC-3: User Flow (snapshot)

**Given** a signed-in member on the task list
**When** they open a task, post a comment, and reload
**Then** the comment persists and is visible to another member

**Test type:** snapshot
**Seed scenario:** populated

## Criteria Status

| ID | Source | Status | Updated by | Date |
|---|---|---|---|---|
| AC-1 | collaborate_on_task: WHEN a member submits a comment THE SYSTEM SHALL append it to the task thread | untested | - | - |
| AC-2 | collaborate_on_task: IF the comment is empty THEN THE SYSTEM SHALL reject it with a message | untested | - | - |
| AC-3 | journey snapshot: collaborate_on_task happy path | untested | - | - |
