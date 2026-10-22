# Review patches for round test-model-proposal (3 patches across 2 files)

## 10_blueprint/datamodel/model.ts

- [x] **p-k3m9x2-1-model** · model-proposal · note: "The editor needs an estimate field: how many hours the task will take."
  ```diff
  @@ ts:entity/Task/fields @@
  +    estimate: f.decimal({ required: false, proposed: { by: 'mockup-feedback', on: '2026-10-23', source: 'k3m9x2-1' } }),
  ```
- [x] **p-k3m9x2-4-model** · model-proposal · note: "Tasks need comments from the team."
  ```diff
  @@ ts:model/entities @@
  +export const Comment = entity({
  +  glossary: 'comment',
  +  display: 'Comment',
  +  label_field: 'body',
  +  proposed: { by: 'mockup-feedback', on: '2026-10-23', source: 'k3m9x2-4' },
  +  fields: {
  +    body: f.text(),
  +    task_id: f.m2o(() => Task, { on_delete: 'cascade' }),
  +  },
  +})
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
