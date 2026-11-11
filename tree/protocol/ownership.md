# Ownership

## Ownership

Read anything, in any order; write only the artifacts you own, through the owner node's contract. `02_grounding/` is readable by every skill. An artifact another skill owns takes only `proposed` entries, and only from a skill listed under that node's `may_propose`. A project file outside `_concept/` other than `APP-DESIGN.md` (a `CONTEXT.md`, docs, ADRs) is a source to read and cite, and stays the project's own: a term or decision it lacks is proposed into the `_concept/` artifact that owns that kind of entry. The one exception is the project glossary, the file that holds the words when the project keeps its own: `concept-glossary` writes there only the definitions of terms it adds or moves, the promotion of a proposed entry (dropping its marker lines) and the rejection of one (removing it), keeps every entry written by `domain-modeling` or by hand as it stands, and a proposed term is filed there too (`tree/glossary.md § Where the words live`). `06_behaviors/` and `10_blueprint/architecture.md` are optional; a reader checks for existence before reading.

A node's frontmatter carries two keys, both required:

```yaml
owner: [concept-glossary]   # skills whose `produces` resolve here; [] when nothing generates it
may_propose: []             # skills that may append `proposed` entries through this node; disjoint from owner
```

A directory node lists the owners of the parts it covers. `may_propose` names skills of this collection and repeats no owner.

**Proposed entry.** An entry a non-owner skill appends to the owner's artifact, marked `status: proposed`, with `proposed_by: <skill>`, `proposed_on: YYYY-MM-DD` and its source (an evidence reference or the user's words). It adds and never edits a confirmed entry. When the owner's artifact does not exist yet, the proposer creates it holding only its proposed entries and no `approved:` key, so the owner's first write fills it instead of finding a gap. The owner reviews each entry with the user and promotes it by dropping the marker, or rejects it and records the rejection in `_concept/10_blueprint/decisions.md`. Each node's `## Format` holds the per-artifact shape, one shape per node.
