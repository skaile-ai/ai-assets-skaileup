---
name: concept-glossary
description: "Use when the product's words are not pinned yet, when another skill has appended proposed terms, or when a concept has no term. Derives the domain vocabulary and its light ontology from what exists, settles the gaps with the user, and writes the glossary every journey, feature, screen, model and test then names things from — in `_concept/glossary.md`, with the definitions in the project's own `CONTEXT.md` when it keeps one. Triggers on 'pin the vocabulary', 'what do we call this', 'write the glossary', 'we use two words for the same thing'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: grounding-findings }
    produces:
      - { id: glossary, path: "_concept/glossary.md" }
      - { id: decisions, path: "_concept/10_blueprint/decisions.md" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
---

# concept-glossary

The owner of `_concept/glossary.md`: the project's ubiquitous language and its light ontology (kinds, is-a, part-of, roles, relations, object axes). It writes no fields, types or paths. Where the project keeps its own glossary (a root `CONTEXT.md`), the definitions and `_Avoid_` lists go there and this file holds the ontology (`tree/glossary.md § Where the words live`). Other skills append `proposed` terms; this skill confirms them or rejects them into `_concept/10_blueprint/decisions.md`.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve the mode, read and derive** — `tree/glossary.md § Where the words live`, then `tree/glossary.md § Writing it`, steps 1–2. A missing `brief.md` is not a blocker: the research, findings, `answers.json`, the project glossary and an existing `glossary.md` carry the candidates, and a scoped `concept-reverse` derives what the code holds.
2. **Sort and settle the gaps** — `tree/glossary.md § Writing it`, steps 3–4, as decision batches per `tree/README.md § How a skill runs`.
3. **Write, show and get the yes** — `tree/glossary.md § Writing it`, steps 5–6, in the shape of `tree/glossary.md § Format`; in split mode that is definitions into the project glossary, ontology into `glossary.md`, and every entry written by others left as it stands.
4. **Settle what changed** — `tree/glossary.md § Writing it`, step 7: pending proposals, ids that match no term, terms with no entry, an undecided `CONTEXT-MAP.md`. Do it on every run, so a run that only has proposals to settle starts here.

**Done when** `glossary.md` is on disk, every `## Checks` line of `tree/glossary.md` holds for each part the mode has, no `proposed` entry is left pending, and the user has said yes, which `approved:` in the frontmatter records.
