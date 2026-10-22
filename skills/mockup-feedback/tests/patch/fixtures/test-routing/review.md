# Review patches for round test-routing (2 patches across 2 files)

## Needs manual review

- note `p7q1z8-1` — journey change: stories.yaml takes no patch; quoting: "A new user should land on the inbox right after signing in."

## 10_blueprint/datamodel/model.ts

- [x] **p-k3m9x2-1-model** · model-proposal · note: "The editor needs an estimate field."
  ```diff
  @@ ts:entity/Task/fields @@
  +    estimate: f.decimal({ required: false, proposed: { by: 'mockup-feedback', on: '2026-10-23', source: 'k3m9x2-1' } }),
  ```

## 07_screens/inbox.md

- [x] **p-k3m9x2-2-content** · category=change · note: "Put the filter bar above the list, not beside it."
  ```diff
  @@ ## Layout @@
  -- filter-bar: beside the task list
  +- filter-bar: above the task list
  ```
