---
path: _concept/02_grounding/standards/index.yml
summary: fast matching of conventions by applies_to and keywords
owner: [quality-standards]
may_propose: []
---

# _concept/02_grounding/standards/index.yml

The file readers actually open. `build-plan` and `build-implement` match on `applies_to` and
`keywords` and load only the standards that hit, so a convention missing from the index exists
and is never applied.

## Format

One entry per convention file carrying `path` (relative to `standards/`), `domain`, `keywords`
and `applies_to`, copied from that file's frontmatter:

```yaml
standards:
  - path: api/route-naming.md
    domain: api
    keywords: [routing, rest, endpoints]
    applies_to: [build-implement, build-plan]
```

## Writing it

Write the index after the convention files, one entry per file; rewrite it whole whenever a
convention is added or removed.

## Checks

The file exists, every entry's `path` resolves to a file that exists, and every `applies_to`
value names an installed skill.
