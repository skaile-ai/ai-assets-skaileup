---
path: [_concept/02_grounding/standards/, _concept/02_grounding/standards/<domain>/]
summary: conventions discovered in an existing codebase, one file per convention
writers: [quality-standards]
---

# _concept/02_grounding/standards/

The conventions an existing codebase already follows, written down so anything added to it
looks like it belongs there. `quality-standards` discovers and records them and applies nothing;
the skills that write code read `index.yml` themselves when they need it
(`tree/02_grounding/standards/index.md`). It reads code, not `_concept/`, so it has no gates, runs
at any point, and works on a repository with no concept at all.

## Format

One file per convention at `02_grounding/standards/<domain>/<convention>.md`, where `<domain>` is
one of `api`, `database`, `ui`, `naming`, `testing`, `architecture`:

```yaml
---
domain: api
keywords: [routing, rest, endpoints]     # what a reader greps for
applies_to: [build-implement, build-plan]  # skill names, exactly as they install
last_updated: YYYY-MM-DD
---
```

The body is the rule in a sentence or two, then one example lifted from this codebase that
follows it and one that would not — an invented example is how a standards file ends up
describing a codebase nobody has. Keep the body short enough to read at the point of use.

`applies_to` names skills by their `name:`, a skill's whole identity; a value that resolves to
no installed skill matches nothing and narrows the standard to zero readers.

## Writing it

1. **Agree the scope.** Ask for the path to analyse — in a reverse-engineering run, the
   repository already open — and which domains to cover. Narrow beats complete: a domain
   nothing downstream writes into produces standards nothing reads.
2. **Scan broadly before concluding.** A convention is a pattern with several independent
   instances; one occurrence is a choice made on one afternoon, and recording it binds every
   future author to an accident. Where a pattern has two competing forms, record the dominant
   one and name the exception rather than picking a winner.
3. **Write one file per convention** in the format above.
4. **Write the index** per `tree/02_grounding/standards/index.md`.
5. **Report** the count per domain and the conventions worth knowing before anyone writes code —
   the ones that will surprise someone arriving from a different project.

## Checks

Every convention file has the frontmatter above and an example from this codebase; the index
lists every file.
