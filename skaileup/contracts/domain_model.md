# Domain Model — Glossary + Decision Records

The project's **domain model** is its shared language plus the record of why it is
shaped the way it is. Two durable artifacts carry it, split by lifecycle:

| Artifact | Path | Role | Lifecycle |
|---|---|---|---|
| **Glossary** | `_concept/blueprint/glossary.md` | ubiquitous language — canonical term → definition | living; entries are **updated in place** |
| **Decision records (ADRs)** | `_concept/decisions.md` (design-time) · `_implementation/decisions.md` (build-time) | why a hard-to-reverse choice was made | **append-only**; entries are never edited, only superseded |

Both are built **lazily and inline** — as a byproduct of the work, never authored
up front. A term is written the moment it is pinned during a grill; a decision is
recorded the moment it is made during planning or implementation. No skill produces
these in a dedicated "write the glossary" pass — they accrete.

**Read by ALL skills.** Like `_grounding/` and `_standards/`, the glossary is always
available as input. Every skill that names a domain concept — feature specs, screen
specs, datamodel entities, plan tasks, test names, code — uses the glossary's term,
not a synonym. This is what keeps a large app's vocabulary from drifting ("account"
in one feature, "user" in a screen, "customer" in code).

---

## Glossary format — `_concept/blueprint/glossary.md`

The glossary is a **glossary and nothing else**: term → definition. It contains
**zero implementation detail** — no schemas, no file paths, no API shapes. Those
live in `datamodel/`, `architecture.md`, and the code. If you are tempted to write
*how* something works, it does not belong here.

```md
# Glossary — <App Name>

<One or two sentences: what this product's domain is.>

## <Optional cluster heading, e.g. Ordering>

**Order**:
A confirmed request from a Customer for one or more Items.
_Avoid_: Purchase, transaction, cart

**Invoice**:
A request for payment sent to a Customer after an Order ships.
_Avoid_: Bill, receipt

**Customer**:
A person or organization that places Orders.
_Avoid_: Client, buyer, account, user
```

**Rules:**
- **Be opinionated.** When several words mean one concept, pick the best, list the
  rest under `_Avoid_`. The `_Avoid_` list is the anti-drift mechanism.
- **Tight definitions.** One or two sentences. Define what it **is**, not what it does.
- **Only project-specific terms.** General programming concepts (timeout, retry,
  cache, DTO) never belong, even when the project uses them heavily. Before adding a
  term ask: *is this concept unique to this domain, or general?* Only the former.
- **Group under subheadings** when natural clusters emerge; a flat list is fine when
  all terms belong to one cohesive area.

### Single vs. multi-context

Most projects have **one** glossary at `_concept/blueprint/glossary.md`.

When a project spans distinct subsystems with their own languages (e.g. a "billing"
subsystem and a "fulfillment" subsystem where the same word means different things),
promote to a **context map**: `_concept/blueprint/glossary/` holds one file per
subsystem plus a `map.md` listing them and their relationships. Do this only when a
term genuinely collides across subsystems — not preemptively.

---

## Decision record (ADR) format

ADRs live beside the blueprint (`_concept/blueprint/decisions.md`, design-time) and
the implementation ledger (`_implementation/decisions.md`, build-time). Each entry is
tiny — the value is recording **that** a decision was made and **why**, not filling
out sections.

```md
## <ISO-8601 date> — <short title of the decision>

<1–3 sentences: the context, what was decided, and why. That's it.>
```

**Optional lines** — include only when they add real value (most entries won't):
- **Status**: `accepted | deprecated | superseded by <date/title>` — when a decision
  gets revisited, mark the old one rather than deleting it.
- **Options considered** — only when the rejected alternatives are worth remembering.
- **Consequences** — only when a non-obvious downstream effect must be flagged.

Append-only: never edit a landed entry. To change your mind, add a new entry that
supersedes the old one and mark the old one's Status.

### The ADR gate — record sparingly

Write an ADR only when **all three** are true:

1. **Hard to reverse** — changing your mind later costs meaningfully.
2. **Surprising without context** — a future reader will look at the result and
   wonder "why on earth did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and one was
   chosen for specific reasons.

If any one is missing, **skip it**. Easy to reverse → you'll just reverse it. Not
surprising → nobody will wonder. No real alternative → nothing to record beyond "we
did the obvious thing." This gate exists because eager decision-logging buries the
few decisions that matter under dozens that don't.

**Qualifies:** architectural shape; integration patterns between subsystems;
technology choices carrying lock-in (DB, auth, message bus); boundary/ownership
decisions ("Customer data is owned by X; others reference by id"); deliberate
deviations from the obvious path ("manual SQL, not an ORM, because…"); constraints
invisible in the code (compliance, latency contracts); non-obvious rejected
alternatives.

**Does not qualify:** routine library picks, obvious choices, anything a reader would
expect by default, transient scratch decisions (those belong in the slice `align.md`).

---

## The discipline — build the model as you work

The glossary and ADRs are grown by the **grill/align skills** (during planning) and
the **slice/build skills** (during implementation), not by a separate documentation
step. When a skill runs a grill and:

- **a term gets pinned or a fuzzy word gets sharpened** → write/update the glossary
  entry then and there. "You keep saying 'account' — you mean the Customer or the
  login User? They're different." → resolve → glossary.
- **a decision passes the 3-test gate** → append an ADR then and there.

The dedicated **`skaileup-domain-model`** skill is the *sharpen-later* tool: a standalone
grill (the skaileup analog of "grill-with-docs") that challenges the existing
glossary against the code, stress-tests terms with edge-case scenarios, and captures
ADRs — run any time the model has drifted or needs hardening. Inline capture keeps
the model current; `skaileup-domain-model` deepens it.

**Consumption is a one-line habit, not this discipline.** Any skill exploring the
project reads `glossary.md` for vocabulary and respects existing ADRs in the area it
touches. If the files don't exist yet, proceed silently — they are created lazily.
