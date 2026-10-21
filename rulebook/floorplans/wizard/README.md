---
id: wizard
kind: screen
summary: "Guided linear task: independent steps, a summary step, a completion state"
posture: transient
density: comfortable
---

# wizard — A guided, linear task

A task done rarely, in steps that are mostly independent of each other, by someone who is not yet expert in it: onboarding a client project, importing a file, setting up a workspace. The screen shows the list of steps, one step's body, and a footer that moves back and forward; the last step summarises everything and the flow ends on a completion state (`rulebook/rules.md § P31`). Chosen per `rulebook/rules.md § P18` only when the steps are independent; steps that need each other's content sit on one screen (`rulebook/rules.md § P24`), and routine daily work is never a wizard (`rulebook/rules.md § P19`).

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the shell frame's top strip |
| `step-list` | navigation | — | every step by name with its state (done, current, to do), step n of m |
| `step-body` | primary | 1 | the one current step: its fields, or the summary, or the completion state |
| `step-help` | secondary | 2 | the source a value depends on and a one-line hint for this step |
| `footer` | chrome | — | Back left, Cancel, one primary Next (Create on the summary step) at the right |

Tier 3 does not surface in a wizard: a step asks only for what the task needs, and a field the person rarely sets belongs to the object's own editor after completion, or behind a named "More options" disclosure in `step-body` (`rulebook/rules.md § P21`).

## Posture and density

Transient (`rulebook/rules.md § P19`): one view, labelled buttons with full verbs, Esc and Enter work, the last values are remembered for the next run; no nested dialog or tab. Density `comfortable` (`rulebook/rules.md § P20`): fewer fields per screen, larger targets, room for one-line help.

## Responsive

- **Wide (≥ 960 px):** `step-list` is a vertical list on the left, `step-body` in the centre, `step-help` a column to its right; the footer sits under `step-body`.
- **Narrow (≤ 640 px):** `step-list` folds into one line, "Step 3 of 5 · Team", with a progress bar; `step-help` moves under the step's fields; the footer sticks to the bottom edge with the primary button full width and Back above or beside it. Touching the step line opens the step list as a sheet.

## Interaction constraints

- **A page, never a drawer or a dialog.** A wizard does not live inside a dialog (`rulebook/rules.md § P5`); on a narrow screen it is the page.
- Back keeps everything entered; leaving with entries asks once, in-app and on `beforeunload` (`rulebook/rules.md § P14`). Each step validates on blur and on Next, naming what is missing beside the field.
- The summary step lists every answer with an "Edit" link back to its step, and its primary button names the effect ("Create project"), never "Finish".
- The completion state says what was created or changed, links to it, and offers the next task (`rulebook/rules.md § P31`); it has no Back.
- A step that asks to verify a value shows its source on the same screen (`rulebook/rules.md § P29`).
- Steps are independent: a person may open any visited step from `step-list`; a step not yet reachable is shown disabled with the reason.
- The primary action is always at the right of the footer (`rulebook/rules.md § P17`).

## Sketch

```text
WIDE
+-----------------------------------------------------------+
| shell                                                     |
+-------------+---------------------------------+-----------+
| step-list   | step-body                       | step-help |
|  1 Client ✓ |  Team                           | Who can   |
|  2 Project✓ |  [ Lead designer     v ]        | edit?     |
|  3 Team  <  |  [ Members           v ]        |           |
|  4 Billing  |                                 |           |
|  5 Review   +---------------------------------+           |
|             | footer  [Back] [Cancel]  [ Next ]|           |
+-------------+---------------------------------+-----------+

NARROW
+---------------------------+
| shell                     |
| step-list: Step 3 of 5 ▮▮▮▯▯|
| step-body                 |
|  fields                   |
| step-help                 |
| footer [Back]  [  Next  ] |
+---------------------------+
```

## When not to use

- The steps need each other's content, or the task is done daily: one screen, `object-page` or a dialog with a short form.
- The task has fewer than 3 steps, or at most 16 fields in at most 5 groups: one page, because a wizard runs 3–8 steps and starts above 16 fields or 5 groups (SAP Fiori — wizard usage; AWS Cloudscape — create resource).
- The task creates one simple object with few fields: a dialog or a quick-create (`rulebook/rules.md § P6`).
- The task edits an existing object in sections: `object-page`.
- The task is configuration reached from navigation: `settings`.
