# Decision Rule — Tier Selection (long form)

This document is the long-form companion to `SKILL.md`. The skill body keeps
the deterministic rule short; this file documents the verbatim source, the
literal interpretation, the fall-through behavior, one worked example per
tier, and the schema-stability contract for downstream tasks.

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

**Decision rule** the `scope-project` skill follows:

```
if features ≤ 1 and persistence trivial:        → mvp
elif features ≤ 5 and single-user:              → simple-app
elif features ≤ 20 or multi-user:               → standard-app
elif multi-product or enterprise integration:   → complex-app
```

User can override at any time by re-running `scope-project --tier=<name>`.

---

## 2. Interpretation Lock-in

The verbatim rule uses prose terms. The skill needs typed signals. The
following mapping is the authoritative interpretation; the validator and
the skill body both implement it.

| Rule term                              | Signal expression                                                  |
| -------------------------------------- | ------------------------------------------------------------------ |
| `features`                             | `signals.features_estimate` (integer)                              |
| `persistence trivial`                  | `signals.persistence == "trivial"`                                 |
| `single-user`                          | `signals.multi_user == false`                                      |
| `multi-user`                           | `signals.multi_user == true`                                       |
| `multi-product or enterprise integration` | `signals.persistence == "external"` OR `len(signals.integrations) >= 2` |

`flow_to_run` is derived deterministically from `tier` as `flow:<tier>`
(e.g. `flow:simple-app`). Bare flow ids (the `id:` field inside each
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

### Branch 3 — `standard-app`
Fires when neither of the above and `features_estimate <= 20 OR multi_user == true`.
This catches both larger single-user apps and any multi-user app, even
small ones. Example: a team todo app with assignees, due-date reminders,
comments, and per-project views.

### Branch 4 — `complex-app`
Fires when none of the above and `persistence == "external" OR len(integrations) >= 2`.
Multi-product, enterprise integrations, queue/bus persistence. Example:
a B2B portal integrating Stripe billing, Salesforce CRM sync, and a
queue-driven order pipeline.

---

## 4. Fall-through Behavior

The verbatim rule's four `if/elif` branches do not strictly cover every
input. Consider `features_estimate = 30, multi_user = false,
persistence = "structured", integrations = []`:

- Branch 1 fails (features_estimate > 1).
- Branch 2 fails (features_estimate > 5).
- Branch 3 fails (features_estimate > 20 AND multi_user == false).
- Branch 4 fails (persistence != "external" AND len(integrations) < 2).

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
- Branch 1 fails. Branch 2 fails (multi_user). Branch 3 fires (12 <= 20 OR multi_user) → `standard-app`.

### Example D — complex-app
- description: "A multi-product B2B portal with single-tenant deployments, integrating Stripe billing, Salesforce CRM sync, and a queue-driven order pipeline."
- signals: `features_estimate=35`, `multi_user=false`, `persistence="external"`, `integrations=["stripe", "salesforce", "rabbitmq"]`
- Branch 1 fails (35 > 1). Branch 2 fails (35 > 5). Branch 3 fails (35 > 20 AND multi_user=false). Branch 4 fires (persistence == "external") → `complex-app`.

**Important note on Example D's signals.** A multi-user 35-feature app
with external persistence would actually fire Branch 3 (`features_estimate <= 20 OR multi_user`)
under the literal rule and produce `standard-app`. To exercise Branch 4
with a clean fixture, Example D pins `multi_user=false`: a single-tenant
B2B portal where each customer gets their own deployment. The integrations
and external persistence are what make it complex; the multi-tenancy is
not what triggers Branch 4. If you encounter a multi-user enterprise app
in practice, expect the rule to return `standard-app`; that result can
either be accepted or overridden via `--tier=complex-app`.

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
- `tier` being one of the four enum values.
- `flow_to_run` being `flow:<tier>` exactly.
- All four `signals.*` keys being present.
- `override.applied` being a boolean.
- `chosen_at` parsing as ISO-8601 UTC with a `Z` suffix.

The validator (`validator.py`) enforces all five.

> **Schema stability:** the schema in this skill is the canonical contract for downstream tasks 2B / 2C / 2D / 2H. Bumping `schema_version` is a major version bump (per `contracts/asset_frontmatter.md` § Skills) and requires updates to every consumer.
