---
name: impl-quality-review-feature
description: "Use after a slice is frozen (or before release) to code-review ONE feature end-to-end. Reads the feature spec + acceptance-criteria ledger + frozen slice dossier, scopes the review to the feature's back-linked commits[] and source_files[], applies logic/security/ui-ux checklists with an adversarial evaluator stance, and writes _implementation/review/<feature_slug>.yaml (approve | needs_changes + file:line findings). Triggers on: 'review feature <slug>', 'feature code review', 'code-review the login feature'."
metadata:
  version: "1.0.0"
  tags:
    - impl-quality
    - review
    - code-review
    - per-feature
    - adversarial
    - findings
    - traceability
  stage: alpha
  subagent: true
  artifacts:
    requires:
      - id: features
        gate: hard
    consumes:
      - id: acceptance-criteria
        gate: soft
      - id: slice-impl-index
        gate: soft
      - id: slice-impl-plan
        gate: soft
      - id: slice-impl-recap
        gate: soft
      - id: slice-impl-refactor
        gate: soft
    produces:
      - id: feature-review-result
  prerequisites:
    files:
      - path: "_concept/experience/features"
        gate: hard
        description: "The feature spec is the review contract."
        min_entries: 1
    inputs_required:
      - id: feature_slug
        label: "Kebab-case feature slug to review (== slice_id)"
        type: text
        hint: "Regex ^[a-z][a-z0-9-]{1,47}$. The feature file must carry commits[]/source_files[] back-links."
    produces:
      - path: "_implementation/review/{feature_slug}.yaml"
        description: "Per-feature review verdict + findings with file:line."
---

# impl-quality-review-feature — feature-scoped adversarial code review

## Overview

Reviews ONE feature's shipped code against everything the pipeline knows
about it: the feature spec, its acceptance-criteria ledger, the frozen slice
dossier (plan / recap / refactor), and the exact commits and source files
back-linked into the feature frontmatter by `impl-slice-commit`. Three check
passes (logic, security, ui-ux) reuse the audit checklists. The verdict is
binary: `approve` (no critical/high findings) or `needs_changes` (with
file:line findings and per-finding recommendations).

## When to Use

- After `impl-slice-recap` inside the slice loop (optional flow node), or per feature before release.
- The feature file carries non-empty `commits`/`source_files` back-links.

## When NOT to Use

- Whole-repo static audit — use `impl-quality-audit`.
- Build + test verification — use `impl-quality-eval-code`.
- Spec-vs-running-app verification in the browser — use `ops-eval-feature`.
- The feature has no back-links yet — run `impl-slice-commit` first.

---

ROLE Feature Code Reviewer — adversarially reviews one feature's diff scoped to its back-linked commits and source files; produces `_implementation/review/<feature_slug>.yaml`. Independent evaluator: was NOT the agent that implemented the slice.

READS
  _concept/experience/features/{group}/{feature_slug}.md      — required; spec + back-links (commits, source_files, slice_ref)
  ? _implementation/acceptance_criteria/{group}/{feature_slug}.ac.md — criteria to check the code against
  ? _implementation/slices/{feature_slug}/plan.md              — vertical rows + testing strategy
  ? _implementation/slices/{feature_slug}/recap.md             — files touched, outcome vs plan
  ? _implementation/slices/{feature_slug}/refactor.md          — known accepted debt
  <git show on commits[]>                                      — required at runtime; the diffs under review
  <source_files[] working-tree content>                        — current state of the reviewed files

WRITES
  _implementation/review/{feature_slug}.yaml                   — verdict + findings; the ONLY file this skill writes

REFERENCES
  impl-quality/audit/references/analysis_checklists.md         — logic / ui-ux / security check catalogs (Sub-agent 1-3 sections)
  impl-quality/contracts/evaluate-contract/CONTRACT.md         — evaluator stance (registered as evaluate-contract; if absent, the inline stance below applies)
  contracts/acceptance_criteria.md                             — Criteria Status table format
  contracts/frontmatter.md                                     — feature back-link keys
  contracts/iron_laws.md                                       — § 7, § 9

REQUIRES
  hard: _concept/experience/features/                          — feature spec must exist
  hard: git

# Evaluator stance (inline minimal stance — applies even if evaluate-contract is not installed)

You are an independent, adversarial reviewer. You did NOT write this code.
Assume something is broken and hunt for it. Every finding needs evidence
(file:line + what the spec/AC says vs what the code does). "Looks fine" is
not a review result — either name findings or affirmatively state which
checks each file passed.

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  refuse to run if the feature file is missing, or its commits[] or source_files[] frontmatter is empty — point at impl-slice-commit (the back-link producer)
MUST  scope the review to commits[] diffs + source_files[] contents; files outside that set get at most a one-line boundary note, never findings
MUST  run all three check passes from analysis_checklists.md: Logic & Runtime Errors, Security & Data Integrity, UI/UX & Accessibility
MUST  cross-check the .ac.md when present: any criterion with Status pass whose assertion the code visibly cannot satisfy is a finding (severity ≥ high, ac_ref set)
MUST  give every finding file, line, severity, category, summary, and a concrete recommendation
MUST  set verdict per the pinned rule: approve requires zero critical AND zero high findings; otherwise needs_changes
MUST  write _implementation/review/<feature_slug>.yaml and run validator.py on it before reporting
MUST  on verdict needs_changes, EMIT the debug pointer (see EMIT block) directing the fixer to impl-quality-debug-self-verify, escalating to impl-quality-debug-handoff after two failed fix attempts

NEVER  review as the same agent/context that implemented the slice — dispatch as a sub-agent or fresh context
NEVER  modify any source file, feature file, or dossier — read-only except the review YAML
NEVER  emit verdict approve while any critical or high finding exists
NEVER  pad findings with style nits contradicting the project's discovered standards (_concept/_standards/) — cite the standard if you flag style

INPUT
  Read from: _concept/_grounding/impl-quality-review-feature/input.json
  If missing, ask the user:
  - feature_slug: Feature slug to review (required) default: <none>

# ── Workflow ───────────────────────────────────────────────────────

STEP 0: Resolve + gate
  - Resolve the feature file: $ ls _concept/experience/features/*/<feature_slug>.md
    (fallback: _concept/product-spec/features/*/<feature_slug>.md). Refuse on 0 or >1 match.
  - Parse frontmatter. Refuse (iron_laws § 7) if commits[] or source_files[] is
    empty:
    > "[impl-quality-review-feature] <feature_slug> has no code back-links.
    >  Run impl-slice-commit (STEP 6 back-link) first."
  - Read the .ac.md and slice dossier files when present; note accepted debt
    from refactor.md (do not re-flag it).

STEP 1: Load the diffs
  - For each sha in commits[]: $ git show <sha>
  - Read the current content of every source_files[] entry.
  - Build the review scope = union(diff hunks, current file contents).

STEP 2: Three check passes (analysis_checklists.md)
  - Pass 1 — Logic & Runtime Errors (§ Sub-agent 1): null/undefined handling,
    async/await correctness, state mutations, error propagation, edge values.
  - Pass 2 — Security & Data Integrity (§ Sub-agent 3): injection, authz on
    every route touched, secrets, unsafe deserialization, row-level scoping.
  - Pass 3 — UI/UX & Accessibility (§ Sub-agent 2): states (loading/error/
    empty), keyboard access, labels, contrast-relevant markup.
  - For each hit: record finding {id F-n, severity, category, file, line,
    ac_ref ("" unless tied to a criterion), summary, recommendation}.

STEP 3: Spec + AC cross-check
  - Walk the feature spec's requirements and the .ac.md criteria; for each,
    locate the implementing code in scope. A pass-marked criterion with no
    plausible implementing code → finding (severity high, ac_ref set).

STEP 4: Verdict + write
  - counts := findings tallied by severity.
  - verdict := approve IF counts.critical == 0 AND counts.high == 0 ELSE needs_changes.
  - Write _implementation/review/<feature_slug>.yaml per the pinned schema
    (schema_version 1, feature_slug, feature_path, slice_ref, commits_reviewed,
    files_reviewed, findings, counts, verdict, last_updated).
  - $ python3 impl-quality/review-feature/validator.py _implementation/review/<feature_slug>.yaml
  - On failure: fix the YAML and re-validate; do not report until it exits 0.

STEP 5: Report
  [impl-quality-review-feature] <feature_slug> → <verdict> (<n> findings: <critical>C/<high>H/<medium>M/<low>L)
  IF needs_changes: list findings ordered by severity, each as
  <file>:<line> [<severity>/<category>] <summary> → <recommendation>

EMIT  [impl-quality-review-feature] completed feature=<slug> verdict=<verdict> findings=<n> critical=<n> high=<n>
EMIT  [impl-quality-review-feature] next=impl-quality-debug-self-verify hint="fix findings via the self-verify protocol; escalate to impl-quality-debug-handoff after two failed attempts"   # ONLY when verdict=needs_changes

CHECKLIST
  - [ ] Feature resolved; commits[] + source_files[] non-empty (else refused with impl-slice-commit pointer)
  - [ ] Every commits[] sha inspected via git show; every source_files[] entry read
  - [ ] All three checklist passes executed (logic, security, ui-ux)
  - [ ] .ac.md pass-rows cross-checked against the code (when ledger exists)
  - [ ] Every finding has file:line + severity + category + recommendation
  - [ ] verdict rule enforced (approve ⇒ zero critical/high); validator.py exits 0
  - [ ] needs_changes path emitted the debug-self-verify pointer

---

## Common Mistakes

| Mistake | What to do instead |
|---|---|
| Reviewing the whole repo "while you're in there" | Scope is commits[] + source_files[]; whole-repo review is impl-quality-audit |
| Approving with a high finding "because it's minor" | Downgrade the severity WITH justification, or verdict needs_changes — never both |
| Re-flagging debt already accepted in refactor.md | Read the dossier first; accepted debt is context, not a finding |
| Fixing the code inline | Read-only skill; route fixes through impl-quality-debug-self-verify |
| Running in the implementer's context | Independent evaluator — fresh sub-agent context |
