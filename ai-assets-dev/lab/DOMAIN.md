---
name: lab
description: "Skaileup-specific skill-on-skill tooling (currently none — all lab skills are collection-agnostic and live in ai-assets-skill-development)"
metadata:
  stage: alpha
  type: domain
---

# lab

Home for **skaileup-specific** skill-on-skill tooling. The
**collection-agnostic** lab skills (validate · judge · improve · learn · report ·
compile-validators · archive · validate-elements-block, plus the lab agent,
contract, and flows) were extracted to their own repository —
[`skaile-ai/ai-assets-skill-development`](https://github.com/skaile-ai/ai-assets-skill-development) —
so they can run against any skill collection.

## Skills

_None at present._ The former **lab-compile-bundle** skill (which synced
`*.bundle.yaml` against `*.flow.yaml`) was removed when bundles were folded into
the flows: each flow now carries its own `requires:` install manifest, so there
is nothing to compile. Manifest correctness is enforced by
`skaileup/flows/_meta/verify_flows.py`, not a lab skill.

## Cross-references

- `skaileup/flows/` — self-contained flow YAMLs (graph + `requires:` manifest).
- `skaileup/flows/_meta/verify_flows.py` — validates each flow's manifest.
- `docs/devlog/SKILL_GRAPH.md` — collection-level view.
