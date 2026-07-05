---
name: ops-trace
description: "Use before release or after a batch of slices to build the two-way traceability matrix. Direction 1 (feature→code): for every feature spec, asserts frozen slice dossier, non-empty commits/source_files back-links, all acceptance criteria pass, eval-feature approved, docs present; writes _implementation/trace.yaml. Direction 2 (code→feature): git ls-files minus the union of all feature source_files → orphan report (advisory, never deletes). Triggers on: 'trace', 'traceability', 'coverage matrix', 'is every feature shipped', 'orphan code', 'two-way trace'."
metadata:
  version: "1.0.0"
  tags:
    - ops
    - traceability
    - matrix
    - orphans
    - release-gate
    - roll-up
    - read-only
  stage: alpha
  artifacts:
    requires:
      - id: features
        gate: hard
    consumes:
      - id: slice-impl-index
        gate: soft
      - id: acceptance-criteria
        gate: soft
      - id: eval-feature-result
        gate: soft
    produces:
      - id: trace
  prerequisites:
    files:
      - path: "_concept/experience/features"
        gate: hard
        description: "Feature specs are the rows of the trace matrix."
        min_entries: 1
    inputs_optional:
      - id: source_dirs
        label: "Code directories to scan for orphans (comma-separated; default: auto-detect)"
        type: text
      - id: docs_dir
        label: "Docs site directory with _sources frontmatter (default: docs/; skip check if absent)"
        type: text
        default: "docs"
    produces:
      - path: "_implementation/trace.yaml"
        description: "Two-way traceability matrix — per-feature status row + orphan list + overall verdict."
---

# ops-trace — two-way traceability reconciler

## Overview

Rolls the whole traceability chain into one matrix. Direction 1 walks every
feature spec forward: frozen slice dossier → commits → source files →
acceptance-criteria ledger → eval-feature verdict → docs. Direction 2 walks
the code backward: every tracked source file must appear in some feature's
`source_files[]` — leftovers are orphans (advisory; this skill never deletes
anything). The output, `_implementation/trace.yaml`, is the release gate
input for `ops-eval-product`: no feature can be silently unshipped,
untested, unevaluated, or undocumented.

## When to Use

- Before `ops-eval-product` (it hard-gates on `_implementation/trace.yaml`).
- After a batch of slices landed and you want the coverage picture.
- When the user asks "is every feature actually done?" or "what code belongs to no feature?"

## When NOT to Use

- To repair broken `_concept/` cross-references — use `ops-review` / `ops-sync`.
- To evaluate one feature in the browser — use `ops-eval-feature`.
- To review a feature's code — use `impl-quality-review-feature`.

---

ROLE Two-way traceability reconciler — builds `_implementation/trace.yaml` (feature→code matrix + code→feature orphans); read-only except for that one file.

READS
  _concept/experience/features/**/*.md                — required; matrix rows (frontmatter: slice_ref, commits, source_files, screens)
  ? _implementation/slices/*/index.md                 — freeze markers + commit SHAs
  ? _implementation/acceptance_criteria/**/*.ac.md    — Criteria Status tables
  ? _implementation/eval-feature/*.yaml               — per-group verdicts (approved|needs_revision|escalate)
  ? <docs_dir>/**/*.md(x)                             — doc pages with _sources frontmatter (contracts/doc_tracking.md)
  ? <git ls-files>                                    — required at runtime for Direction 2

WRITES
  _implementation/trace.yaml                          — the ONLY file this skill writes

REFERENCES
  contracts/acceptance_criteria.md                    — Criteria Status table format
  contracts/doc_tracking.md                           — _sources schema + excluded patterns
  contracts/feedback_loop.md                          — back-link registration protocol (Task-1 write-back)
  contracts/frontmatter.md                            — feature back-link keys (slice_ref, commits, source_files)
  contracts/iron_laws.md                              — § 7, § 9
  ops/sync/SKILL.md                                   — diff-first advisory reporting style

REQUIRES
  hard: _concept/experience/features/                 — ≥ 1 feature file
  hard: git

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  enumerate EVERY file under _concept/experience/features/**/ as a matrix row — no sampling, no manually-named groups
MUST  key the eval-feature lookup on the feature's <NN_group> directory name (_implementation/eval-feature/<group>.yaml) and record eval_verdict: missing when the file is absent — this closes the silently-un-evaluated gap
MUST  apply the pinned status rules: red = not frozen | commits empty | source_files empty | ac_file missing | any AC fail/untested | eval_verdict needs_revision/escalate; amber = hard checks pass but docs false or eval_verdict missing; green otherwise
MUST  set overall: green iff zero red rows (ambers are surfaced in the report, not blocking)
MUST  compute orphans as: git ls-files under the source dirs, minus the union of all features' source_files, minus doc_tracking excluded patterns (*.test.ts, *.spec.ts, **/__tests__/**, **/node_modules/**, **/dist/**, *.config.*) and _concept/, _implementation/, _debug/, docs/, dotfiles
MUST  present the matrix + orphan list to the user as a table BEFORE writing trace.yaml, with a per-red-row pointer to the repairing skill (impl-slice-commit for missing back-links, impl-plan-plan-vertical for missing .ac.md, impl-slice-test for untested ACs, ops-eval-feature for missing verdicts)
MUST  run validator.py on trace.yaml after writing; on failure report and exit non-zero

NEVER  write to any file other than _implementation/trace.yaml
NEVER  delete or modify orphan files — Direction 2 is advisory only
NEVER  mark a feature green because its checks are "probably fine" — every boolean comes from a file read or git command
NEVER  invent a feature row that has no file under _concept/experience/features/

INPUT
  Read from: _concept/_grounding/ops-trace/input.json
  If missing, ask the user:
  - source_dirs: Code directories to scan for orphans (optional) default: <auto-detect>
  - docs_dir: Docs directory (optional) default: docs

# ── Workflow ───────────────────────────────────────────────────────

STEP 0: Gate + inventory
  - Refuse if _concept/experience/features/ has no *.md files (iron_laws § 7).
  - $ git ls-files
  - Auto-detect source_dirs if not provided: top-level directories from
    git ls-files minus {_concept, _implementation, _debug, docs, e2e-screenshots}
    and dot-directories.

STEP 1: Direction 1 — one row per feature
  For each file F under _concept/experience/features/<NN_group>/*.md:
  - feature_slug := F stem; group := parent dir name.
  - Parse frontmatter: slice_ref, commits, source_files (default ""/[]/[]).
  - frozen := slice_ref non-empty AND <slice_ref>/index.md exists.
  - ac_file := _implementation/acceptance_criteria/<group>/<feature_slug>.ac.md
    if it exists, else "". When present, parse its `## Criteria Status` table →
    ac_counts {pass, fail, untested}.
  - eval_group_file := _implementation/eval-feature/<group>.yaml if it exists,
    else ""; eval_verdict := its `verdict` field, or `missing`.
  - docs := null if <docs_dir> has no pages with `_sources:` frontmatter at all;
    else true when ≥ 1 doc page lists any of this feature's source_files in
    _sources[].path, false otherwise (contracts/doc_tracking.md schema).
  - status := per the pinned status rules (see MUST above).

STEP 2: Direction 2 — orphan scan
  - tracked := union of source_files[] across ALL feature rows.
  - candidates := git ls-files entries under source_dirs.
  - orphans := candidates − tracked − excluded patterns (see MUST above).

STEP 3: Assemble + present (CHECKPOINT trace_report)
  - Build the trace.yaml document per the pinned schema
    (schema_version: 1, generated: today, features, orphans, summary, overall).
  - Show the user: the matrix as a markdown table (slug | frozen | commits |
    ACs | eval | docs | status), the orphan list, and per-red-row repair
    pointers. Advisory only — offer NO auto-fixes.
  CHECKPOINT trace_report
    > "Trace matrix: <green>/<total> green, <amber> amber, <red> red,
    >  <n> orphans. Write _implementation/trace.yaml?"

STEP 4: Write + validate
  - Write _implementation/trace.yaml.
  - $ python3 ops/trace/validator.py _implementation/trace.yaml
  - On failure: report errors and exit non-zero.

EMIT  [ops-trace] completed features=<n> green=<n> amber=<n> red=<n> orphans=<n> overall=<green|red>

CHECKLIST
  - [ ] Every _concept/experience/features/**/*.md has exactly one matrix row
  - [ ] eval-feature lookups keyed on <NN_group> dir names; absent files recorded as eval_verdict: missing
  - [ ] Orphan list computed from git ls-files minus source_files union minus exclusions
  - [ ] Matrix + repair pointers shown to user before writing (CHECKPOINT trace_report)
  - [ ] Only _implementation/trace.yaml written; validator.py exits 0
  - [ ] overall is green iff zero red rows

---

## Common Mistakes

| Mistake | What to do instead |
|---|---|
| Evaluating only the groups the user names | Enumerate every feature file — the whole point is catching silently-skipped features |
| Deleting or "cleaning up" orphan files | Report them; deciding is the user's job (they may be planned work) |
| Marking docs=false red | Docs and missing eval runs are amber (advisory); red is reserved for hard gaps |
| Writing repair edits into _concept/ | This skill is read-only except trace.yaml; point at the owning skill instead |
| Trusting feature frontmatter commits without checking the freeze | frozen requires the slice dossier's index.md to exist |
