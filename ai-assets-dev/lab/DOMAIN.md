---
name: lab
description: "Skaileup-specific skill-on-skill tooling: compile-bundle (flow↔bundle sync)"
metadata:
  stage: alpha
  type: domain
---

# lab

Skaileup-specific skill-on-skill tooling. The **collection-agnostic** lab skills
(validate · judge · improve · learn · report · compile-validators · archive ·
validate-elements-block, plus the lab agent, contract, and flows) were extracted to
their own repository — [`skaile-ai/ai-assets-skill-development`](https://github.com/skaile-ai/ai-assets-skill-development) —
so they can run against any skill collection. What remains here is tightly coupled
to skaileup's flow/bundle model:

## Skills

- **lab-compile-bundle** (`compile-bundle/`) — Syncs `*.bundle.yaml` with `*.flow.yaml` by adding any missing `skill:` entries. Additive only — never removes user-added entries. Run after modifying a flow. Hardcoded to `skaileup/flows/` and the `@skaile-ai/` publisher. CI guard: `ai-assets-dev/scripts/check-bundles.sh`.

## Cross-references

- `skaileup/flows/` — the flow + bundle YAMLs this skill keeps in sync.
- `docs/devlog/SKILL_GRAPH.md` — collection-level view.
