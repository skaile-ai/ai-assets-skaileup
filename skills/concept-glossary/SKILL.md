---
name: concept-glossary
description: "Use when the product's words are not pinned yet, when another skill has appended proposed terms, or when a concept has no term. Derives the domain vocabulary and its light ontology from what exists, settles the gaps with the user, and writes the glossary every journey, feature, screen, model and test then names things from. Triggers on 'pin the vocabulary', 'what do we call this', 'write the glossary', 'we use two words for the same thing'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: scope }
    produces:
      - { id: glossary, path: "_concept/glossary.md" }
  prerequisites:
    files:
      - { path: "_concept/01_meta/scope.yaml", gate: soft }
      - { path: "_concept/brief.md", gate: soft }
---

# concept-glossary

The owner of `_concept/glossary.md`: the project's ubiquitous language and its light ontology (kinds, is-a, part-of, roles, relations, object axes). It writes no fields, types or paths. Other skills append `proposed` terms; this skill confirms or rejects them.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Read and derive** — `tree/glossary.md § Writing it`, steps 1–2. A missing `brief.md` is not a blocker: the research, findings, `answers.json` and an existing glossary carry the candidates, and a scoped `concept-reverse` fills in what the code holds.
2. **Sort and settle the gaps** — `tree/glossary.md § Writing it`, steps 3–4, as decision batches per `tree/README.md § How a skill runs`.
3. **Write, show and get the yes** — `tree/glossary.md § Writing it`, steps 5–6, in the shape of `tree/glossary.md § Format`.
4. **Promote proposed entries** — `tree/glossary.md § Writing it`, step 7. Run it on every run, so a re-entry that only has proposals to settle starts here.

**Done when** `glossary.md` is on disk, every `## Checks` line of `tree/glossary.md` holds, no `proposed` entry is left pending, and the user has said yes, which `approved:` in the frontmatter records.
