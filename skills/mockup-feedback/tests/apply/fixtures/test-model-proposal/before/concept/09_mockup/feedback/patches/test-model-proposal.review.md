# Review patches for round test-model-proposal (3 proposals)

## Proposals

- [x] **p-k3m9x2-1-model** · proposal · note: "The editor needs an estimate field: how many hours the task will take."
  ```yaml
  # proposal → _concept/10_blueprint/datamodel/model.yaml @ entities.Task.fields.estimate
  { type: decimal, required: false }
  ```
- [x] **p-k3m9x2-4-model** · proposal · note: "Tasks need comments from the team."
  ```yaml
  # proposal → _concept/10_blueprint/datamodel/model.yaml @ entities.Comment
  glossary: comment
  display: Comment
  label_field: body
  fields:
    body: text
    task_id: { type: m2o, to: Task, on_delete: cascade }
  ```
- [x] **p-k3m9x2-4-glossary** · proposal · note: "Tasks need comments from the team."
  ```markdown
  <!-- proposal → _concept/glossary.md @ term:Comment -->
  **Comment** (`comment`):
  - kind: object
  ```
