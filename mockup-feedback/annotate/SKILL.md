---
name: mockup-feedback-annotate
description: "Injects the annotation overlay into a walkthrough site root so stakeholders can click elements and submit comments. Produces _concept/_feedback/sessions/ for annotation storage. First skill in the mockup-feedback cluster."
metadata:
  version: "0.1.0"
  tags:
    - mockup-feedback
    - annotation
    - overlay
    - data-spec
    - walkthrough
  stage: alpha
  prerequisites:
    files:
      - path: "_concept/walkthrough-mockup"
        gate: hard
        description: "At least one walkthrough-mockup-* output must exist (manifest.json + HTML files)"
        min_entries: 1
    reads:
      - path: "_concept/walkthrough-mockup/static-html/manifest.json"
        description: "Validates data-spec-element IDs and identifies provisional ones"
    produces:
      - path: "_concept/walkthrough-mockup/static-html/annotation-overlay.js"
        description: "The overlay bundle copied from skill/overlay/"
      - path: "_concept/_feedback/sessions/"
        description: "Session JSON directory (gitignored); created if absent"
      - path: "_concept/_feedback/index.json"
        description: "Session index (gitignored); created if absent"
---

# mockup-feedback-annotate

## BODY_PLACEHOLDER

(Skill body authored in Task 4.)
