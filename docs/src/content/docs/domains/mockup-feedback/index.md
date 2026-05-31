---
title: "mockup-feedback"
description: "Annotation → patch loop: annotate · triage · patch · apply (+ bidirectional sync via references + devlog)"
sourcePath: "skaileup/mockup-feedback/DOMAIN.md"
sidebar:
  label: "Overview"
  order: 0
---


# mockup-feedback

Turns stakeholder annotations on a live walkthrough site into committed diffs against `_concept/` files. Use this domain after a `mockup-walkthrough-*` output exists and stakeholder review has begun.

## Skills

- **mockup-feedback-annotate** (`annotate/`) — Injects `annotation-overlay.js` into the walkthrough site; writes session JSONs to `_concept/_feedback/sessions/`.
- **mockup-feedback-triage** (`triage/`) — Resolves each annotation's `specRef` to a `_concept/` file path; writes `_concept/_feedback/triage/<sid>.json`. Deterministic Python, no LLM.
- **mockup-feedback-patch** (`patch/`) — Authors section-anchored unified diffs per annotation (LLM for `change` kind, templated for `add`/`remove`/`question`); writes `_concept/_feedback/patches/<sid>.json` + `patches/<sid>.review.md`.
- **mockup-feedback-apply** (`apply/`) — Applies approved diffs from `review.md` to `_concept/` files, appends `_concept/_feedback/devlog.md`, writes `applied/<sid>.json` audit trail, creates one git commit. Deterministic Python, no LLM.

## When to Use

- A `mockup-walkthrough-*` site exists (`_concept/mockup-walkthrough/`) and stakeholders need to annotate it.
- Concept files in `_concept/` need to be updated based on stakeholder feedback without re-running the full walkthrough.
- You need a committed audit trail of which annotations were accepted, skipped, or deferred.

## When NOT to Use

- No walkthrough site exists yet — run `mockup-walkthrough-*` first.
- Feedback is purely verbal or in a doc; skip annotate/triage and author patches manually against `_concept/`.
- You want to regenerate the walkthrough from scratch — use `mockup-walkthrough-*` directly instead.

## Sequence

```
mockup-feedback-annotate   →  _concept/_feedback/sessions/<sid>.json
mockup-feedback-triage     →  _concept/_feedback/triage/<sid>.json
mockup-feedback-patch      →  _concept/_feedback/patches/<sid>.json + <sid>.review.md
  (user edits review.md: tick/untick/hand-edit diffs)
mockup-feedback-apply      →  _concept/**/*.md  +  devlog.md  +  applied/<sid>.json  +  git commit
```

## Cross-references

- `../mockup-walkthrough/` — prerequisite domain; produces the site this domain annotates.
- `../contracts/` — shared frontmatter schema and iron laws all skills read.
- `../SKILL_GRAPH.md` — collection-level dependency graph.


## Skills in this domain

- [mockup-feedback-annotate](./mockup-feedback-annotate/) — Use when a walkthrough site is ready and you need stakeholders to annotate it. Injects the annotation overlay so stakeholders can click elem
- [mockup-feedback-apply](./mockup-feedback-apply/) — Use when patches for a feedback session are reviewed and ready to land. Applies approved section-anchored diffs to _concept/ files, appends 
- [mockup-feedback-patch](./mockup-feedback-patch/) — Use when a triage file exists for a feedback session and you need to author diffs for each annotation. Produces patches/<sid>.json + patches
- [mockup-feedback-triage](./mockup-feedback-triage/) — Use when a feedback session JSON exists and annotations need to be routed to their target concept files. Resolves specRef.screen/feature/jou
