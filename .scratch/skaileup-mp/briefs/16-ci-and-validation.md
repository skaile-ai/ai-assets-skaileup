# Brief: 16 — CI and validation

Evidence for the grilling ticket `.scratch/skaileup-mp/issues/16-ci-and-validation.md`.
**Nothing here is a resolution.** Every question the ticket asks is left open at the bottom.

Path aliases used below:

| alias | path |
|---|---|
| `SK/` | `/Users/matthias/devBench/SKAILEdev/ai-assets/ai-assets-skaileup/` |
| `MP/` | `/Users/matthias/devBench/SKAILEdev/ai-assets/ai-assets-skaileup-mp/` |
| `FC/` | `/Users/matthias/devBench/SKAILEdev/forge/forge-concept/` |
| `WS/` | `/Users/matthias/devBench/SKAILEdev/workspaces/packages/workspaces/` |

---

## 0. Correction to the ticket's own premises

Three of the ticket's framing statements are off, and each changes the shape of the decision:

1. **"Today a pre-commit hook … `-mp` is a fresh repo, so CI is a free choice."**
   The old repo **already has GitHub Actions**: `SK/.github/workflows/collection-ci.yml`
   (49 lines, 3 jobs). The pre-commit hook is the *lesser* half of the story and, as
   measured below, **is not installed**. CI is not a new idea here; it is the thing that
   actually runs.
2. **"`verify_artifacts.py` … is dead on arrival."** Two of its checks are not about the
   registry at all — a **restatement detector** and a **line-budget check** — and the
   line budget is ticket 03's ceiling in code. See row 5 of the table.
3. **"`ac_lib.py` is why `acceptance_criteria.md` survived … the EARS grammar."**
   `ac_lib.py` contains **no EARS check**. It validates ledger structure. The only EARS
   regex in the repo lives in a per-skill validator, not in `ac_lib`. See §5.

The ticket also misses a validator entirely: **`docs/scripts/audit.py`**, which is CI job #1.

And one fact from outside the ticket reframes the whole flow half: **forge-concept — the
acceptance target — runs no flow schema validation at all** (§3). Whatever `-mp` validates
about its own flows, it validates for itself.

---

## 1. The validator table

Every executable under `contracts/scripts/`, `flows/_meta/`, and (added) `docs/scripts/`.

| # | Validator | Lines | What it validates | Still exists after 03/09/15? | Invoked by | Verdict-evidence |
|---|---|---|---|---|---|---|
| 1 | `SK/skaileup/flows/_meta/verify_flows.py` | 372 | 7 checks: flows validate against `contracts/flow.schema.json`; `id` == dir/filename stem; every `nodes[].data.skill` resolves to a real `name:`; `requires:` skill-set **exactly** == node-skill set; `requires:` flow-set exactly == sub-flow targets; `contract:` refs resolve in `skaile.yaml`'s `assets:`; scoped-ref grammar `kind:@pub/name`; `parentNode` → group node; router `target` → node id; no stray `*.flow.yaml` outside `flows/` | **Partly.** Flow contract survives (ticket 01/15). But it validates the *stale* schema (§3), and two of its inputs die: `skaile.yaml`'s `assets:` block (absent in `MP/` by design) and the hardcoded `ALL_FLOWS` list | CI job `flows`; pre-commit check #4 (hook not installed); nothing else | Runs green today: `OK: 17 flows consistent … 0 warning(s)`, exit 0 |
| 2 | `SK/skaileup/flows/_meta/test_verify.py` | 446 | 14 pytest cases over #1 (happy path, unresolved skill, deferred warn, missing/extra requires, unknown contract, schema violations, new node/edge types, phase fields, dangling `parentNode`, bad router target, shared sub-flow registration) | Tracks #1 | CI job `flows` (`pytest`) | Depends on `pytest`; hardcodes the 17-flow shape |
| 3 | `SK/skaileup/contracts/scripts/lint_concept.py` | 575 | 6 passes over a target project's `_concept/`: `check_structure`, `check_frontmatter`, `check_golden_principles`, `check_cross_references`, `check_model`, `check_seed` | **Half.** The structure/frontmatter/golden halves point at paths tickets 05/07/08 are moving; the model/seed half validates `postxl-schema.json`, which `golden_principles.md` itself demotes to derived (§4) | **Nothing automated.** Named in prose only: `SK/skaileup/00_skaileup-orchestrator/skills/skaileup/SKILL.md:342`, `…/agents/skaileup-conceptualize/SOUL.md:62`, `contracts/README.md:85`, `contracts/DOMAIN.md:37`. Not in CI, not in the hook | Both prose call sites are files ticket 12 already deletes (`SOUL.md` — no `agents/` in `-mp`; the orchestrator skill is replaced) |
| 4 | `SK/skaileup/contracts/scripts/validator_lib.py` | 416 | Not a validator — the **shared library** behind the per-skill `validator.py` files. `Validator` class with `must`/`never`/`checklist`/`skip` registrars + ~20 primitives (`file_exists`, `parse_frontmatter`, `json_schema_validate`, `folders_match_pattern`, `every_key_maps_to_existing_file`, …) | **Its consumers are the question, not the file.** It is imported by **~20 per-skill `validator.py` files** across 8 domains — far more than the ticket's "checks `_concept/` against `golden_principles`" framing | ~20 `validator.py` files (`import validator_lib`), each invoked by #6 or by a skill body. Not in CI | Ticket 03 kept "a hard guardrail survives as a named failure **with a check behind it**" — this library *is* that check mechanism |
| 5 | `SK/skaileup/contracts/scripts/verify_artifacts.py` | 280 | 7 registry checks against `contracts/artifacts.yaml` (well-formed, producer-exists, id-in-registry, no-dangling, producer-bidirectional, registry-has-producer, path-match) **plus two non-registry checks**: `check_restatements` (ERROR if a `MUST`/`NEVER` line shares an 8-gram with any contract) and `check_line_budget` (WARN over 400 lines) | **Registry half dead** — ticket 09 dropped `artifacts.yaml`. **Restatement check dead** — ticket 03 removed `MUST`/`NEVER` lines, so the detector has nothing to scan. **Line budget alive in spirit** — ticket 03 set the ceiling at 140 | CI job `artifacts`; pre-commit check #3 (hook not installed) | Runs today: `79 registry ids · 0 errors · 7 warnings`, all 7 warnings are the line budget, incl. `mockup-walkthrough-astro 1133 lines` (ticket 03's port target) |
| 6 | `SK/skaileup/contracts/scripts/validate_skill_rules.py` | 582 | Claude Code `PostToolUse` hook. Finds `validator.py` next to a `SKILL.md`, runs it, formats violations; `--semantic` chains an LLM (default haiku, 300 s timeout, ≤40 files, ≤50 000 chars/file) for rules the compiled validator marked `skip` | **Dead as written.** It is the DSL's `MUST`/`NEVER`/`CHECKLIST` enforcement path; ticket 03 removed the blocks and ticket 09 deleted `skill_grammar.md`. Its docstring examples still use pre-2026-05 skill names (`concept-2-experience-4-storybook`) | A Claude Code hook that **is not configured anywhere in this repo** — no `.claude/settings.json` wiring found; only prose (`contracts/DOMAIN.md:44` "lab/validate runs it", `skill_grammar.md:220`) and the SOUL/agent.yaml of an agent tree `-mp` does not have | Its `SKILL_SUBDIRS = ["concept", "implement", "support"]` predates two reorganizations |
| 7 | `SK/skaileup/contracts/scripts/ac_lib.py` | 125 | Structure of an `.ac.md` ledger: 5 required frontmatter keys, ≥1 `## AC-n` / `### AC-Bn` section, a `## Criteria Status` table with header `\| ID \| Source \| Status \| Updated by \| Date \|`, status ∈ `untested\|pass\|fail`, non-empty `Source`, `Updated by`+`Date` filled on non-`untested` rows, and **bidirectional heading↔row consistency** | Yes — but **it does not check EARS** (§5) | 2 per-skill validators: `11_impl-plan/03_plan-vertical/validator.py:309`, `12_impl-slice/04_test/validator.py:278`. Not in CI | Both callers are skills ticket 07 folds into `build-plan` / `build-implement` |
| 8 | `SK/skaileup/contracts/scripts/pre-commit` | 81 | See §2 | See §2 | **Not installed** | §2 |
| 9 | `SK/skaileup/contracts/tests/test_verify_artifacts.py` | 84 | Dedup guards in #5 | Registry half dead with #5 | CI job `artifacts` (`pytest skaileup/contracts/tests/`) | Ticket 16 says "`tests/` already deleted" — true of the `MP/` skeleton, **not** of `SK/`, where it still exists alongside the `elements_block_examples.md` fixture |
| 10 | `SK/docs/scripts/audit.py` | 169 | Frontmatter audit over every `SKILL.md`: missing `metadata.version` / `stage` / `tags`; deprecated `user_inputs`, `reads_from`, `writes_to`; `stage: stable` with no `validator.py` | **Half.** Ticket 01 says frontmatter actually read is `version`, `artifacts.requires[].id`, `prerequisites.*`, `requires`; `stage` and `tags` are documentation. The `stage: stable ⇒ validator.py` rule is a live design statement about #4 | **CI job `audit`** — the first job in `collection-ci.yml` | Not mentioned anywhere in ticket 16. Runs green: `88 skills audited: 0 errors, 0 warnings` |

**Dependencies.** All Python. `from __future__ import annotations` + PEP-604 `X \| None` throughout
⇒ effectively **3.10+**; CI pins **3.12**. Third-party: `pyyaml` (#1,2,5,7, and #4 lazily at
`validator_lib.py:156`), `jsonschema` (#1,2, and #4 lazily at `:325`), `pytest` (#2,9).
`lint_concept.py` (#3), `validate_skill_rules.py` (#6) and `audit.py` (#10) are **stdlib-only** —
#3 and #10 each hand-roll their own frontmatter parser rather than take the PyYAML dependency.

---

## 2. The pre-commit hook

`SK/skaileup/contracts/scripts/pre-commit`, 81 lines, bash, `set -euo pipefail`.

It wires **four** checks, all conditioned on what is staged:

| # | Trigger | Check | Status after 03/09 |
|---|---|---|---|
| 1 | any staged `SKILL.md` | greps for the string `_grounding/general/` (a path renamed to `_grounding/research/`) | A one-off migration guard from a 2026-era rename. Nothing in `-mp` has ever had `_grounding/general/` |
| 2 | any staged `SKILL.md` | greps for deprecated `user_inputs:` / `reads_from:` / `writes_to:` | **Duplicates `audit.py` checks 1–3 exactly** (`docs/scripts/audit.py:53-55`), which CI already runs on every push |
| 3 | staged `SKILL.md` or `contracts/artifacts.yaml` | `verify_artifacts.py` must print `0 errors` | Dies with `artifacts.yaml` |
| 4 | staged `*.flow.yaml` | `verify_flows.py` exit 0 | The live one |

**Installation is manual and has not been done.** The header instructs
`cp skaileup/contracts/scripts/pre-commit .git/hooks/pre-commit`. `SK/` is a submodule, so its
hooks live at `/Users/matthias/devBench/SKAILEdev/.git/modules/ai-assets/ai-assets-skaileup/hooks/`
— that directory is **empty of non-`.sample` files**. So the hook has never fired in this
checkout. Checks 3 and 4 also degrade to a `WARN: … skipping` line when PyYAML/jsonschema are
missing, i.e. it is advisory even when installed.

**Ecosystem context:** across all 8 SKAILE repos surveyed (`forge-concept`, `forge-common`,
`forge-workspace`, `workspaces`, `platform`, and the three `ai-assets/*`), **no repo has an
active git hook** — no `.husky/`, no `lefthook.yml`, no `.pre-commit-config.yaml`, no installed
`.git/hooks/*`. The house pattern is GitHub Actions only.

---

## 3. `verify_flows.py` vs the schema that is actually enforced

Ticket 15 established: one schema, `FlowManifestSchema` in `@skaile/workspaces`
(`WS/factory-assets/connectors/flow/engine/flow-manifest.ts:30-98`), every level `z.looseObject`,
required = `id` + `name` at top, `id` per node, `source`+`target` per edge, everything else
optional. Platform adds three imperative checks (unique node ids, no dangling endpoints, no
self-loops).

**Refinement measured this session, and it matters for ticket 16.** Ticket 15 recorded that
"platform's `validateFlow` is the same export forge-concept's loader ships". *Ships* is not
*calls*: `grep -rn "validateFlow\|FlowManifestSchema" FC --include='*.ts'` excluding
`node_modules` and `.output` returns **zero real call sites**. forge-concept never runs the zod
schema. Its only shape gate is `loadFlowsFromDir`'s truthy check on `id`/`nodes`/`edges`
(`WS/…/loader.ts:41-63`) — a file missing any of the three is silently discarded, and a file
that has all three is accepted whatever else is in it.

So for the **acceptance target**, the enforced rule set is exactly two things:
`id`+`nodes`+`edges` present, and the engine's `edges.filter(e => e.type === "flow")`.
Everything else — including the zod schema — is platform-side, and ticket 15 already
established platform is not a file host and will never see `-mp`'s flow files unless a human
imports one.

Three further measurements tighten ticket 15's table:

- `FlowEdgeSchema` (`flow-manifest.ts:50-55`) declares only `id`, `source`, `target`,
  `condition` — **`type` is not a field of the schema at all**, so it rides through as an
  unchecked loose-object extra. The `EdgeType` union `flow|parallel|optional` is a
  compile-time TypeScript type (`types.ts:155`), never a runtime check.
- Node `type` is `z.string().optional()` — a **free string**. The
  `skill|group|sub-flow|router` union (`types.ts:81`) is likewise compile-time only. Nothing at
  runtime would reject a `gate` node; it would simply do nothing.
- **`data.phase` is not in the zod schema either.** `FlowNodeSchema.data` validates only
  `optional` and `approval.mandatory`. The three-value `Phase` union lives in forge-concept's
  UI layer (`FC/shared/flow-phases.ts:8`, `isPhase` at `:31-33`), not in manifest validation.
  So `flow.schema.json`'s `phase` enum is the **only** machine enforcement of ticket 04's
  every-node-declares-phase rule that exists anywhere.

`verify_flows.py` does not implement any of that directly — it delegates shape entirely to
`SK/skaileup/contracts/flow.schema.json`, which ticket 15 showed is the stale artefact.
Measured against the 17 live flows (`python3` walk, this session):

```
flows: 17
edge types: {flow: 94, optional: 52, parallel: 6, review-loop: 1}   untyped edges: []
node types: {skill: 130, sub-flow: 27, group: 24, router: 4}        gate nodes: 0
nodes with position: 185 / 185                                      nodes with data.phase: 57
```

### Where the script checks things nothing enforces

| Script/schema demands | Reality |
|---|---|
| `position: {x, y}` **required** on all 5 node kinds | Engine documents it as unused (`WS/…/types.ts:84-88`); platform recomputes with dagre. 185/185 nodes carry it as pure hand-authoring tax |
| `gate` node kind, requiring `data.check` + `data.on_fail` | Not an engine node kind. **0 uses in 17 flows.** Note the vocabulary collision: `CONTEXT.md` line 50 defines **Gate** as *a precondition on running a skill*, hard or soft — a different thing from this node type |
| edge `type: review-loop` (+ `max_iterations`, `exit_condition`) | Not an `EdgeType`. 1 use, in `skaileup-stepwise`, and per §"the sharpest rule" below it is **already a no-op** |
| `additionalProperties: false` at ~12 levels | Runtime is `looseObject`. Concretely: top-level props are `[$schema, description, edges, entry, globals, id, meta, modes, name, next_flows, nodes, requires, version]` — so a flow written with workspaces' own spelling **`metadata:`** would be **rejected** by this schema, as would `tier_presets` / `artifact_handoff` |
| `modes:` block with `research`/`standards` sub-schemas | Ticket 15: `modes` has **no reader in any of the three repos** |
| `requires:` exactness (script check #4) | Nothing at runtime reads `requires` for *exactness*; it drives transitive install (ticket 01). The exact-match rule is a house rule, and a strong one — but it is ours |
| `contract:` refs resolve in `skaile.yaml` `assets:` (check #5) | `MP/skaile.yaml` **deliberately ships no `assets:` block** (newer workspaces throws on it — ticket 01). `gather_known_contracts()` would return an empty set, so this check **silently degrades to "every contract ref is unknown"**, i.e. it inverts from a guard into a blanket failure |
| hardcoded `ALL_FLOWS` list of 17 ids + `PHASE_2_PLANNED` set of 12 names + `deferred_skills.yaml` | Migration scaffolding from Phases 2/3. `deferred_phase_3: []` since 2026-05-30. In `MP/` (`flows/` deliberately empty) the script would emit 17 × `missing flow file` |

### Where the script misses what the runtime does enforce

| Runtime rule | Does `verify_flows.py` catch it? |
|---|---|
| **`edges.filter(e => e.type === "flow")` — an edge with no `type` orders nothing** | **No.** `flow-edge.required = ["id", "source", "target"]`; `type` is optional with `"default": "flow"`, and JSON-Schema `default` is annotation-only — draft-07 validators do not inject it. An untyped edge validates green, draws on both canvases, and creates **zero** dependency. Ticket 15 verified this against `computeFlowState`. **Nothing in this repo checks it.** The 17 flows are safe today by authoring habit alone |
| Unique node ids | **No** |
| No dangling edge endpoints (`source`/`target` → real node) | **No.** The script checks `parentNode` → group node and router `target` → node id, but **not plain edge endpoints** |
| No self-loops | **No** |
| Top-level `name` present (platform's `validateFlow` requires it; forge-concept's loader does not) | **Yes** — `flow.schema.json` `required: ["id","name","nodes","edges"]`. This is the one place the stale schema is stricter in a way that helps: it satisfies both required-sets at once |
| `data.phase` ∈ `conceptualization\|implementation\|review` | **Yes**, via the schema's enum — and ticket 15 flagged this as the one place the schema is right and workspaces is silent. Load-bearing for `-mp` because ticket 04 made every node declare `phase` explicitly |
| Edge type ∈ `flow\|parallel\|optional` (the real `EdgeType`) | **Partly** — the schema's enum is that set **plus** the non-existent `review-loop` |

**Net:** of the four cheap checks ticket 15 handed to ticket 16 (untyped edge, unique ids,
dangling endpoints, self-loops), `verify_flows.py` currently implements **zero**.

### Already-live tension in `MP/`

`MP/contracts/flow.schema.json` is **byte-identical** to `SK/skaileup/contracts/flow.schema.json`
(diff exit 0, 434 lines both). The ticket-11 skeleton forked the stale file verbatim, before
ticket 15 established it was stale. Ticket 15's ruling — "this file **ports narrowed or not at
all**" — is therefore not yet executed.

---

## 4. `lint_concept.py` + `golden_principles.md`

`golden_principles.md` is 112 lines / 9 rule sections. `lint_concept.py` mechanizes some of it,
skips some, and **contradicts one section outright**.

### What it enforces, against which paths

| Pass | Rules | Paths it hard-codes | Survives 07/08? |
|---|---|---|---|
| `check_structure` | 6 required artifacts + 4 optional | `discovery/`, `experience/journeys`, `experience/features`, `experience/screens`, `blueprint/techstack.md`, `blueprint/datamodel`, `discovery/brand/tokens.json` | **Ticket 08 open.** Two of the six name skills that ticket 07 already deleted, in the remediation strings: "Run `product-spec-features`", "Run `experience-screens`", "Run `impl-architecture-datamodel`" |
| `check_frontmatter` | every `.md` needs frontmatter; `status ∈ {draft, approved, implemented, tested, mockup_ready}`; `last_updated` ISO; features need `priority`/`roles`/`screens`/`data_entities`; screens need `implements` | `experience/features/`, `experience/screens/` (with an `experience/screens/00_layout` exemption) | The `00_layout` exemption is an `NN_`-prefixed path — ticket 04 killed `NN_` in the collection tree but **ticket 05 explicitly deferred the `_concept/` folder list to 07/08** |
| `check_golden_principles` | feature-group folders match `^\d{2}_`; group numbers sequential with no gaps; screen groups mirror feature groups; every feature file has a `- [ ]` checkbox; every screen has `## Component Inventory` (or `## Components`) and `## States`; no spaces in filenames | same two trees | **The `^\d{2}_` rule is the live collision.** Ticket 05 renamed *feature group* → **featureset**; ticket 07 renamed the concept dossier to `_concept/dossiers/<feature_slug>/`. Whether `-mp` artifact folders keep `NN_` is undecided |
| `check_cross_references` | feature `screens[]` paths exist; screen `implements[]` paths exist; feature `data_entities[]` ∈ model names | `experience/features`, `experience/screens`, **`blueprint/datamodel/postxl-schema.json`** | See the inversion below |
| `check_model` | `postxl-schema.json` has `name`/`slug`/`models`; **model names PascalCase**; `standardFields ⊇ {id, createdAt, updatedAt}`; **field names camelCase**; relation fields end **`Id`**; inline enum values PascalCase | `blueprint/datamodel/postxl-schema.json` | **Inverted — see below** |
| `check_seed` | `seed.json` has scenarios `empty`/`single_user`/`populated`/`edge_cases`; `populated` ≥2 entries per model; **model keys PascalCase** | `blueprint/datamodel/seed.json` | Scenario-name half matches the contract; the PascalCase-key half is inverted |

### The inversion (sharpest finding in this section)

`golden_principles.md:8-46` governs the **semantic** model and demands:

> entity names `lowercase_snake_case` singular · field names `lowercase_snake_case` ·
> relation fields end **`_id`** · **"Translation note:** Output conventions (PascalCase model
> names in Prisma/PostXL, camelCase fields) are applied by the stack translator — **never in
> the semantic layer.**"

and `golden_principles.md:82-84`:

> "`model.json` is the canonical stack-agnostic data model. Stack-specific files
> (`schema.prisma`, `postxl-schema.json`) are **derived** — cross-references always target
> `model.json`."

`lint_concept.py` `check_model` / `check_seed` / the entity half of `check_cross_references`
open **`postxl-schema.json`** and enforce **PascalCase models, camelCase fields, `Id` suffix**.
That is the translated PostXL output judged by PostXL conventions. `model.json` — the file
`golden_principles.md` names canonical, and the file the datamodel skill actually writes
alongside `model.dbml` / `seed.json` / `feature_map.json` — appears **nowhere** in
`lint_concept.py`. `grep -rn "model.json" lint_concept.py` → no hits.

So the one validator the ticket calls out as having "a live justification" is, in three of its
six passes, checking a derived single-template artifact against rules its own contract says
apply to the layer above it. Independent corroboration inside the collection:
`SK/skaileup/14_ops/10_add-feature/SKILL.md:306` lists "Using PascalCase seed entity keys" as a
**failure mode**, fix: "Use singular snake_case keys per golden_principles.md" — the exact rule
`check_seed` enforces in reverse.

Rules in `golden_principles.md` that **nothing mechanizes**: the entire Entity/Field/Enum/
Relation semantic set (as applied to `model.json`), `## Description` section required per
feature, `roles` non-empty, the bidirectional screen↔feature back-link, `story_refs` → `stories.yaml`,
and every Seed Data Rule except the four scenario names.

---

## 5. `ac_lib.py` + `acceptance_criteria.md`

**There is no EARS grammar check in `ac_lib.py`.** The file (125 lines) validates the *ledger*:
frontmatter keys, section↔row bijection, the status table's header shape, the status enum, and
that `Source` is non-empty. ~~The word EARS appears in it **zero times**.~~
**[Corrected 2026-09-05, re-verified: it appears once — `ac_lib.py:108`, inside an error
string ("Source cell must cite the EARS line / story-id"), not a check. The finding
stands; only the "zero times" phrasing was wrong.]**

The only EARS regex in the whole collection is in a per-skill validator:

```
SK/skaileup/11_impl-plan/02_align/validator.py:52
EARS_RE = re.compile(r"WHEN\b.+\bTHE\s+\S+\s+SHALL\b.+", re.IGNORECASE)
```

used once, at `:154`, to require ≥1 EARS line inside a `## Acceptance handoff` section. Its
comment says "same regex as concept-slice-align", i.e. it is **copy-pasted**, not shared through
`ac_lib`. It matches only the event-driven variant — `WHILE …` (state-driven) and
`IF … THEN …` (unwanted behaviour), both listed as canonical at
`SK/skaileup/contracts/acceptance_criteria.md:211-222`, would not match.

**Who calls `ac_lib` in-body / in-validator:** exactly two, both per-skill `validator.py`, both
in skills ticket 07 dissolves:

| Caller | Line | Mode |
|---|---|---|
| `11_impl-plan/03_plan-vertical/validator.py` | `:309` | `validate_ac_file(path, require_untested=True)` — creation, every row must be `untested` |
| `12_impl-slice/04_test/validator.py` | `:278-282` | `validate_ac_file(path)` + an extra rule: an updated row's `Updated by` must name a known updater skill |

`acceptance_criteria.md:244-253` names four owners of the ledger — `impl-plan-plan-vertical`
(creates), `impl-slice-test` (flips rows), `impl-quality-test-e2e` (flips journey rows),
`ops-trace` (reads) — and closes with "Validation: `…/ac_lib.py` (`validate_ac_file`)". Two of
those four owners are skills ticket 07 merged; the other two sit in tickets 17 and (unowned)
`ops`. Ticket 09 shrank the contract "to the EARS grammar" — that is the ~15-line
`## EARS template` section (`:211-222`), which is precisely the part **no code reads**.

---

## 6. The candidate new validator: `name:` == directory name

### It is genuinely unchecked

`grep` for any comparison between a `SKILL.md` frontmatter `name:` and its parent directory,
across `contracts/scripts/`, `flows/_meta/`, `docs/scripts/`: **no hit.** The only
`parent.name` in the whole validator set is `test_verify.py:75`, where it is a *flow* directory,
and the only stem comparison is `verify_flows.py:267` (`flow id` vs filename stem) —
the flow analogue of the rule, never the skill one.

More than unchecked: today it is **near-universally violated by design**. Measured this session
over all 88 `SKILL.md` in `SK/skaileup/`:

```
name == dir : 3      (skaileup, skaileup-build, skaileup-domain-model — ticket 04's exception)
name != dir : 85
no name     : 0
```

`verify_flows.py` `gather_existing_skill_names()` reads `name:` from frontmatter and never looks
at the path, so it validates flow references correctly *and is blind to the mismatch* by
construction.

### What holds it together today, and why that support is gone in `-mp`

`SK/skaile.yaml` carries an explicit **`assets:` block, 359 lines**, one entry per asset:

```yaml
  - kind: skill
    name: concept-brief
    root: skaileup/01_concept/01_brief
```

That table *is* the name↔path map. Ticket 01 established the block is **dead in newer
workspaces (it throws)**, and ticket 11 acted on it: `MP/skaile.yaml` **deliberately ships no
`assets:` block**, with a comment saying discovery runs in glob mode. `MP/skills/README.md`
already states the rule — "directory name == the skill's `name:` field verbatim".

### Blast radius — the four roles

Ticket 01 §2.3 pins the chain. Under glob discovery the directory becomes the identity:

```
WS/cli/src/skill-walker.ts:56-67  (walkSkills)
  out.push({ name: entry.name, path: full, skillPath: skillMd, domain });
```

`walkSkills` **never opens `SKILL.md`** — it takes `entry.name`, the directory name, as the
skill's name, and `findSkills()` de-dupes on it. Corroborated by
`FC/server/utils/skill-docs.ts:35`, whose own comment reads
`name: entry, // directory name is the canonical skill ID`.

| Role | Resolves via | Breaks how, when `name:` ≠ dir |
|---|---|---|
| **1. Install path** | `walkSkills` → dir name; `WS/core/src/workspace-config.ts:2363-2436` (`stageMaterializedSkills`) stages `.skaile/assets/skill/<name>/` → `<skillsDir>/<name>/` | The skill installs under its **directory** name. Frontmatter `name:` is not consulted |
| **2. Flow `data.skill`** | `run.post.ts:53-54` → `resolveSkillContent(skillId)` → `{root}/.claude/skills/{skillId}/SKILL.md` (`FC/server/utils/skill-content.ts:17-27`) | A flow authored against frontmatter `name:` looks for a directory that does not exist. **`data.skill` is a path segment, not a lookup key** |
| **3. `produced_by`** | `artifacts.yaml` → `getArtifactsForSkill()` → `produced_by[0]` (`FC/…/artifact-contract.ts:232-235`) | **Moot in `-mp`** — ticket 09 deleted `artifacts.yaml`, and ticket 01 showed it was unreachable as deployed anyway |
| **4. Grounding path** | `WS/resolver/src/validator.ts:107`: `join(projectDir, "_concept", "_grounding", skillId, "input.json")`; same in `FC/server/utils/concept-agent.ts:379-400` | The dialog-input file is written to / read from a folder named for whichever of the two won upstream — a split-brain if the two disagree |

So **three of four roles are live and two of those three take the directory name directly**.

### forge-concept fails silently — measured

The mismatch is not merely unchecked; it is **structurally invisible**, and the miss it causes
degrades quietly rather than erroring:

- `FC/server/utils/skill-content.ts:17-46` (`resolveSkillPath`) joins `skillId` as a literal path
  segment: `join(dir, skillId, "SKILL.md")`. It **never reads frontmatter**.
- `FC/server/utils/skill-docs.ts:29-56` does parse the frontmatter block into a `meta` map — and
  then **discards `meta.name`**, hard-coding `name: entry` with the comment
  `// directory name is the canonical skill ID`. Only `meta.description` is kept.
- On a miss, `FC/server/api/flows/nodes/[nodeId]/run.post.ts:78-80` does **not** throw. It falls
  back to a generic prompt:
  `` `Run skill ${skillId}\n\nExecute the ${skillId} skill for this project.` ``
  The node runs. It just runs with no skill body.
- On the same miss, `FC/server/api/flows/nodes/[nodeId]/requirements.get.ts:37-48` returns
  `{ skillId, satisfied: true, files: [], inputs: [], reads: [] }` — a **fabricated all-clear**.
  A skill that does not exist reports zero unmet requirements.
- `produced_by` (`FC/…/artifact-contract.ts:152-176`, `:232-247`) and the grounding folder
  (`FC/server/utils/grounding.ts:19-23`, `stepId.replace(/^cf_/, "")`) are likewise raw-string
  matches against the same key, never cross-checked against a `SKILL.md`.

**Nothing in forge-concept reads a `SKILL.md`'s `name:` for identity at all.** The frontmatter
field is not a second source of truth that can disagree — it is a field with no reader on the
identity path. Which is precisely why a violation is silent: the directory always wins, the
flow reference silently resolves to nothing, and the node reports `satisfied: true`.

`-mp` also has a fifth, softer role ticket 04 introduced: the **domain is the first name segment**
(`concept-` / `spec-` / `build-` / …), and `phaseForNode` falls back to name prefixes when
`data.phase` is absent (`FC/shared/flow-phases.ts:35-41`). Ticket 04 defused this by requiring
explicit `data.phase` on every `-mp` node — so the prefix is documentation, not a contract, **as
long as the `data.phase` rule holds**. Nothing checks that either; the schema makes `phase`
optional.

---

## 7. What CI exists in this ecosystem — the house pattern

`SK/.github/workflows/collection-ci.yml`, 49 lines, `on: push[main] + pull_request[main]`,
three independent jobs on `ubuntu-latest` / `actions/setup-python@v5` **Python 3.12**:

| Job | Installs | Runs |
|---|---|---|
| `audit` | nothing | `python3 docs/scripts/audit.py` |
| `flows` | `pyyaml jsonschema pytest` | `verify_flows.py`, then `pytest skaileup/flows/_meta/test_verify.py -q` |
| `artifacts` | `pyyaml pytest` | `verify_artifacts.py`, then `pytest skaileup/contracts/tests/ -q` |

All three pass on the current tree (verified by running them: exit 0 / 0 / 0).
Note the shape: **script + its pytest, per concern** — the tests are treated as part of the gate,
not as a separate suite.

Across the ecosystem:

| Repo | Workflows | Stack |
|---|---|---|
| `ai-assets-skaileup` | `collection-ci.yml` | **Python** — the only Python CI in the ecosystem |
| `ai-assets-skaileup-mp` | **none**, no `.github/` at all | — |
| `ai-assets-skill-development`, `ai-assets-skaile-powers` | **none**, no `.github/` at all | — |
| `forge-concept` | `ci.yml` (SSH-agent + `forge-shared` submodule clone, Bun 1.3.9, `bunx nuxi typecheck`, `bun run test:unit`, Hocuspocus `:1234` smoke), `build-image.yml` (GHCR) | Node/Bun |
| `forge-common` | `ci.yml` (Biome lint `continue-on-error`, typecheck, vitest), `release.yml` | Node/Bun |
| `forge-workspace` | `typecheck.yml` only | Node/Bun |
| `workspaces` | `ci.yml`, `release.yml`, `docs.yml`, `claude-code-review.yml`, `changeset-check.yml` | Node/Bun, self-hosted runners |
| `platform` | 11 workflows (ci, e2e, version, changeset-check, nix-build, agent-image-build, claude-code-review, claude, …) | Node/Bun + Nix + Docker |

**No shared/reusable workflow anywhere** — every repo's YAML is a self-contained copy of a
common style. **No active git hook in any of the 8 repos.** So the house pattern is:
GitHub Actions, per-repo, hand-rolled; and the two sibling asset collections run **no CI at all**,
which is the live precedent for "nothing until the collection is populated".

### The map's acceptance test, measured

`FC/tests/integration/skaileup-flows.test.ts` is **130 lines**, and it asserts far less than the
map's "flows load green" phrasing suggests.

*What it does:* writes a throwaway `skaile.yaml` naming 6 flows
(`appbuilder-mvp|simple|standard|complex`, `skaileup-slice-concept`, `skaileup-slice-impl`) and
2 skills (`concept-brief`, `concept-goals`), then two tests:

| Test | Assertions |
|---|---|
| `install() deploys every declared flow and skill` (`:85-104`) | `result.missing` is empty; `result.deployed` contains `flow:<id>` / `skill:<name>` for each; the flow dir and each `<flowsDir>/<id>` exist; `readdirSync(skillsDir).length > 0` |
| `loadAvailableFlows() discovers and parses every deployed flow` (`:106-119`) | each id is in the map; `flow.id === id`; `Array.isArray(flow.nodes)` and `nodes.length > 0`; `Array.isArray(flow.edges)` — **no length or content assertion on edges** |

*What it does not do:* it never calls `validateFlow`, never resolves a `data.skill` against an
installed `SKILL.md`, never reads a `requires:` manifest, never compares a `name:` to a
directory, and never inspects an edge's `type`. `readdirSync(skillsDir).length > 0` is the
entire skill-side assertion — **one non-empty directory**.

*And it usually does not run.* The whole `describe` is `skipIf(!REACHABLE)`, where `REACHABLE`
is `git ls-remote git@github.com:skaile-ai/ai-assets-skaileup.git HEAD` succeeding over SSH
(`:41-54`). In `forge-concept`'s CI the only key loaded into the agent is comment-filtered to
`forge-shared`, so the suite reduces to a trailing marker test asserting
`typeof REACHABLE === "boolean"`. A separate consequence for the port: the repo URL is
**hardcoded in the test file**, so "one repo URL changed" is a `forge-concept` edit, and the
`-mp` variant would need its own reachable SSH access.

---

## Open tensions

*Sharpest form of each live question. No answers here — these are for the conversation.*

1. **The `-mp` skeleton already contains the file ticket 15 condemned.**
   `MP/contracts/flow.schema.json` is byte-identical to the stale 434-line original — the one
   that invents `gate`, invents `review-loop`, requires `position` nothing reads, and would
   reject workspaces' own `metadata:` spelling. Ticket 15 said it "ports narrowed or not at
   all". Is ticket 16 the ticket that executes that, or does the schema go back to ticket 15?
   And if narrowed: does a validator written against a *loose* runtime keep
   `additionalProperties: false` as house discipline, knowing it is the mechanism that will
   reject the next field workspaces adds?

2. **Ticket 15 handed over four cheap checks. `verify_flows.py` implements none of them.**
   Untyped edge (orders nothing), unique node ids, dangling endpoints, self-loops. Only the
   first is *invisible* — the other three are things a sane author does not do. Is the untyped
   edge worth a validator on its own, given that `type` is optional in every schema in play and
   the collection's 153 edges are all typed today by habit? Put differently: is the check
   "every edge has a `type`", or "the flow's dependency graph is connected under
   `type == 'flow'`" — a much stronger and much more useful assertion?

3. **`verify_flows.py` cannot port unedited, and two of the edits are decisions, not chores.**
   Its contract-ref check (#5) reads `skaile.yaml`'s `assets:` block, which `-mp` deliberately
   does not have — so either the check dies or `-mp` grows a manifest it just decided against.
   And its `ALL_FLOWS` is a hardcoded list of 17 ids, its `PHASE_2_PLANNED` a hardcoded set of
   12 skill names, its `deferred_skills.yaml` empty since 2026-05-30 — migration scaffolding.
   With `flows/` deliberately empty (ticket 11), a ported script emits 17 `missing flow file`
   errors on day one. Does the port wait for ticket 10's flow set, or does the script get
   rewritten to glob?

4. **The `requires:` exactness rule is the most valuable thing `verify_flows.py` does, and it
   is entirely ours.** Nothing at runtime reads `requires` for exactness; it drives transitive
   install. It is also the check most likely to catch a real authoring mistake in a
   ~30-skill collection. Does a house rule with no runtime reader earn a validator, when
   ticket 09's whole bar for a contract was "a machine reads it"?

5. **`lint_concept.py`'s model half contradicts the contract it claims to enforce.**
   `golden_principles.md` says the semantic layer is snake_case and that `postxl-schema.json`
   is derived; `check_model`/`check_seed` open `postxl-schema.json` and demand PascalCase
   models, camelCase fields, `Id` suffixes. `model.json` — the file the contract calls
   canonical — is not opened anywhere in the linter. Is the fix to re-point at `model.json`
   (a rewrite of ~200 lines), to drop the model/seed passes and keep only structure +
   frontmatter + cross-refs, or to notice that a **PostXL-shaped check inside a
   template-agnostic collection** is the same category error ticket 06 used to kill the
   `framework` renderer?

6. **`lint_concept.py` validates a target project, not this repo — so what could ever run it?**
   Every other validator here checks the collection's own files and is therefore CI-able.
   `lint_concept.py` needs a `_concept/` that only exists in someone else's repo. Today its
   only "invocations" are two prose lines in an orchestrator skill and a `SOUL.md`, both in
   files `-mp` does not have. Is it a validator at all in `-mp`, or is it the body of an
   `ops-` skill — and if it is a skill, does it stay Python, or does it become the prose
   checklist that a 140-line skill can carry?

7. **The `_concept/` folder shape is still open, and every path in `lint_concept.py` is a bet
   on it.** Ticket 05 deferred the folder list to 07/08; ticket 07 renamed the concept dossier
   to `_concept/dossiers/<feature_slug>/` and renamed *feature group* → **featureset**;
   ticket 08 is still `ready`, not resolved. `check_golden_principles` hard-codes
   `^\d{2}_` on featureset folders and an `experience/screens/00_layout` exemption — the same
   `NN_` scheme ticket 04 deleted from the collection tree. Does `-mp` keep `NN_` inside
   `_concept/`, and is that ticket 08's call or this one's?

8. **`ac_lib.py` does not do the thing that saved its contract.** Ticket 09 kept
   `acceptance_criteria.md` "shrunk to the EARS grammar" on the strength of a machine reader —
   but `ac_lib` contains no EARS check, and the only EARS regex is a copy-pasted one-variant
   pattern in a per-skill validator that misses `WHILE …` and `IF … THEN …`. So either the
   grammar section is prose with no reader (ticket 09's own delete criterion), or the ledger
   structure is the real machine clause and the contract should have been shrunk to *that*
   instead. Which?

9. **`validator_lib.py` is not one file's fate, it is ~20 skills' fate.** The ticket treats it
   as `lint_concept`'s helper. It is actually the runtime for every per-skill `validator.py` —
   and ticket 03's amendment ("a hard guardrail survives as a named failure **with a check
   behind it**") is a promise that something plays this role. `-mp` targets ~30 skills at
   ≤140 lines. Does each of them ship a `validator.py`? If yes, `validator_lib` ports and the
   per-skill validator becomes a standing cost on every skill in the collection. If no,
   ticket 03's "check behind the failure" needs a different mechanism, and `audit.py`'s
   `stage: stable ⇒ validator.py` rule dies with it.

10. **`verify_artifacts.py` is dead, but two checks inside it are not — and they belong to
    different tickets.** The restatement detector (8-gram overlap between a `MUST`/`NEVER`
    line and a contract) is the mechanical form of ticket 09's "citation vs reader"
    distinction, but ticket 03 deleted the `MUST`/`NEVER` lines it scans. The line budget is
    ticket 03's ceiling in code — currently 400, and 7 skills breach it, including
    `mockup-walkthrough-astro` at 1133. `-mp`'s ceiling is 140. Does the budget survive as the
    one thing salvaged from this script, and if so at 140 — a hard fail or a warn?

11. **Hook, Actions, or nothing — and the ecosystem's answer is "nothing" twice.**
    `ai-assets-skill-development` and `ai-assets-skaile-powers` are sibling asset collections
    with **no `.github/` at all**. No repo in the ecosystem has an active git hook, and the
    old repo's hook was never installed in this checkout. Two of the hook's four checks are
    dead and one duplicates `audit.py` verbatim. Is there a reason to carry a hook at all, or
    is "Actions only, when there is something to check" the honest read of the house pattern?

12. **`docs/scripts/audit.py` is the CI job nobody has decided on.** Ticket 16 does not
    mention it; it is the first job in `collection-ci.yml`, it passes 88/88 today, and it lives
    under `docs/` — a tree the map lists as "port, regenerate, or drop, depends on how much
    frontmatter survives". Ticket 01 says only `version`, `artifacts.requires[].id`,
    `prerequisites.*` and `requires` are actually read; `audit.py` gates on `stage` and `tags`,
    which are documentation. Does the frontmatter audit port, shrink to the four read fields,
    or die with the `docs/` question?

13. **Where does a validator live in a flat tree — and does that answer change if there is
    only one?** Ticket 04 hoists to `skills/` · `flows/` · `contracts/` · `docs/` (+ `profiles/`).
    The ticket proposes a `scripts/` root entry. But if the surviving set is one script, a
    root `scripts/` directory is heavier than the thing in it; and if `verify_flows` survives,
    the old repo's own answer was to put it **next to what it validates** (`flows/_meta/`),
    which the flat tree does not obviously forbid. Is `scripts/` a decision about layout, or
    about how many validators are expected to exist a year from now?

14. **The acceptance test is weaker than the map's phrasing, and it may not run at all.**
    `skaileup-flows.test.ts` asserts: flows are in the map, `id` round-trips, `nodes` is
    non-empty, `edges` is an array, and `skillsDir` has ≥1 entry. It resolves no `data.skill`,
    reads no `requires:`, calls no schema. And it self-skips unless
    `git ls-remote git@github.com:skaile-ai/ai-assets-skaileup.git` succeeds — which in
    forge-concept's own CI it almost certainly does not, because the loaded SSH key is
    comment-filtered to `forge-shared`. So the map's "done when flows load green" currently
    cashes out as a locally-run test with five shallow assertions. Does ticket 16 own
    strengthening it (it is a `forge-concept` edit, which this map rules out of scope), or
    does `-mp` need its own validator precisely **because** the acceptance test asserts so
    little?

15. **forge-concept validates nothing, so who is `flow.schema.json` for?**
    Measured this session: `validateFlow`/`FlowManifestSchema` have **zero call sites** in
    forge-concept. Its only gate is `loadFlowsFromDir`'s truthy `id`/`nodes`/`edges`. Platform
    runs the zod schema but never reads `-mp`'s files. So a flow YAML in `-mp` faces **no
    schema enforcement from any host** — which cuts both ways: it means `flow.schema.json` is
    a purely internal authoring discipline (strengthening the case that it should encode
    *our* rules, narrowed, rather than mirror a runtime), and it means its `data.phase` enum
    is the **only** machine check anywhere of ticket 04's every-node-declares-`phase`
    decision. Does that one enum alone justify keeping a schema file?
