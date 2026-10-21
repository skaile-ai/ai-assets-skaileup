---
path: _concept/glossary.md
summary: the ubiquitous language and its light ontology — terms, kinds, relations
owner: [concept-glossary]
may_propose: [concept-brief, experience-journeys, architecture-datamodel, architecture-system, spec-feature, experience-interaction, experience-shell, experience-screen, experience-behaviors, concept-reverse, quality-design]
---

# _concept/glossary.md

The project's ubiquitous language and the home of the domain's light ontology: every term with the words it beat under `_Avoid_`, and per term its `kind`, `is-a`, `part-of`, named roles, a one-line `purpose`, an operational principle where the term is an object or concept, and the `## Relations` between terms as triples. For a term of `kind: object` it also holds the four object axes (navigation, lifecycle, origin, operations) the screens and the permission model read. Every journey, feature, screen, entity and test names things from it; without a glossary each coins its own words ("account" in one feature, "user" in a screen, "customer" in code), and without the ontology each skill re-derives what a term *is* and how it connects.

`concept-glossary` owns the file. Where the project keeps its own glossary, this file is the ontology half: the definitions and `_Avoid_` lists sit in the project's file and this one holds what each term *is* and how it connects (`## Where the words live`). A skill that meets a domain word the glossary lacks files a `proposed` entry (`tree/README.md § Ownership`) and carries on; the owner confirms it with the user later. It holds no fields, types, storage, paths or API shapes — those are the data model's (`tree/10_blueprint/datamodel/README.md`) and the code's.

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

In split mode the same terms read as two files. The project glossary, with one confirmed and one proposed term:

````markdown
# Shop

Orders, fulfilment and the people who handle them.

## Language

**Order**:
A confirmed request from a Customer for one or more Items.
_Avoid_: Purchase, transaction, cart

**Backorder**:
An Order line the stock cannot fill yet.
_Avoid_: Waiting line
- status: proposed
- proposed_by: spec-feature
- proposed_on: 2026-10-21
- source: "Backordered lines wait until stock arrives" (spec/features/fulfilment.md)
````

and `_concept/glossary.md`, with no definition and no `_Avoid_` line:

````markdown
---
last_updated: YYYY-MM-DD
approved: YYYY-MM-DD     # only after the user's yes
---

# Glossary — Shop

Words: `CONTEXT.md` (split mode, `tree/glossary.md § Where the words live`).

**Order** (`order`):
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

**Backorder** (`backorder`):
- status: proposed
- proposed_by: spec-feature
- proposed_on: 2026-10-21
- source: "Backordered lines wait until stock arrives" (spec/features/fulfilment.md)
- kind: state

## Relations

- order · placed-by · customer
- order · has-many · order-line
````

- **Id and heading.** A term's id is the kebab-case slug of the term (`Order line` → `order-line`; the rule is `## Where the words live`, *Ids*), written in backticks after the bold term; it is unique in the file and is what the data model's `glossary_id`, the relations and the other skills cite. In split mode it is derived from the bold term of the project glossary and never written there. A renamed term changes its slug: in concept mode it keeps its id until the user decides otherwise, and in split mode the old id no longer matches a term, which step 7 settles.
- **`kind`** is one of `object · role · event · state · value · concept`. An object is a noun the user manages (OOUX); a role is a kind of person or actor; an event is something that happens and is named aloud; a state is a named condition of another term; a value is a typed word with no life of its own (a Currency); a concept is any other project word.
- **Ontology lines** after `_Avoid_`, each omitted when empty: `is-a` (the broader term, by id — shares its permissions and behaviour), `part-of` (the whole the term belongs to), `roles` (the named parts people or terms play toward it), `purpose` (one line, why the product has it), `principle` (the operational principle, at most three steps, for objects and concepts). Targets are term ids.
- **Object axes**, all four on every `kind: object` term and on no other: `navigation: primary | contextual | none` (primary — own navigation entry and index; contextual — reached through a parent or a workspace; none — never navigated to), `lifecycle: independent | owned-by <Term> | link` (owned-by — deleted with its parent; link — joins two objects), `origin: user | system | derived` (system — generated or imported, read-only to users; derived — computed, not stored), `operations:` a subset of `create · read · edit · delete · archive`, the default permitted operations that feature permissions narrow per role.
- **`## Relations`** is a list of triples `subject · predicate · object`, both ends term ids and the predicate a short kebab-case verb phrase (`placed-by`, `has-many`, `confirms`). `is-a` and `part-of` stay on the term and are not repeated here.
- **Proposed entry.** A term a non-owner skill appends carries `status: proposed`, `proposed_by`, `proposed_on` and `source` (an evidence reference or the user's words), plus the `kind` when the proposer knows it; the ontology lines and axes wait for the owner. It adds an entry and never edits a confirmed one. In split mode the term and its marker lines go into the project glossary and only a known `kind` goes here, under the same id (`## Where the words live`, *Proposed terms*).
- **Be opinionated.** When several words mean one concept, pick the best and list the rest under `_Avoid_`; that list is the anti-drift mechanism, so it names every word the sources used for the same concept.
- **Tight definitions.** One or two sentences saying what the thing *is*, not what it does.
- **Only project-specific terms.** A general programming word (timeout, retry, cache, DTO) stays out however heavily the product uses it.
- **One glossary.** When subsystems give one word different meanings, keep one entry per meaning under a cluster heading naming the subsystem, each with its own qualified bold term so the ids differ, and only when a term genuinely collides.

## Where the words live

The words — term, definition, `_Avoid_` — live in one of two places, and one rule resolves which, the same way for every skill. Take the `glossary` value of `_concept/01_meta/scope.yaml` (`tree/01_meta/scope.md`): the key, or while it is absent its latest `proposed` entry (greatest `proposed_on`, the later list position breaking a tie). Then, in this order:

1. **The value is a project-relative path** (no leading `/`, no `..`): **split mode**, with that file as the *project glossary*.
2. **The value is `concept`**: **concept mode**, everything in this file, as `## Format` shows first.
3. **No value and the project root has a `CONTEXT.md`**: split mode with `CONTEXT.md`, and no question asked.
4. **No value, no `CONTEXT.md`, and the root has a `CONTEXT-MAP.md`**: the mode is *undecided*, because a map names several contexts and does not say which one this `_concept/` describes. A proposer files a full entry here, as in concept mode. `concept-glossary` asks which context file this `_concept/` describes, appends a `proposed` entry `{ key: glossary, value: <path> }` to `scope.yaml` (`tree/01_meta/scope.md § Asking a missing key`) and works with the answer at once.
5. **Otherwise**: concept mode.

A path that names no file is a gap, not a mode change: `concept-glossary` asks whether the key is wrong or the file is still to be made, and until the file exists a proposer files its entry here in full, as in concept mode.

**Split mode.** The project glossary holds term, definition and `_Avoid_` in its own format — the `domain-modeling` skill's `CONTEXT.md`: `# <Context>`, one sentence, `## Language`, then per term a `**Term**:` line, a one-to-two-sentence definition line and an `_Avoid_: a, b` line, with optional `###` cluster subheadings, no frontmatter and no ids. This file holds, per term, `kind`, `is-a`, `part-of`, `roles`, `purpose`, `principle`, the four object axes and `## Relations`, and no definition and no `_Avoid_` line. Every confirmed term of the project glossary has an entry here with at least `kind`, so the ontology never lags the words; the terms of both files are the same set. Whatever turns a project to split mode (a `domain-modeling` run creating `CONTEXT.md`, an answered CONTEXT-MAP question, a key set later) leaves any full entry already here to be moved (`## Writing it`, step 7).

**Ownership.** The project glossary stays the project's file. `concept-glossary` writes there only the definitions and `_Avoid_` lines of terms it adds or moves, the promotion of a `proposed` entry (dropping its marker lines) and the rejection of one (removing the entry). Entries written by `domain-modeling` or by hand are kept as they stand, never reordered or reformatted, and it adds no frontmatter, id or ontology line, so the file stays readable by the tools and people that already use it. `approved:` lives in this file's frontmatter and covers both parts.

**Ids.** The id of a term is the kebab-case slug of its bold term: lowercase it, then transliterate `ä→ae`, `ö→oe`, `ü→ue`, `ß→ss`, turn each run of characters outside `[a-z0-9]` into `-`, and trim `-` at both ends (`LÄK-Punkte` → `laek-punkte`, `Überweisung` → `ueberweisung`). Ids are unique across the project glossary: two meanings of one word get distinct bold terms, qualified (`Order (Billing)` → `order-billing`), and `concept-glossary` asks for the qualification (step 7). In split mode the id is derived and never written into the project glossary; an ontology-only entry here whose id matches no term there is a rename or a removal, which `concept-glossary` asks about (step 7).

**Proposed terms.** In split mode a non-owner skill appends the term at the end of the project glossary's `## Language` section or of the matching cluster heading (`##` or `###`), else at the end of the file, as `**Term**:`, a definition line and an `_Avoid_:` line, followed by the four marker lines (`- status: proposed`, `- proposed_by: <skill>`, `- proposed_on: YYYY-MM-DD`, `- source: <evidence or the user's words>`). When it knows the `kind`, it also files an entry with the same id here — ``**Term** (`id`):``, the four marker lines and `- kind: <kind>` — creating this file holding only that entry when it is absent. A term of unknown kind goes into the project glossary alone. In concept mode and in the undecided case the full entry, definition and `_Avoid_` included, goes here.

## Writing it

1. **Resolve the mode, then read what exists.** Resolve the mode first (`## Where the words live`): it decides which file holds each part of what follows. Then read, in any order and none required: `_concept/brief.md` (pitch, audience, problem, hero flow, `## Comparables`), `_concept/02_grounding/research/{domain,competitors,audiences}.md` where research ran — the field's own words are there — `_concept/02_grounding/findings/` where a repository was reverse engineered, whose names each carry a grade, `answers.json` for terms the user already gave, and an existing `glossary.md`. In split mode read the project glossary whole — every term with its definition and `_Avoid_`, including the entries written by `domain-modeling` or by hand, which stay the project's own; in concept mode a project glossary outside `_concept/` (a `CONTEXT.md` the `domain-modeling` skill keeps) is a cited source and nothing more. A glossary with `proposed` entries or a prior `approved:` is a re-entry: read it, then go to step 7 for the entries and to step 4 for any gap.
2. **Derive.** From that material infer the candidate terms (every noun the product keeps, every role of a person, every event or state a user would name aloud) *and* the ontology: each term's kind, is-a, part-of, roles, purpose, the object axes and the relations, each marked with where it came from. In split mode the terms the project glossary already holds are the project's chosen words: derive their ontology and only the candidates it lacks. Where the code holds evidence and no findings exist, run `concept-reverse` scoped to the names and mark what it returns `inferred`. A name taken from code is a candidate, never settled, because code names drift from what people say.
3. **Sort before asking.** Restate the derived result as a draft glossary with its ontology — terms grouped, kinds and relations filled in — and gaps marked, then ask about the gaps (`tree/README.md § How a skill runs`, rule 4); a questionnaire first buries what was already settled.
4. **Interview as decision batches** (`tree/README.md § How a skill runs`, rules 2–5). A long gap list runs over several batches of seven questions at most, placements that change other answers first, so each message stays answerable. Each question carries the recommended term or placement first and a one-line consequence of the answer, such as "is-a Customer → shares Customer's permissions", "owned-by Order → deleted with the Order", "navigation: primary → gets its own index and nav entry". Two words for one concept: ask which wins and list the loser under `_Avoid_`. One word for two concepts: split it into two qualified terms (`Order (Billing)`), each with its own id, and name both. A word from neither the user nor a cited source goes in only on a yes. Depth follows rule 3, not the flow's name: a user who gives a handful of precise terms gets those settled and the rest proposed; a user who wants the whole domain pinned gets the list worked until they stop correcting.
5. **Write the files** with `last_updated` and no `approved:` yet, before asking for approval, so the user reviews the files and not a chat summary. In concept mode `glossary.md` holds the domain sentence, the entries grouped under cluster headings where clusters are natural, and `## Relations`. In split mode write each new term's definition and `_Avoid_` into the project glossary under its clusters, leave every entry written by `domain-modeling` or by hand as it stands — its words change only when the user corrects that term, and then only the lines corrected — and write `glossary.md` with the `Words:` line, one ontology-only entry per term and `## Relations`.
6. **Show it and wait for a yes in words.** In split mode show the project glossary's new and changed entries beside `glossary.md`. Apply corrections, show again, ask again; on the yes write `approved: <date>` in the same write. An edit to either part after that clears the key until the user says yes again.
7. **Settle what changed since the last run.** On every run, list what is pending and settle it seven at a time, each message one decision batch with a recommendation per item (`tree/README.md § How a skill runs`, rule 2); the eighth item opens the next message.
   - **Proposed entries** (name, proposer, source), found in the project glossary in split mode and here in concept mode. A confirmed entry gets its ontology lines and axes through steps 2–4, then drops the marker (`status`, `proposed_by`, `proposed_on`, `source`) in both files; in split mode its definition stays in the project glossary and the ontology completes here. A rejected one is removed from both files and the rejection recorded in `_concept/10_blueprint/decisions.md` with the reason, so it is not proposed again.
   - **A full entry here in split mode** (a definition or `_Avoid_` line), whatever turned the project to split mode: append its definition and `_Avoid_` to the project glossary under a fitting cluster when the term is not there yet; where it is and the definitions differ, the batch asks which wins. The entry here keeps its ontology lines and loses definition and `_Avoid_`; a `proposed` one has its marker lines copied, so both files carry them.
   - **An ontology-only entry here whose id matches no term of the project glossary** (split mode): ask in one batch whether it is a rename or a removal. A rename moves the entry, its relations and every id that cites it to the new id, and names the artifacts that cite the old one (`glossary_id`, features, screens) so the user decides before the edit; a removal drops the entry and its relations.
   - **A term of the project glossary with no entry here** (written by `domain-modeling` or by hand): add the entry with at least `kind`, and the rest through steps 2–4.
   - **Terms whose ids repeat** (`Order` under two clusters of the project glossary): ask which qualified bold term each meaning gets (`Order (Billing)`); the answer corrects those terms, so only their bold lines change, and each gets its own entry here.
   - **An undecided mode** (`CONTEXT-MAP.md`, no `CONTEXT.md`): ask which context file this `_concept/` describes and append the proposed `glossary` entry to `scope.yaml`; the full entries already filed here then fall under the full-entry bullet above.

   A changed confirmed definition ripples into the artifacts that quote it, so name which ones and let the user decide before the edit. Stamp `approved:` again on the yes.

A skill that meets a missing term does not stop: if it is listed under this node's `may_propose` it files a `proposed` entry where `## Where the words live` says — the project glossary in split mode, this file in concept mode, creating the file with only that entry when it is absent — and carries on with it, and the owner settles it in step 7.

The globally installed `domain-modeling` skill is the sharpen-later tool: a standalone grill that challenges the glossary against the code, stress-tests terms with edge cases and captures decisions, run any time the model has drifted. This collection ships no skill for that job; `concept-glossary` keeps the glossary current and `domain-modeling` deepens it.

## Checks

**This file**

- Every term id is unique in the file and is the kebab-case slug of its term; in split mode the ids derived from the project glossary are unique too.
- In concept mode every entry has a definition and an `_Avoid_` line (or says there is none); in split mode no entry has either, and the `Words:` line names the project glossary.
- In split mode every id matches a term of the project glossary.
- Every subject and object in `## Relations` is an existing term id, and every `is-a` and `part-of` target exists.
- Every `kind: object` term carries all four axes with allowed values, and an `owned-by` target exists.
- No entry carries implementation detail: no fields, types, storage, paths or API shapes.
- Every `proposed` entry carries `proposed_by`, `proposed_on` and `source`; a promoted entry carries none of them.
- `approved:` records the user's yes.
- No message of the run asked more than seven questions.

**The project glossary** (split mode)

- Every confirmed term has an entry in `_concept/glossary.md` with at least `kind`.
- Every term `concept-glossary` wrote has a definition and an `_Avoid_` line (or says there is none).
- No entry written by `domain-modeling` or by hand was changed, reordered or reformatted beyond a line the user corrected, and the file gained no frontmatter, id or ontology line.
- Every `proposed` term carries the four marker lines; a promoted term carries none.
