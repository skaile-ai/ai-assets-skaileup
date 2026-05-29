---
title: "mockup-feedback"
description: "Annotation → patch loop: annotate · triage · patch · apply (+ bidirectional sync via references + devlog)"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`skaileup/mockup-feedback/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/mockup-feedback/DOMAIN.md)
:::


# mockup-feedback

Manages the annotation-to-patch loop for mockups: annotate, triage, patch, and apply changes, with bidirectional sync via references and a devlog. Phase 1 stub — see SKILL_GRAPH.md §1.

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

- See `../SKILL_GRAPH.md` for the catalog-level view.
- See `../../docs/devlog/mockup-design.md` if this domain is a mockup cluster.


## Skills in this domain

- [mockup-feedback-annotate](./mockup-feedback-annotate/) — Injects the annotation overlay into a walkthrough site root so stakeholders can click elements and submit comments. Produces _concept/_feedb
- [mockup-feedback-apply](./mockup-feedback-apply/) — Reads patches/<sid>.json + patches/<sid>.review.md (checklist), applies approved section-anchored diffs to _concept/ files (best-effort), ap
- [mockup-feedback-patch](./mockup-feedback-patch/) — Reads triage/<sid>.json, authors section-anchored diffs for each annotation (LLM for change; templated for add/remove/question), emits patch
- [mockup-feedback-triage](./mockup-feedback-triage/) — Routes each annotation in a session JSON to its target _concept/ file by resolving specRef.screen/feature/journey. Produces triage/<sid>.jso
