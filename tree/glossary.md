---
path: _concept/glossary.md
summary: the ubiquitous language and its light ontology — terms, kinds, relations
owner: [concept-glossary]
may_propose: [concept-brief, experience-journeys, architecture-datamodel, architecture-system, spec-feature, experience-interaction, experience-shell, experience-screen, experience-behaviors, concept-reverse, quality-design]
---

# _concept/glossary.md

The project's ubiquitous language and the home of the domain's light ontology: every term with the words it beat under `_Avoid_`, and per term its `kind`, `is-a`, `part-of`, named roles, a one-line `purpose`, an operational principle where the term is an object or concept, and the `## Relations` between terms as triples. For a term of `kind: object` it also holds the four object axes (navigation, lifecycle, origin, operations) the screens and the permission model read. Every journey, feature, screen, entity and test names things from it; without a glossary each coins its own words ("account" in one feature, "user" in a screen, "customer" in code), and without the ontology each skill re-derives what a term *is* and how it connects.

`concept-glossary` owns the file. A skill that meets a domain word the glossary lacks appends a `proposed` entry (`tree/README.md § Ownership`) and carries on; the owner confirms it with the user later. It holds no fields, types, storage, paths or API shapes — those are the data model's (`tree/10_blueprint/datamodel/README.md`) and the code's.

## Format

````markdown
---
last_updated: YYYY-MM-DD
approved: YYYY-MM-DD     # only after the user's yes
---

# Glossary — <App Name>

<One or two sentences: what this product's domain is.>

## <Optional cluster heading, e.g. Ordering>

**Order** (`order`):
A confirmed request from a Customer for one or more Items.
_Avoid_: Purchase, transaction, cart
- kind: object
- is-a: —
- part-of: —
- roles: placed by a Customer; fulfilled by a Clerk
- purpose: records what a Customer committed to buy, so it can be paid, packed and shipped.
- principle: a Customer places the Order → a Clerk confirms it → the Order is fulfilled or cancelled.
- navigation: primary
- lifecycle: independent
- origin: user
- operations: create · read · edit · archive

**Order line** (`order-line`):
One Item at one quantity within an Order.
_Avoid_: Position, row
- kind: object
- part-of: order
- purpose: lets one Order carry several Items, each priced on its own.
- principle: a Customer adds an Item → the line takes its price → the line is changed or removed until the Order is confirmed.
- navigation: contextual
- lifecycle: owned-by Order
- origin: user
- operations: create · read · edit · delete

**Clerk** (`clerk`):
A staff member who confirms and packs Orders.
_Avoid_: Agent, operator
- kind: role
- is-a: user
- purpose: carries Orders from confirmed to fulfilled.

**Backorder** (`backorder`):
An Order line the stock cannot fill yet.
- status: proposed
- proposed_by: spec-feature
- proposed_on: 2026-10-21
- source: "Backordered lines wait until stock arrives" (spec/features/fulfilment.md)
- kind: state

## Relations

- order · placed-by · customer
- order · has-many · order-line
- clerk · confirms · order
````

- **Id and heading.** A term's id is the kebab-case slug of the term (`Order line` → `order-line`), written in backticks after the bold term; it is unique in the file and is what the data model's `glossary_id`, the relations and the other skills cite. A renamed term keeps its id until the user decides otherwise.
- **`kind`** is one of `object · role · event · state · value · concept`. An object is a noun the user manages (OOUX); a role is a kind of person or actor; an event is something that happens and is named aloud; a state is a named condition of another term; a value is a typed word with no life of its own (a Currency); a concept is any other project word.
- **Ontology lines** after `_Avoid_`, each omitted when empty: `is-a` (the broader term, by id — shares its permissions and behaviour), `part-of` (the whole the term belongs to), `roles` (the named parts people or terms play toward it), `purpose` (one line, why the product has it), `principle` (the operational principle, at most three steps, for objects and concepts). Targets are term ids.
- **Object axes**, all four on every `kind: object` term and on no other: `navigation: primary | contextual | none` (primary — own navigation entry and index; contextual — reached through a parent or a workspace; none — never navigated to), `lifecycle: independent | owned-by <Term> | link` (owned-by — deleted with its parent; link — joins two objects), `origin: user | system | derived` (system — generated or imported, read-only to users; derived — computed, not stored), `operations:` a subset of `create · read · edit · delete · archive`, the default permitted operations that feature permissions narrow per role.
- **`## Relations`** is a list of triples `subject · predicate · object`, both ends term ids and the predicate a short kebab-case verb phrase (`placed-by`, `has-many`, `confirms`). `is-a` and `part-of` stay on the term and are not repeated here.
- **Proposed entry.** A term a non-owner skill appends carries `status: proposed`, `proposed_by`, `proposed_on` and `source` (an evidence reference or the user's words), plus the `kind` when the proposer knows it; the ontology lines and axes wait for the owner. It adds an entry and never edits a confirmed one.
- **Be opinionated.** When several words mean one concept, pick the best and list the rest under `_Avoid_`; that list is the anti-drift mechanism, so it names every word the sources used for the same concept.
- **Tight definitions.** One or two sentences saying what the thing *is*, not what it does.
- **Only project-specific terms.** A general programming word (timeout, retry, cache, DTO) stays out however heavily the product uses it.
- **One glossary.** When subsystems give one word different meanings, keep one entry per meaning under a cluster heading naming the subsystem, and only when a term genuinely collides.

## Writing it

1. **Read what exists**, in any order and none required: `_concept/brief.md` (pitch, audience, problem, hero flow, `## Comparables`), `_concept/02_grounding/research/{domain,competitors,audiences}.md` where research ran — the field's own words are there — `_concept/02_grounding/findings/` where a repository was reverse engineered, whose names each carry a grade, `answers.json` for terms the user already gave, a project glossary outside `_concept/` (a `CONTEXT.md` the `domain-modeling` skill keeps) as a cited source that stays the project's own file, and an existing `glossary.md`. A glossary with `proposed` entries or a prior `approved:` is a re-entry: read it, then go to step 7 for the entries and to step 4 for any gap.
2. **Derive.** From that material infer the candidate terms (every noun the product keeps, every role of a person, every event or state a user would name aloud) *and* the ontology: each term's kind, is-a, part-of, roles, purpose, the object axes and the relations, each marked with where it came from. Where the code holds evidence and no findings exist, run `concept-reverse` scoped to the names and mark what it returns `inferred`. A name taken from code is a candidate, never settled, because code names drift from what people say.
3. **Sort before asking.** Restate the derived result as a draft glossary with its ontology — terms grouped, kinds and relations filled in — and gaps marked, then ask about the gaps (`tree/README.md § How a skill runs`, rule 4); a questionnaire first buries what was already settled.
4. **Interview as decision batches** (`tree/README.md § How a skill runs`, rules 2–5). Each question carries the recommended term or placement first and a one-line consequence of the answer, such as "is-a Customer → shares Customer's permissions", "owned-by Order → deleted with the Order", "navigation: primary → gets its own index and nav entry". Two words for one concept: ask which wins and list the loser under `_Avoid_`. One word for two concepts: split it and name both. A word from neither the user nor a cited source goes in only on a yes. Depth follows rule 3, not the flow's name: a user who gives a handful of precise terms gets those settled and the rest proposed; a user who wants the whole domain pinned gets the list worked until they stop correcting.
5. **Write `glossary.md`** with `last_updated` and no `approved:` yet, the domain sentence, the entries grouped under cluster headings where clusters are natural, and `## Relations`. Write it before asking for approval, so the user reviews the file and not a chat summary.
6. **Show it and wait for a yes in words.** Apply corrections, show again, ask again; on the yes write `approved: <date>` in the same write. An edit after that clears the key until the user says yes again.
7. **Promote proposed entries.** On every run, list the pending `status: proposed` entries (name, proposer, source) and settle them in confirm-or-reject decision batches with a recommendation each (`tree/README.md § How a skill runs`, rule 2 — more than seven pending entries take a second batch). A confirmed entry gets its ontology lines and axes through steps 2–4, then drops the marker (`status`, `proposed_by`, `proposed_on`, `source`); a rejected one is removed and the rejection recorded in `_concept/10_blueprint/decisions.md` with the reason, so it is not proposed again. A changed confirmed definition ripples into the artifacts that quote it, so name which ones and let the user decide before the edit. Stamp `approved:` again on the yes.

A skill that meets a missing term does not stop: if it is listed under this node's `may_propose` it appends a `proposed` entry to `_concept/glossary.md` — creating the file with only that entry when it is absent, even where the project keeps a `CONTEXT.md` — and carries on with it, and the owner settles it in step 7.

The globally installed `domain-modeling` skill is the sharpen-later tool: a standalone grill that challenges the glossary against the code, stress-tests terms with edge cases and captures decisions, run any time the model has drifted. This collection ships no skill for that job; `concept-glossary` keeps the glossary current and `domain-modeling` deepens it.

## Checks

- Every term id is unique in the file and is the kebab-case slug of its term.
- Every entry has a definition and an `_Avoid_` line (or says there is none).
- Every subject and object in `## Relations` is an existing term id, and every `is-a` and `part-of` target exists.
- Every `kind: object` term carries all four axes with allowed values, and an `owned-by` target exists.
- No entry carries implementation detail: no fields, types, storage, paths or API shapes.
- Every `proposed` entry carries `proposed_by`, `proposed_on` and `source`; a promoted entry carries none of them.
- `approved:` records the user's yes.
