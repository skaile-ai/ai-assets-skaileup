---
name: concept-glossary
description: "Use when the product's words are not pinned yet, when another skill has proposed terms in its proposal file, or when a concept has no term. Derives the domain vocabulary and its light ontology from what exists, settles the gaps with the user through the domain-modeling skill, and writes the glossary every journey, feature, screen, model and test then names things from — the words in the project's root `GLOSSARY.md`, the ontology in `_concept/glossary.md`. Triggers on 'pin the vocabulary', 'what do we call this', 'write the glossary', 'we use two words for the same thing'."
version: "0.2.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
    - skill:@mattpocock/domain-modeling#0.1.0
  artifacts:
    requires:
      - { id: brief }
      - { id: grounding-findings }
    produces:
      - { id: glossary, path: "_concept/glossary.md" }
      - { id: proposals, path: "_concept/proposals/<date>-concept-glossary-<scope>.yaml" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
---

# concept-glossary

The owner of `_concept/glossary.md`: the project's ubiquitous language and its light ontology (kinds, is-a, part-of, roles, relations, object axes). It writes no fields, types or paths. The words — definitions and `_Avoid_` lists — live in the project glossary, by default a root `GLOSSARY.md` kept the `domain-modeling` way, and this file holds the ontology (`tree/glossary.md § Where the words live`). Other skills propose terms in their own proposal files (`_concept/proposals/`); this skill promotes or rejects them.

## Route

Read `tree/protocol/running.md` and `tree/protocol/ownership.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve the mode, read and derive** — `tree/glossary.md § Where the words live`, then `tree/glossary.md § Writing it`, steps 1–2. A legacy root `CONTEXT.md` gets its one-time `git mv` offer to `GLOSSARY.md` in the first batch. A missing `brief.md` is not a blocker: the research, findings, `answers.json`, the project glossary and an existing `glossary.md` carry the candidates, and a scoped `concept-reverse` derives what the code holds.
2. **Sort and settle the gaps** — `tree/glossary.md § Writing it`, steps 3–4, as decision batches per `tree/protocol/running.md § How a skill runs`. For the words, call the Skill tool with "domain-modeling": it challenges the terms against the project glossary, sharpens fuzzy language and writes each resolved term there in its own format. Ask the ontology questions in the same batches. An ADR it offers goes into this run's proposal file with `target: docs/adr/` (`tree/docs/adr/README.md § Writing it`).
3. **Write, show and get the yes** — `tree/glossary.md § Writing it`, steps 5–6, in the shape of `tree/glossary.md § Format`: the ontology, the `Words:` line and `## Relations` into `glossary.md`, every entry written by others left as it stands.
4. **Settle what changed** — `tree/glossary.md § Writing it`, step 7, and `tree/proposals/README.md § Writing it`: pending proposal entries targeting the glossary (promote = words into the project glossary in `domain-modeling`'s format plus the ontology entry; reject = status and reason), ids that match no term (`tree/glossary.md § Where the words live`, *Ids*), terms with no entry, a legacy `CONTEXT.md`, an undecided `GLOSSARY-MAP.md`. Do it on every run, so a run that only has proposals to settle starts here.

**Done when** `glossary.md` is on disk, every `## Checks` line of `tree/glossary.md` holds for each part the mode has, no pending proposal entry targets the glossary, and the user has said yes, which `approved:` in the frontmatter records.
