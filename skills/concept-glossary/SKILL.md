---
name: concept-glossary
description: "Use when the brief is approved and the product's words are not pinned yet, or when a later step meets a concept that has no term. Grills the user on the domain vocabulary and writes the glossary every journey, feature, screen, model and test then names things from. Triggers on 'pin the vocabulary', 'what do we call this', 'write the glossary', 'we use two words for the same thing'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: scope }
      - { id: brief }
    produces:
      - { id: glossary, path: "_concept/glossary.md" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: hard }
      - { path: "_concept/01_meta/scope.yaml", gate: soft }
---

# concept-glossary

The one writer of `_concept/glossary.md`: the project's ubiquitous language. It writes words and nothing else — no fields, no types, no paths — and re-enters whenever a later step meets a concept with no term.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Pin the vocabulary** — `tree/glossary.md`. Its `## Writing it` steps 1–5 are the first run; step 6 is the re-entry when a hand-back names a missing term.

**Done when** `glossary.md` is on disk, every entry has a definition and an `_Avoid_` line (or says there is none), no entry carries implementation detail, and the user has said yes, which `approved:` in the frontmatter records.
