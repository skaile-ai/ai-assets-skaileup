# 0021 — The glossary carries the light ontology

**Status:** accepted

Supersedes [ADR 0014](0014-the-glossary-is-a-root-file.md)'s reading of the glossary as words
and nothing else. The root placement, the file name and the rest of ADR 0014 stand.

## Context

The glossary was "words and nothing else": no relations, no fields, no types. The datamodel
holds entities and relations but is storage. The relations that make a vocabulary useful —
this is a kind of that, this is part of that, this plays that role for that — had no home
(U11; both critics recommended the enriched glossary).

The object classification suffered the same way (U10). `core`, `child` and `system` mixed three
axes: navigation importance, lifecycle ownership and origin. And the classification lived in
`APP-DESIGN.md § Objects`, written late, so skills that needed to know an object's role early
(shell destinations, datamodel, screens) could not read it.

## Decision

**The glossary carries the light ontology.** Per term:

- `kind`, `is-a`, `part-of`, named roles, and a one-line `purpose`;
- for behavioural terms, an operational principle of at most three steps;
- a `## Relations` section of triples: subject · predicate · object.

**Object terms carry three axes, separately:** navigation role (how prominently the object
appears), lifecycle ownership (whether it lives and dies with a parent) and origin (user-made,
imported or system-made). Permitted operations stay in the app-design object map; the glossary
says what the thing is, not what a screen allows.

**The datamodel cites glossary ids and owns storage only.** `model.json` is authored,
`model.dbml` is generated. A feature that coins a name splits one concept into two, so ids
come from the glossary.

**`concept-glossary` infers the ontology** from the brief, journeys and code evidence, marks
inferred relations, and interviews in batches with a consequence line each
([ADR 0019](0019-scoped-fact-resolution.md)).

**One owner, many proposers.** `concept-glossary` stays the owner. Every authoring skill may
append a `proposed` term or relation ([ADR 0022](0022-shared-artifact-contracts-and-proposed-entries.md)),
which replaces ADR 0014's "read it, never append to it" without bringing back three writers.

## Consequences

- `glossary` stops being a plain term list; its node gains the ontology format and the
  proposed-entry protocol.
- The object class (core / supporting / child / junction / system) leaves
  `APP-DESIGN.md § Objects`; the shell and the datamodel read the glossary instead.
- A concept with no term no longer waits for `concept-glossary` to run: the skill that meets it
  proposes the term.
