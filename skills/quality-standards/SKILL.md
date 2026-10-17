---
name: quality-standards
description: "Use when work is starting against an existing codebase and its conventions have not been written down — scans the code for the patterns it already follows and records them as standards the build skills read. Triggers on 'discover standards', 'what conventions does this codebase use', 'analyse the codebase'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    produces:
      - { id: standards, path: "_concept/02_grounding/standards/" }
---

# quality-standards

Reads an existing codebase and writes down the conventions it already follows, so anything added
to it looks like it belongs there. Discovery only: it applies nothing, has no gates, and works
on a repository with no concept at all.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Scope, scan and write one file per convention** — `tree/02_grounding/standards/README.md`. Ask the path and the domains (`api`, `database`, `ui`, `naming`, `testing`, `architecture`) first.
2. **Write the index** — `tree/02_grounding/standards/index.md`; the build skills match on it.

**Done when** `index.yml` exists, every entry in it resolves to a file that exists, and every `applies_to` value names a skill that is installed.
