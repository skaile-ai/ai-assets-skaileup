# Decision Rule — Route Selection (long form)

This document is the long-form companion to `SKILL.md`. The skill body keeps
the deterministic rule short; this file documents the verbatim source, the
literal interpretation, the fall-through behavior, one worked example per
tier, and the schema-stability contract for downstream tasks.

Routing has **two stages**:

- **Stage 0 — Shape check (runs first).** Picks a non-app *variant flow* when
  the project isn't a standard sized application. Orthogonal to size.
- **Stage 1 — Tier sizing.** Only runs when Stage 0 resolves to `app`. Picks
  one of the four sizing tiers from the feature/persistence/user signals.

The resolved value (a variant flow id or a sizing tier) is written to `tier`,
and `flow_to_run` is always `flow:<tier>`.

---

## 0. Stage 0 — Shape Check (BEFORE sizing)

The `shape` signal classifies the *kind* of deliverable. It is evaluated first
and, for any non-`app` shape, short-circuits the sizing rule entirely:

```
if existing codebase to extract a concept from:   → reverse-engineer   (shape: reverse-engineer)
elif concept/spec package only, no implementation: → concept-only       (shape: concept-only)
elif headless command-line tool, no UI:            → cli-app            (shape: cli)
else:                                              → run Stage 1 sizing (shape: app)
```

| Shape signal       | Routed flow (`tier`) | When                                                              |
| ------------------ | -------------------- | ----------------------------------------------------------------- |
| `reverse-engineer` | `reverse-engineer`   | Input is an existing repo; extract a concept, then optionally enrich |
| `concept-only`     | `concept-only`       | Deliverable is a concept/handoff package; no build pass            |
| `cli`              | `cli-app`            | Headless CLI tool — no UI, brand, screens, or mockups             |
| `app`              | one of the 4 tiers   | A normal UI application — fall through to Stage 1 sizing           |

The shape is recorded in the optional top-level `shape` field of `scope.yaml`.
When absent it defaults to `app` (backward-compatible with pre-variant scopes).
`shape == app` requires `tier ∈ {mvp, simple-app, standard-app, complex-app}`;
each variant shape requires its 1:1 routed flow (`cli → cli-app`,
`concept-only → concept-only`, `reverse-engineer → reverse-engineer`). The
validator enforces this agreement.

> Variants are **orthogonal to size** — `cli-app`, `concept-only`, and
> `reverse-engineer` are single end-to-end flows, not sized tiers. A CLI tool of
> any size routes to `cli-app`; the sizing rule below applies only to `app`.

---

## 1. Verbatim Source — `SKILL_GRAPH.md` § 3 (lines 132–160)

Quoted unchanged so this file remains the single point of contact for any
future edit. If the upstream rule changes, update `SKILL_GRAPH.md` first,
then mirror the change here, then bump `metadata.version` in the skill.

```
              concept side             implementation side       supervision
              ─────────────            ─────────────────────     ──────────
mvp           linear, minimal          single impl-slice         autonomous
              (no design slicing)      (skip recap, refactor)

simple-app    linear, full             N × impl-slice            autonomous
              (one pass through all    (full slice loop)
              features upfront)

standard-app  linear high-level +      N × impl-slice            mostly autonomous,
              N × concept-slice        (full slice loop +        plan checkpoint
              (per-feature design)      recap mandatory)         per slice

complex-app   linear high-level +      N × impl-slice            HITL — supervised
              N × concept-slice        (full slice loop +        plan + brainstorm
              + project-overview       audit between slices)     + align per slice
```

**Decision rule** the `scope-project` skill follows (order matters — enterprise check sits above the multi-user/feature-count branch so a multi-user enterprise app does not short-circuit to `standard-app`):

```
if features ≤ 1 and persistence trivial:        → mvp
elif features ≤ 5 and single-user:              → simple-app
elif multi-product or enterprise integration:   → complex-app
elif features ≤ 20 or multi-user:               → standard-app
else:                                           → complex-app   # explicit fall-through (large but unclassified)
```

User can override at any time by re-running `scope-project --tier=<name>`.

---

## 2. Interpretation Lock-in

The verbatim rule uses prose terms. The skill needs typed signals. The
following mapping is the authoritative interpretation; the validator and
the skill body both implement it.

| Rule term                              | Signal expression                                                  |
| -------------------------------------- | ------------------------------------------------------------------ |
| `shape`                                | `shape` (one of `app` / `cli` / `concept-only` / `reverse-engineer`) |
| `features`                             | `signals.features_estimate` (integer)                              |
| `persistence trivial`                  | `signals.persistence == "trivial"`                                 |
| `single-user`                          | `signals.multi_user == false`                                      |
| `multi-user`                           | `signals.multi_user == true`                                       |
| `multi-product or enterprise integration` | `signals.persistence == "external"` OR `len(signals.integrations) >= 2` |

Stage 0 maps a non-`app` shape directly to its routed `tier`:
`cli → cli-app`, `concept-only → concept-only`, `reverse-engineer → reverse-engineer`.
Stage 1 (sizing) runs only when `shape == app`.

`flow_to_run` is derived deterministically from `tier` as `flow:<tier>`
(e.g. `flow:simple-app`, `flow:cli-app`). Bare flow ids (the `id:` field inside each
`*.flow.yaml`, per `contracts/asset_frontmatter.md` § Flow) drop the
`flow:` prefix; the prefix is the **runtime reference** form used by
`scope.yaml` consumers, not the flow-file's own id.

---

## 3. Branches — One Sentence + One Example Each

### Branch 1 — `mvp`
Fires when `features_estimate <= 1 AND persistence == "trivial"`. This is
the smallest viable shape: one feature, local state, no DB, no
collaboration. Example: a single-user budget tracker that stores entries
in one local JSON file.

### Branch 2 — `simple-app`
Fires when the previous didn't and `features_estimate <= 5 AND multi_user == false`.
A solo product with up to five features and a real (but single)
data shape. Example: a personal recipe collector with tagging, search,
and a print-friendly view.

### Branch 3 — `complex-app` (enterprise check, runs BEFORE the standard-app catch-all)
Fires when the previous didn't and `persistence == "external" OR len(integrations) >= 2`.
Multi-product, enterprise integrations, queue/bus persistence. This branch
sits above the multi-user/feature-count branch on purpose: a multi-user
enterprise app would otherwise short-circuit to `standard-app` via Branch 4's
`OR multi_user` clause and never reach the complex-app check. Example:
a multi-tenant B2B portal integrating Stripe billing, Salesforce CRM sync,
and a queue-driven order pipeline.

### Branch 4 — `standard-app`
Fires when none of the above and `features_estimate <= 20 OR multi_user == true`.
This catches both larger single-user apps and any multi-user app that did NOT
already trip the enterprise check. Example: a team todo app with assignees,
due-date reminders, comments, and per-project views.

---

## 4. Fall-through Behavior

The four `if/elif` branches do not strictly cover every input. Consider
`features_estimate = 30, multi_user = false, persistence = "structured",
integrations = []`:

- Branch 1 fails (features_estimate > 1).
- Branch 2 fails (features_estimate > 5 — and even if it weren't, multi_user is moot here).
- Branch 3 fails (persistence != "external" AND len(integrations) < 2).
- Branch 4 fails (features_estimate > 20 AND multi_user == false).

The skill **falls through to `complex-app`** in this case and explicitly
documents the fall-through in `reasoning`. Rationale: a 30-feature app
that escapes the first three branches is by feature count alone large
enough to warrant `complex-app`'s HITL supervision and per-slice audit.

If you ever encounter a fall-through in practice, the `reasoning` block
of the produced `scope.yaml` must include a sentence such as:
"None of the four rule branches matched (30 features, single-user,
structured persistence, no integrations); fell through to complex-app."

---

## 5. Worked Examples — Computing `chosen_tier` from `signals`

Each example below is also stored as a fixture in
`skaileup/scope/scope-project/examples/fixtures.json` and as a snapshot
output in `skaileup/scope/scope-project/examples/<tier>.scope.yaml`.

### Example A — mvp
- description: "A single-user personal budget tracker that stores entries in one local JSON file."
- signals: `features_estimate=1`, `multi_user=false`, `persistence="trivial"`, `integrations=[]`
- Branch 1 fires (1 <= 1 AND persistence trivial) → `mvp`.

### Example B — simple-app
- description: "A solo recipe collector with tagging, search, and a print-friendly view."
- signals: `features_estimate=4`, `multi_user=false`, `persistence="structured"`, `integrations=[]`
- Branch 1 fails (persistence not trivial). Branch 2 fires (4 <= 5 AND single-user) → `simple-app`.

### Example C — standard-app
- description: "A team todo app with assignees, due-date reminders, comments, and per-project views."
- signals: `features_estimate=12`, `multi_user=true`, `persistence="structured"`, `integrations=["sendgrid"]`
- Branch 1 fails. Branch 2 fails (multi_user). Branch 3 fails (persistence != external AND only 1 integration). Branch 4 fires (12 <= 20 OR multi_user) → `standard-app`.

### Example D — complex-app
- description: "A multi-tenant B2B portal with assignee/role hierarchies, integrating Stripe billing, Salesforce CRM sync, and a queue-driven order pipeline."
- signals: `features_estimate=35`, `multi_user=true`, `persistence="external"`, `integrations=["stripe", "salesforce", "rabbitmq"]`
- Branch 1 fails (35 > 1). Branch 2 fails (35 > 5). Branch 3 fires (persistence == "external" — and 3 integrations also satisfies `len >= 2`) → `complex-app`. Note: the enterprise check sits above the multi-user/feature-count branch precisely so this case doesn't short-circuit to standard-app.

(Implementation note: the fixtures' `expected_tier` is what the rule
returns, NOT what a human would pick. The four canonical examples are
chosen so each branch fires its own example without needing override.)

---

## 6. Override Semantics

`--tier=<name>` (or the `tier_override` input) bypasses the rule but
records what the rule **would** have picked. The produced YAML always
contains both:

```yaml
tier: <chosen>                         # what the user gets
override:
  applied: true
  requested_tier: <chosen>             # equals tier when applied=true
  rule_would_have_picked: <rule_tier>  # what the deterministic rule produced
```

This makes re-scoping decisions auditable: a future human can see that
the rule would have picked `standard-app` but the user forced
`complex-app`. The validator enforces `override.requested_tier == tier`
when `override.applied == true`.

---

## 7. Schema Stability — Contract for Downstream Tasks

The schema produced by this skill (`schema_version: "1.0"`) is the
canonical contract for downstream tasks 2B / 2C / 2D / 2H. Bumping
`schema_version` is a **major version bump** (per
`contracts/asset_frontmatter.md` § Skills) and requires coordinated
updates to every consumer.

Consumers may rely on:
- `tier` being one of the seven route values — the four sizing tiers
  (`mvp`, `simple-app`, `standard-app`, `complex-app`) or the three variant
  flows (`cli-app`, `concept-only`, `reverse-engineer`).
- `flow_to_run` being `flow:<tier>` exactly.
- `shape` (optional) being one of `app` / `cli` / `concept-only` /
  `reverse-engineer`; absent means `app`. When present it agrees with `tier`.
- All four `signals.*` keys being present.
- `override.applied` being a boolean.
- `chosen_at` parsing as ISO-8601 UTC with a `Z` suffix.

The validator (`validator.py`) enforces all of these. The variant routes were
added additively (the four-tier files remain valid), so `schema_version` stays
`"1.0"`.

> **Schema stability:** the schema in this skill is the canonical contract for downstream tasks 2B / 2C / 2D / 2H. Bumping `schema_version` is a major version bump (per `contracts/asset_frontmatter.md` § Skills) and requires updates to every consumer.
