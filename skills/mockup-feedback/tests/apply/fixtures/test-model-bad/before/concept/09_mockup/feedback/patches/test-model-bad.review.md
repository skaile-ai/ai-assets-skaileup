# Review patches for round test-model-bad (1 patch)

## 10_blueprint/datamodel/model.yaml

- [x] **p-k3m9x2-1-model** · model-proposal · note: "The editor needs an estimate field."
  ```diff
  @@ yaml:entity/Task/fields @@
  +      estimate: { type: hours, required: false, proposed: { by: mockup-feedback, on: 2026-10-23, source: k3m9x2-1 } }
  ```
