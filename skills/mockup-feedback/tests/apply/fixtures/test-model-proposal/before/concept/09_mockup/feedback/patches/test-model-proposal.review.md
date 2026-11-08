# Review patches for round test-model-proposal (3 patches across 2 files)

## 10_blueprint/datamodel/model.yaml

- [x] **p-k3m9x2-1-model** · model-proposal · note: "The editor needs an estimate field: how many hours the task will take."
  ```diff
  @@ yaml:entity/Task/fields @@
  +      estimate: { type: decimal, required: false, proposed: { by: mockup-feedback, on: 2026-10-23, source: k3m9x2-1 } }
  ```
- [x] **p-k3m9x2-4-model** · model-proposal · note: "Tasks need comments from the team."
  ```diff
  @@ yaml:model/entities @@
  +  Comment:
  +    glossary: comment
  +    display: Comment
  +    label_field: body
  +    proposed: { by: mockup-feedback, on: 2026-10-23, source: k3m9x2-4 }
  +    fields:
  +      body: text
  +      task_id: { type: m2o, to: Task, on_delete: cascade }
  ```

## glossary.md

- [x] **p-k3m9x2-4-glossary** · glossary-proposal · note: "Tasks need comments from the team."
  ```diff
  @@ before:## Relations @@
  +**Comment** (`comment`):
  +- status: proposed
  +- proposed_by: mockup-feedback
  +- proposed_on: 2026-10-23
  +- source: "Tasks need comments from the team." (k3m9x2-4)
  +- kind: object
  +
  ```
