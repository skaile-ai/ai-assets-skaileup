# Review patches for round test-routing (2 patches across 2 files)

## Needs manual review

- note `p7q1z8-1` — journey change: stories.yaml takes no patch; quoting: "A new user should land on the inbox right after signing in."

## Proposals

- [x] **p-k3m9x2-1-model** · proposal · note: "The editor needs an estimate field."
  ```yaml
  # proposal → _concept/10_blueprint/datamodel/model.yaml @ entities.Task.fields.estimate
  { type: decimal, required: false }
  ```

## 07_screens/inbox.md

- [x] **p-k3m9x2-2-content** · category=change · note: "Put the filter bar above the list, not beside it."
  ```diff
  @@ ## Layout @@
  -- filter-bar: beside the task list
  +- filter-bar: above the task list
  ```
