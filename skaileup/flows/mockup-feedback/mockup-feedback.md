---
title: "mockup-feedback"
description: "Shared mockup-feedback cluster: annotate → triage → patch → apply (all optional)."
order: 15
---

The **mockup-feedback** flow is the shared feedback loop over mockups:
annotate → triage → patch → apply, every step optional. It was byte-identical
in `appbuilder-standard` and `appbuilder-complex`; both now delegate to it via
a **sub-flow node** after the mockup renderers. Standalone-runnable
(`skaile run flow:mockup-feedback`) against an existing
`_concept/mockup-walkthrough/` or `_concept/mockup-component/` tree.

## Pipeline

```
annotate? → triage? → patch? → apply?
```

## Install manifest

`mockup-feedback.flow.yaml` carries a top-level `requires:` listing
`shared-contracts` and the four `mockup-feedback-*` skills.
