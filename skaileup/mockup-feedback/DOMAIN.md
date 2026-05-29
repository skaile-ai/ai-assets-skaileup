---
name: mockup-feedback
description: "Annotation → patch loop: annotate · triage · patch · apply (+ bidirectional sync via references + devlog)"
metadata:
  stage: alpha
  type: domain
---

# mockup-feedback

Manages the annotation-to-patch loop for mockups: annotate, triage, patch, and apply changes, with bidirectional sync via references and a devlog.

## Skills

- [`mockup-feedback-annotate`](annotate/SKILL.md) — Inject annotation overlay into a walkthrough site
- [`mockup-feedback-triage`](triage/SKILL.md) — Route annotations to _concept/ files by resolving specRef
- [`mockup-feedback-patch`](patch/SKILL.md) — Author section-anchored diffs for each annotation (LLM-driven)
- [`mockup-feedback-apply`](apply/SKILL.md) — Apply approved diffs, append devlog, commit

## Usage sequence

```
mockup-feedback-annotate   → injects overlay into walkthrough; user downloads sessions/*.json
mockup-feedback-triage     → resolves specRef → _concept/ paths; groups by file
mockup-feedback-patch      → authors diffs; emits patches/*.json + *.review.md
  (user reviews and edits review.md)
mockup-feedback-apply      → applies diffs, appends devlog, one git commit
```

## Cross-references

- See `../../../docs/devlog/SKILL_GRAPH.md` for the catalog-level view.
- See `../REFACTOR_MOCKUP.md` if this domain is a mockup cluster.
