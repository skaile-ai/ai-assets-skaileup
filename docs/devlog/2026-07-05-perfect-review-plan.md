# Perfect Review (Two-Way Traceability) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the traceability loop so every feature spec provably maps to frozen slice → commits → source files → per-criterion acceptance results → feature review → release gate, and every source file maps back to a feature (orphan detection).

**Architecture:** Three layers. (1) *Back-links*: `impl-slice-commit` writes `slice_ref`/`commits`/`source_files` into the feature spec's frontmatter on freeze, and `impl-plan-plan-vertical` materializes the already-specced-but-never-built `.ac.md` acceptance-criteria ledger, updated per-criterion by `impl-slice-test` and `impl-quality-test-e2e`. (2) *Reconciler*: a new `ops-trace` skill rolls both directions up into `_implementation/trace.yaml` (feature→code matrix + code→feature orphans) and `ops-eval-product` refuses release unless the matrix is green. (3) *Feature review*: a new `impl-quality-review-feature` skill code-reviews one feature scoped to its back-linked commits/files, producing `_implementation/review/<slug>.yaml`; both new skills get wired into the flows.

**Tech Stack:** markdown skills DSL (`skaileup/contracts/skill_grammar.md`), YAML contracts (`skaileup/contracts/artifacts.yaml`, flow YAMLs), Python validators (stdlib + PyYAML, pattern of `skaileup/12_impl-slice/04_test/validator.py`), pytest.

## Global Constraints

- **Repo root:** `/Users/matthias/.superset/worktrees/4ab1967b-09ee-47d3-b5f3-30d3d0afad59/main` — run ALL commands from here; all paths below are relative to it.
- **Dependency assumption:** this plan assumes `docs/devlog/2026-07-05-skill-dedup-plan.md` (evaluator contract) and `docs/devlog/2026-07-05-flow-restructure-plan.md` (quality-gate sub-flow) landed first. **As of authoring, NEITHER exists in the repo.** Fallbacks (both already baked into the tasks below): (a) Task 6 references the existing `evaluate-contract` (`skaileup/13_impl-quality/contracts/evaluate-contract/CONTRACT.md`, registered in `skaile.yaml`) AND inlines a minimal adversarial stance so the skill is self-sufficient; (b) Task 8 wires `ops-trace` + `impl-quality-review-feature` **directly into `appbuilder-standard` / `appbuilder-complex`** (Variant B). If a `quality-gate` sub-flow exists under `skaileup/flows/quality-gate/` when you execute Task 8, use Variant A instead (documented inside the task).
- **Naming convention:** new skill dirs get the next free `NN_` prefix (`skaileup/14_ops/12_trace/`, `skaileup/13_impl-quality/13_review-feature/`); the frontmatter `name:` is the domain-relative path with every `NN_` prefix stripped and `/`→`-` (so `ops-trace`, `impl-quality-review-feature`).
- **Registry discipline:** every new artifact id goes into `skaileup/contracts/artifacts.yaml` **in the same commit** as the skill frontmatter that declares `produces:` for it — `python3 skaileup/contracts/scripts/verify_artifacts.py` enforces the bidirectional link and must exit 0 after every task.
- **Flow discipline:** every flow edit is two-sided (node + `requires:` skill ref); `python3 skaileup/flows/_meta/verify_flows.py` must exit 0 after every flow-touching task. Baseline before Task 1: both verifiers exit 0.
- **Feature-file path caveat:** the canonical feature tree is `_concept/experience/features/<NN_group>/<feature>.md` (per `artifacts.yaml` id `features`), but `impl-plan-plan-vertical` frontmatter carries `feature_path: _concept/product-spec/features/...` (pre-existing repo inconsistency). All new logic resolves the target as: use `feature_path` verbatim if the file exists, else retry with `product-spec/features` → `experience/features`; if neither exists, warn and skip (never invent a file).
- **Never-clobber:** writes into `_concept/` touch ONLY the named frontmatter keys + `last_updated`, always show a diff first (ops-sync style, `skaileup/14_ops/09_sync/SKILL.md` Step 6/7).
- **Status enums (exact):** `.ac.md` criterion status ∈ `untested | pass | fail`; `trace.yaml` per-feature `status` ∈ `green | amber | red`, `overall` ∈ `green | red` (green iff zero red rows); review `verdict` ∈ `approve | needs_changes`; finding `severity` ∈ `critical | high | medium | low`.
- **Python/pytest:** `python3`, `pytest -q`; validators exit 0 on OK, 2 on failure, print `ERROR: ...` to stderr (house pattern).
- **Commits:** one per task, message given in the task, each ending with the trailer line `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. Stage explicit file lists, never `git add .`.
- **Do not modify** any file not listed in a task's **Files** block.

---

### Task 1: Feature back-links on slice freeze (impl-slice-commit)

**Files:**
- Modify: `skaileup/contracts/frontmatter.md` (feature schema section, ~line 122-153)
- Modify: `skaileup/contracts/feedback_loop.md` (add registration-protocol section)
- Modify: `skaileup/contracts/concept_structure.md` (slices section, ~line 281)
- Modify: `skaileup/contracts/artifacts.yaml` (`features` id `produced_by` list, ~line 163)
- Modify: `skaileup/12_impl-slice/07_commit/SKILL.md`
- Modify: `skaileup/12_impl-slice/07_commit/validator.py` (add Mode D)
- Test: `skaileup/12_impl-slice/07_commit/tests/test_back_link.py` (new)

**Interfaces:**
- Consumes: `recap.md` section `## Files touched` (written by `impl-slice-recap`, bullets `<path> (new|modified|deleted)`); `index.md` frontmatter key `commits: [<sha>, ...]` (written by this same skill in STEP 5); slice frontmatter keys `slice_id`, `feature_title`, `feature_path`.
- Produces: three new frontmatter keys on the feature file — `slice_ref: _implementation/slices/<slice_id>/`, `commits: [<sha>, ...]`, `source_files: [<path>, ...]` — consumed by Tasks 4 (ops-trace) and 6 (review-feature). Validator Mode D CLI: `python3 skaileup/12_impl-slice/07_commit/validator.py --back-link <feature.md> --slice-dir <slice_dir>`.

- [ ] **Step 1: Write the failing test**

Create `skaileup/12_impl-slice/07_commit/tests/test_back_link.py`:

```python
"""Tests for impl-slice-commit validator Mode D (--back-link)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent

_spec = importlib.util.spec_from_file_location(
    "impl_slice_commit_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)

GOOD_FEATURE = """\
---
priority: must-have
roles: [all_users]
story_refs: [onboarding_flow]
screens:
  - path: experience/screens/01_user_auth/login.md
data_entities: [User]
slice_ref: _implementation/slices/login/
commits: [abc1234, deadbeef1234567]
source_files:
  - src/routes/login.ts
  - src/components/LoginForm.tsx
last_updated: 2026-07-05
---

# Login
"""


def make_slice_dir(tmp_path: Path, slice_id: str = "login", frozen: bool = True) -> Path:
    d = tmp_path / "_implementation" / "slices" / slice_id
    d.mkdir(parents=True)
    if frozen:
        (d / "index.md").write_text(
            "---\nslice_id: login\nphase: frozen\nstatus: shipped\n"
            "commits: [abc1234, deadbeef1234567]\nlast_updated: 2026-07-05\n---\n",
            encoding="utf-8",
        )
    return d


def write_feature(tmp_path: Path, text: str) -> Path:
    fdir = tmp_path / "_concept" / "experience" / "features" / "01_user_auth"
    fdir.mkdir(parents=True)
    f = fdir / "login.md"
    f.write_text(text, encoding="utf-8")
    return f


def test_good_back_link_passes(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path)
    feature = write_feature(tmp_path, GOOD_FEATURE)
    errors = validator.validate_back_link(feature, slice_dir)
    assert errors == []


def test_missing_slice_ref_fails(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path)
    feature = write_feature(
        tmp_path, GOOD_FEATURE.replace("slice_ref: _implementation/slices/login/\n", "")
    )
    errors = validator.validate_back_link(feature, slice_dir)
    assert any("slice_ref" in e for e in errors)


def test_empty_commits_fails(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path)
    feature = write_feature(
        tmp_path, GOOD_FEATURE.replace("commits: [abc1234, deadbeef1234567]", "commits: []")
    )
    errors = validator.validate_back_link(feature, slice_dir)
    assert any("commits" in e for e in errors)


def test_non_sha_commit_fails(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path)
    feature = write_feature(
        tmp_path,
        GOOD_FEATURE.replace("commits: [abc1234, deadbeef1234567]", "commits: [not-a-sha!]"),
    )
    errors = validator.validate_back_link(feature, slice_dir)
    assert any("SHA" in e for e in errors)


def test_empty_source_files_fails(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path)
    feature = write_feature(
        tmp_path,
        GOOD_FEATURE.replace(
            "source_files:\n  - src/routes/login.ts\n  - src/components/LoginForm.tsx\n",
            "source_files: []\n",
        ),
    )
    errors = validator.validate_back_link(feature, slice_dir)
    assert any("source_files" in e for e in errors)


def test_unfrozen_slice_fails(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path, frozen=False)
    feature = write_feature(tmp_path, GOOD_FEATURE)
    errors = validator.validate_back_link(feature, slice_dir)
    assert any("index.md" in e for e in errors)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest -q skaileup/12_impl-slice/07_commit/tests/test_back_link.py`
Expected: FAIL / ERROR with `AttributeError: module 'impl_slice_commit_validator' has no attribute 'validate_back_link'`

- [ ] **Step 3: Implement validator Mode D**

In `skaileup/12_impl-slice/07_commit/validator.py`:

3a. Add after the `HANDOFF_FILES` / regex constants block (after line 47):

```python
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
```

3b. Add a new section before `# ── CLI ─...` (after `validate_pre_flight`):

```python
# ── Mode D: feature back-link ─────────────────────────────────────


def validate_back_link(feature_file: Path, slice_dir: Path) -> list[str]:
    """Assert impl-slice-commit STEP 6 wrote slice_ref/commits/source_files
    into the feature spec's frontmatter, and only after the freeze."""
    errors: list[str] = []
    if not feature_file.exists():
        return [f"feature file not found: {feature_file}"]
    try:
        fm, _ = split_frontmatter(feature_file.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"{feature_file}: {exc}"]

    slice_id = slice_dir.name
    expected_ref = f"_implementation/slices/{slice_id}/"
    if fm.get("slice_ref") != expected_ref:
        errors.append(
            f"slice_ref is {fm.get('slice_ref')!r}; expected {expected_ref!r}"
        )

    commits = fm.get("commits")
    if not isinstance(commits, list) or not commits:
        errors.append("'commits' must be a non-empty list of git SHAs")
    else:
        for sha in commits:
            if not isinstance(sha, str) or not SHA_RE.match(sha):
                errors.append(f"commits entry {sha!r} is not a git SHA (7-40 hex chars)")

    source_files = fm.get("source_files")
    if not isinstance(source_files, list) or not source_files:
        errors.append("'source_files' must be a non-empty list of repo-relative paths")

    if not (slice_dir / "index.md").exists():
        errors.append(
            f"{slice_dir / 'index.md'} missing — back-link must be written "
            "AFTER the STEP 5 freeze (index.md is the freeze marker)"
        )
    return errors
```

3c. In `main()`, add to the mutually exclusive group (after the `--pre-flight` line):

```python
    group.add_argument(
        "--back-link",
        help="Mode D: path to the feature .md whose frontmatter should carry the back-link",
    )
```

and add after the existing `--root` argument:

```python
    parser.add_argument(
        "--slice-dir",
        default=None,
        help="(Mode D) path to the frozen _implementation/slices/<id>/ directory",
    )
```

and extend the dispatch chain (after the `elif args.pre_flight:` branch):

```python
    elif args.back_link:
        if not args.slice_dir:
            print("ERROR: --back-link requires --slice-dir", file=sys.stderr)
            return 2
        errors = validate_back_link(Path(args.back_link), Path(args.slice_dir))
```

3d. Update the module docstring usage block: add the line

```
    # Mode D: assert the feature spec carries the back-link (slice_ref/commits/source_files).
    python3 validator.py --back-link <path/to/feature.md> --slice-dir <path/to/_implementation/slices/<id>/>
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest -q skaileup/12_impl-slice/07_commit/tests/`
Expected: all tests PASS (the pre-existing tests in that dir must still pass too).

- [ ] **Step 5: Extend the feature frontmatter contract**

In `skaileup/contracts/frontmatter.md`, in the `## experience/features/\<group\>/\<feature\>.md` section, replace:

```yaml
screens: []                     # populated by screens skill
data_entities: []               # populated by datamodel skill
last_updated: YYYY-MM-DD
---
```

with:

```yaml
screens: []                     # populated by screens skill
data_entities: []               # populated by datamodel skill
slice_ref: ""                   # populated by impl-slice-commit: _implementation/slices/<slice_id>/
commits: []                     # populated by impl-slice-commit: git SHAs that shipped this feature
source_files: []                # populated by impl-slice-commit: code files from recap.md "## Files touched"
last_updated: YYYY-MM-DD
---
```

Then, after the existing `### data_entities[] format (populated by downstream skill)` block, add:

```markdown
### back-link format (populated by impl-slice-commit on freeze)

Forward-built features get code back-links when their slice is frozen —
same shape `ops-reverse-engineer` writes for imported repos:

​```yaml
slice_ref: _implementation/slices/login/
commits: [abc1234, deadbeef1234567]      # 7-40 hex chars each
source_files:
  - src/routes/login.ts
  - src/components/LoginForm.tsx
​```

`ops-trace` (Direction 1) treats an empty `commits`/`source_files` on a
frozen slice's feature as a red trace row.
```

(Remove the zero-width escapes `​` before the inner backticks — they are only here to nest the fence.)

- [ ] **Step 6: Extend feedback_loop.md and concept_structure.md**

6a. In `skaileup/contracts/feedback_loop.md`, insert before `### When a screen is deleted or renamed:`:

```markdown
### When impl-slice-commit freezes a slice:

1. Read `_implementation/slices/<slice_id>/recap.md` `## Files touched`
2. Resolve the feature file from the dossier's `feature_path` (retry
   `product-spec/features` → `experience/features` if the verbatim path is absent)
3. Set `slice_ref: _implementation/slices/<slice_id>/`, `commits:` (landed SHAs),
   `source_files:` (code paths from Files touched, excluding `_concept/`,
   `_implementation/`, and dossier files) in the feature frontmatter
4. Show the frontmatter diff before writing; update `last_updated` on the feature file
```

6b. In `skaileup/contracts/concept_structure.md`, replace the line:

```
The implementation side mirrors this exactly under `_implementation/slices/<slice_id>/`
(`brainstorm · align · plan · test · recap · refactor · index`), frozen by `impl-slice-commit`.
```

with:

```
The implementation side mirrors this exactly under `_implementation/slices/<slice_id>/`
(`brainstorm · align · plan · test · recap · refactor · index`), frozen by `impl-slice-commit`.
On freeze, `impl-slice-commit` also back-links the feature spec: it writes `slice_ref`,
`commits`, and `source_files` into the feature file's frontmatter (diff-first, never
clobbering other keys) so `ops-trace` can walk feature → slice → commits → code.
```

- [ ] **Step 7: Register impl-slice-commit as a features producer**

In `skaileup/contracts/artifacts.yaml`, `features:` entry, replace:

```yaml
    produced_by: [product-spec-features, concept-slice-design-feature, ops-sync, ops-reverse-engineer, ops-add-feature, experience-screens, impl-architecture-datamodel]
```

with:

```yaml
    # impl-slice-commit is a feedback-loop writer: it back-populates
    # slice_ref/commits/source_files frontmatter on freeze.
    produced_by: [product-spec-features, concept-slice-design-feature, ops-sync, ops-reverse-engineer, ops-add-feature, experience-screens, impl-architecture-datamodel, impl-slice-commit]
```

- [ ] **Step 8: Extend impl-slice-commit SKILL.md**

All edits to `skaileup/12_impl-slice/07_commit/SKILL.md`:

8a. Frontmatter — in `metadata.artifacts`, replace:

```yaml
    produces:
      - id: slice-impl-index
```

with:

```yaml
    produces:
      - id: slice-impl-index
      - id: features
```

8b. Frontmatter — in `prerequisites.produces`, after the `index.md` entry, add:

```yaml
      - path: "_concept/experience/features/{group}/{feature_slug}.md"
        description: "Back-link write-back on freeze: slice_ref, commits, source_files frontmatter keys (diff-first)."
```

8c. WRITES block — after the `(FREEZES)` line, add:

```
  <feature file at feature_path>                              — back-link frontmatter ONLY (slice_ref, commits, source_files, last_updated); diff-first
```

8d. Constraints — after the last `MUST` line (`MUST  remove ONLY the transient ...`), add:

```
MUST  back-link the feature spec after a successful freeze: write slice_ref, commits (landed SHAs), source_files (from recap.md "## Files touched") into its frontmatter
MUST  show the feature-file frontmatter diff before writing the back-link (never-clobber; ops-sync style)
MUST  exclude _concept/, _implementation/, and dossier paths from source_files — it lists CODE files only
```

and after the last `NEVER` line, add:

```
NEVER  modify any feature-file frontmatter key other than slice_ref, commits, source_files, last_updated
NEVER  fail the already-landed commits because the back-link target cannot be resolved — warn and skip instead
```

8e. Workflow — after STEP 5 and before the `EMIT` line, insert:

```
STEP 6: Back-link the feature spec (feedback loop)
  Only after STEP 5 succeeded (index.md exists).
  1. Resolve the feature file: use feature_path verbatim if it exists on disk;
     else retry with `product-spec/features` replaced by `experience/features`.
     If neither exists: WARN
     > "[impl-slice-commit] back-link skipped — feature file not found at <feature_path>."
     and continue to EMIT (do NOT fail; commits already landed).
  2. Collect the landed SHAs from STEP 4 ($ git log -N --pretty=%h for the N
     commits just created — same list written into index.md `commits:`).
  3. Parse recap.md "## Files touched"; keep code paths only (drop any path
     under _concept/, _implementation/, _debug/, and deleted files).
  4. Build the frontmatter patch (ONLY these keys):
     slice_ref: _implementation/slices/<slice_id>/
     commits: [<sha>, ...]
     source_files: [<path>, ...]
     last_updated: <today YYYY-MM-DD>
  5. Show the diff of the feature file's frontmatter (before/after) to the user,
     then write. Leave the change in the working tree (it lands with the next
     commit, same convention as index.md).
  6. Verify:
     $ python3 impl-slice/commit/validator.py --back-link <feature file> --slice-dir _implementation/slices/<slice_id>/
     On failure: report errors; do NOT roll back commits.
```

8f. Replace the EMIT line:

```
EMIT  [impl-slice-commit] completed slice_id=<id> commits=<n> frozen=_implementation/slices/<id>/
```

with:

```
EMIT  [impl-slice-commit] completed slice_id=<id> commits=<n> frozen=_implementation/slices/<id>/ back_linked=<feature file|skipped>
```

8g. CHECKLIST — after the `index.md written` item, add:

```
  - [ ] Feature spec back-linked (slice_ref, commits, source_files) or skip warned; validator --back-link exits 0
```

8h. Common Mistakes table — add row:

```
| Skipping the back-link because the feature file lives at a different root | Retry product-spec/features → experience/features before warning; the back-link is what ops-trace walks |
```

- [ ] **Step 9: Verify registry + full test run**

Run: `python3 skaileup/contracts/scripts/verify_artifacts.py`
Expected: last line `... 0 errors ...`, exit 0.
Run: `pytest -q skaileup/12_impl-slice/07_commit/tests/`
Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add skaileup/contracts/frontmatter.md skaileup/contracts/feedback_loop.md skaileup/contracts/concept_structure.md skaileup/contracts/artifacts.yaml skaileup/12_impl-slice/07_commit/SKILL.md skaileup/12_impl-slice/07_commit/validator.py skaileup/12_impl-slice/07_commit/tests/test_back_link.py
git commit -m "feat(impl-slice-commit): back-link feature specs on freeze

Write slice_ref/commits/source_files into the feature file frontmatter
after the lifecycle freeze (diff-first, never-clobber). Adds validator
Mode D (--back-link) + tests; extends frontmatter/feedback-loop/structure
contracts and registers impl-slice-commit as a features producer.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Acceptance-criteria ledger (.ac.md) — contract + producer

**Files:**
- Create: `skaileup/contracts/scripts/ac_lib.py`
- Modify: `skaileup/contracts/acceptance_criteria.md` (add status-table + ownership sections)
- Modify: `skaileup/contracts/artifacts.yaml` (new id `acceptance-criteria`)
- Modify: `skaileup/11_impl-plan/03_plan-vertical/SKILL.md`
- Modify: `skaileup/11_impl-plan/03_plan-vertical/validator.py` (add `--ac` / `--ac-initial`)
- Create: `skaileup/11_impl-plan/03_plan-vertical/examples/team-todo-comments.ac.md` (golden fixture)
- Test: `skaileup/11_impl-plan/03_plan-vertical/tests/test_ac_validator.py` (new)

**Interfaces:**
- Consumes: feature spec EARS lines + `story_refs` (feature frontmatter), align.md `## Acceptance handoff` — same sources plan-vertical already reads.
- Produces: `_implementation/acceptance_criteria/<NN_group>/<feature_slug>.ac.md` with frontmatter keys `feature_ref`, `screen_refs`, `story_refs`, `derived_from`, `last_updated`, per-AC sections `## AC-n:` / `### AC-Bn:`, and a trailing `## Criteria Status` table with header `| ID | Source | Status | Updated by | Date |` (statuses all `untested` at creation). Artifact id `acceptance-criteria`. Shared library function `ac_lib.validate_ac_file(path, require_untested=False) -> list[str]` (used again in Task 3). Validator CLI: `python3 skaileup/11_impl-plan/03_plan-vertical/validator.py <plan.md> --ac <ac.md> --ac-initial`.

- [ ] **Step 1: Write the failing test**

Create `skaileup/11_impl-plan/03_plan-vertical/tests/test_ac_validator.py`:

```python
"""Tests for the acceptance-criteria ledger validation (ac_lib via plan-vertical)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
REPO = SKILL_DIR.parent.parent.parent  # repo root
GOLDEN_AC = SKILL_DIR / "examples" / "team-todo-comments.ac.md"

sys.path.insert(0, str(REPO / "skaileup" / "contracts" / "scripts"))
import ac_lib  # noqa: E402


def test_golden_ac_passes_initial():
    errors = ac_lib.validate_ac_file(GOLDEN_AC, require_untested=True)
    assert errors == []


def test_missing_status_table_fails(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8")
    broken = text.split("## Criteria Status")[0]
    f = tmp_path / "broken.ac.md"
    f.write_text(broken, encoding="utf-8")
    errors = ac_lib.validate_ac_file(f)
    assert any("Criteria Status" in e for e in errors)


def test_bad_status_enum_fails(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace("| untested |", "| maybe |", 1)
    f = tmp_path / "bad.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = ac_lib.validate_ac_file(f)
    assert any("status" in e.lower() for e in errors)


def test_pass_row_rejected_when_initial(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace(
        "| untested | - | - |", "| pass | impl-slice-test | 2026-07-05 |", 1
    )
    f = tmp_path / "not-initial.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = ac_lib.validate_ac_file(f, require_untested=True)
    assert any("untested" in e for e in errors)


def test_row_id_without_section_fails(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace(
        "| AC-2 |", "| AC-9 |", 1
    )
    f = tmp_path / "dangling-row.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = ac_lib.validate_ac_file(f)
    assert any("AC-9" in e for e in errors)


def test_missing_frontmatter_key_fails(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace("story_refs:", "story_refsX:", 1)
    f = tmp_path / "no-story-refs.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = ac_lib.validate_ac_file(f)
    assert any("story_refs" in e for e in errors)
```

- [ ] **Step 2: Create the golden fixture**

Create `skaileup/11_impl-plan/03_plan-vertical/examples/team-todo-comments.ac.md`:

```markdown
---
feature_ref: _concept/experience/features/02_tasks/team-todo-comments.md
screen_refs:
  - _concept/experience/screens/02_tasks/task-detail.md
story_refs: [collaborate_on_task]
derived_from:
  - requirements: 3
  - screen_states: 2
  - behavior_rules: 0
last_updated: 2026-07-05
---

# Acceptance Criteria: Team Todo Comments

## AC-1: Member posts a comment

**Given** a signed-in member viewing a task with 0 comments
**When** they submit "Looks good" in the comment box
**Then** the comment appears in the thread without a page reload

- Assert: thread shows exactly 1 comment with text "Looks good"
- Assert: comment shows the member's display name from seed scenario `populated`

**Test type:** assertion
**Seed scenario:** populated

## AC-2: Empty comment is rejected

**Given** a signed-in member viewing a task
**When** they submit an empty comment
**Then** the form shows exactly "Comment cannot be empty" and no comment is created

- Assert: error text equals "Comment cannot be empty"
- Assert: comment count is unchanged

**Test type:** assertion
**Seed scenario:** populated

## AC-3: User Flow (snapshot)

**Given** a signed-in member on the task list
**When** they open a task, post a comment, and reload
**Then** the comment persists and is visible to another member

**Test type:** snapshot
**Seed scenario:** populated

## Criteria Status

| ID | Source | Status | Updated by | Date |
|---|---|---|---|---|
| AC-1 | collaborate_on_task: WHEN a member submits a comment THE SYSTEM SHALL append it to the task thread | untested | - | - |
| AC-2 | collaborate_on_task: IF the comment is empty THEN THE SYSTEM SHALL reject it with a message | untested | - | - |
| AC-3 | journey snapshot: collaborate_on_task happy path | untested | - | - |
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest -q skaileup/11_impl-plan/03_plan-vertical/tests/test_ac_validator.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'ac_lib'`

- [ ] **Step 4: Implement `ac_lib.py`**

Create `skaileup/contracts/scripts/ac_lib.py`:

```python
#!/usr/bin/env python3
"""ac_lib — shared validation for acceptance-criteria ledgers (.ac.md).

Contract: skaileup/contracts/acceptance_criteria.md (§ AC File Format and
§ Criteria Status Table). Used by the impl-plan-plan-vertical validator
(creation, all rows untested) and the impl-slice-test validator (updates).
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REQUIRED_FRONTMATTER_KEYS = {
    "feature_ref",
    "screen_refs",
    "story_refs",
    "derived_from",
    "last_updated",
}

ALLOWED_STATUSES = {"untested", "pass", "fail"}
AC_HEADING_RE = re.compile(r"^#{2,3} (AC-B?\d+)\b", re.MULTILINE)
STATUS_HEADER_RE = re.compile(
    r"^\|\s*ID\s*\|\s*Source\s*\|\s*Status\s*\|\s*Updated by\s*\|\s*Date\s*\|",
    re.MULTILINE,
)


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("File does not start with YAML frontmatter (---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Could not parse frontmatter — need two `---` lines")
    return yaml.safe_load(parts[1]) or {}, parts[2]


def parse_status_rows(body: str) -> list[list[str]]:
    """Return data rows of the `## Criteria Status` table as cell lists
    [ID, Source, Status, Updated by, Date]."""
    section = body.split("## Criteria Status", 1)
    if len(section) < 2:
        return []
    rows: list[list[str]] = []
    saw_header = saw_align = False
    for raw in section[1].splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        if not saw_header:
            if STATUS_HEADER_RE.match(line):
                saw_header = True
            continue
        if not saw_align:
            if re.match(r"^\|\s*[-:]+\s*(\|\s*[-:]+\s*)+\|?$", line):
                saw_align = True
                continue
            saw_align = True
        rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


def validate_ac_file(path: Path, require_untested: bool = False) -> list[str]:
    errors: list[str] = []
    path = Path(path)
    if not path.exists():
        return [f"file not found: {path}"]
    try:
        fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [str(exc)]

    missing = REQUIRED_FRONTMATTER_KEYS - set(fm)
    if missing:
        errors.append(f"missing frontmatter keys: {sorted(missing)}")

    heading_ids = AC_HEADING_RE.findall(body)
    if not heading_ids:
        errors.append("no `## AC-n:` criterion sections found (≥ 1 required)")

    if "## Criteria Status" not in body:
        errors.append("missing `## Criteria Status` section")
        return errors

    rows = parse_status_rows(body)
    if not rows:
        errors.append(
            "`## Criteria Status` must contain a table with header "
            "`| ID | Source | Status | Updated by | Date |` and ≥ 1 data row"
        )
        return errors

    row_ids: list[str] = []
    for row in rows:
        if len(row) < 5:
            errors.append(f"status row has fewer than 5 cells: {row}")
            continue
        rid, source, status, updated_by, date = row[0], row[1], row[2], row[3], row[4]
        row_ids.append(rid)
        if status not in ALLOWED_STATUSES:
            errors.append(
                f"{rid}: status {status!r} not in {sorted(ALLOWED_STATUSES)}"
            )
        if not source or source == "-":
            errors.append(f"{rid}: Source cell must cite the EARS line / story-id")
        if require_untested and status != "untested":
            errors.append(
                f"{rid}: status must be 'untested' at creation, got {status!r}"
            )
        if status != "untested" and (updated_by == "-" or date == "-"):
            errors.append(
                f"{rid}: non-untested rows must fill 'Updated by' and 'Date'"
            )

    for rid in row_ids:
        if rid not in heading_ids:
            errors.append(f"status row {rid} has no matching `## {rid}:` section")
    for hid in heading_ids:
        if hid not in row_ids:
            errors.append(f"criterion section {hid} has no status row")

    return errors
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest -q skaileup/11_impl-plan/03_plan-vertical/tests/test_ac_validator.py`
Expected: 6 passed.

- [ ] **Step 6: Wire `--ac` into the plan-vertical validator**

In `skaileup/11_impl-plan/03_plan-vertical/validator.py`:

6a. After the `import yaml` line, add:

```python
_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "contracts" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import ac_lib  # noqa: E402
```

(`__file__` is `skaileup/11_impl-plan/03_plan-vertical/validator.py`, so `.parent.parent.parent` is `skaileup/` — the contracts scripts dir resolves to `skaileup/contracts/scripts`.)

6b. Replace the whole `main()` function with:

```python
def main(argv: list[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to _implementation/slices/<id>/plan.md")
    parser.add_argument(
        "--ac", default=None,
        help="also validate the acceptance-criteria ledger (.ac.md) at this path",
    )
    parser.add_argument(
        "--ac-initial", action="store_true",
        help="(with --ac) require every Criteria Status row to be 'untested'",
    )
    args = parser.parse_args(argv[1:])

    errors, warnings = validate(Path(args.path))
    if args.ac:
        errors.extend(
            f"[ac] {e}"
            for e in ac_lib.validate_ac_file(Path(args.ac), require_untested=args.ac_initial)
        )
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print("OK")
    return 0
```

- [ ] **Step 7: Sanity-run the extended validator against the golden fixtures**

Run: `python3 skaileup/11_impl-plan/03_plan-vertical/validator.py skaileup/11_impl-plan/03_plan-vertical/examples/team-todo-comments-plan.md --ac skaileup/11_impl-plan/03_plan-vertical/examples/team-todo-comments.ac.md --ac-initial`
Expected: `OK`, exit 0. (If the plan fixture lives at a different name, `ls skaileup/11_impl-plan/03_plan-vertical/examples/` and use the existing `*-plan.md` golden.)
Also confirm nothing pre-existing broke: `pytest -q skaileup/11_impl-plan/03_plan-vertical/tests/`
Expected: all PASS.

- [ ] **Step 8: Extend contracts/acceptance_criteria.md**

8a. In the `## AC File Format` fenced example, replace the frontmatter lines:

```markdown
feature_ref: _concept/experience/features/<group>/<feature>.md
screen_refs:
  - _concept/experience/screens/<group>/<screen>.md
```

with:

```markdown
feature_ref: _concept/experience/features/<group>/<feature>.md
screen_refs:
  - _concept/experience/screens/<group>/<screen>.md
story_refs: []        # journey ids copied from the feature frontmatter
```

8b. Append at the end of the file:

```markdown
---

## Criteria Status Table (tracking spine)

Every `.ac.md` ends with a `## Criteria Status` section containing one row per
criterion (frontend `AC-n` and backend `AC-Bn` alike):

​```markdown
## Criteria Status

| ID | Source | Status | Updated by | Date |
|---|---|---|---|---|
| AC-1 | <story-id>: <EARS line copied verbatim> | untested | - | - |
| AC-B1 | <story-id or feature §>: <EARS line / rule> | untested | - | - |
​```

- `Status` ∈ `untested | pass | fail`. Rows are created `untested`.
- `Source` cites the EARS line + story-id the criterion was derived from —
  this is the story → AC traceability edge.
- Non-`untested` rows must fill `Updated by` (skill name) and `Date` (ISO).

### Ownership

| Skill | Responsibility |
|---|---|
| `impl-plan-plan-vertical` | Creates the file at `_implementation/acceptance_criteria/<group>/<feature>.ac.md`; every row `untested` |
| `impl-slice-test` | Flips rows exercised by the slice gate to `pass`/`fail` (only rows backed by a `[PASS]`/`[FAIL]`-tagged check) |
| `impl-quality-test-e2e` | Flips journey/snapshot rows on end-to-end journey pass/fail |
| `ops-trace` | Reads the table; any `fail`/`untested` row makes the feature's trace row red |

Validation: `skaileup/contracts/scripts/ac_lib.py` (`validate_ac_file`).
```

(Remove the zero-width escapes `​` before the inner backticks.)

- [ ] **Step 9: Register the artifact id**

In `skaileup/contracts/artifacts.yaml`, insert after the `test-plan:` entry (keep the `# ── implementation — durable ledgers` grouping):

```yaml
  acceptance-criteria:
    path: _implementation/acceptance_criteria/        # <NN_group>/<feature>.ac.md
    kind: durable
    side: impl
    produced_by: [impl-plan-plan-vertical, impl-slice-test, impl-quality-test-e2e]
    description: Per-feature acceptance-criteria ledger — EARS-derived ACs + per-criterion status (untested|pass|fail).
```

(Tasks 2 and 3 both edit skills named here; `verify_artifacts.py` only errors when a `produced_by` skill exists but lacks the `produces` declaration — Step 10 adds plan-vertical's now; Task 3 adds the other two. If `verify_artifacts.py` errors on the not-yet-updated skills at the end of this task, move ONLY the `impl-slice-test`/`impl-quality-test-e2e` names from this list into Task 3 Step 1 instead.)

- [ ] **Step 10: Extend impl-plan-plan-vertical SKILL.md**

All edits to `skaileup/11_impl-plan/03_plan-vertical/SKILL.md`:

10a. Frontmatter `metadata.artifacts` — replace:

```yaml
    produces:
      - id: slice-impl-plan
```

with:

```yaml
    produces:
      - id: slice-impl-plan
      - id: acceptance-criteria
```

10b. Frontmatter `prerequisites.produces` — after the existing plan.md entry, add:

```yaml
      - path: "_implementation/acceptance_criteria/{group}/{feature_slug}.ac.md"
        description: "Acceptance-criteria ledger — one row per EARS-derived criterion, status untested."
```

10c. WRITES block — replace:

```
WRITES
  _implementation/slices/{slice_id}/plan.md                                  — handoff for impl-slice/implement (Task 2D)
```

with:

```
WRITES
  _implementation/slices/{slice_id}/plan.md                                  — handoff for impl-slice/implement (Task 2D)
  _implementation/acceptance_criteria/{group}/{feature_slug}.ac.md           — AC ledger (contracts/acceptance_criteria.md); all rows untested
```

10d. REFERENCES block — add the line:

```
  contracts/acceptance_criteria.md                                — .ac.md format + Criteria Status table (this skill creates it)
```

10e. Constraints — after `MUST  write to _implementation/slices/<slice_id>/plan.md ...`, add:

```
MUST  write _implementation/acceptance_criteria/<group>/<feature_slug>.ac.md per contracts/acceptance_criteria.md — one criterion row per EARS line (with its story-id in the Source cell), every Status cell `untested`
MUST  derive <group> from the resolved feature_path's parent directory name (e.g. 01_user_auth)
```

and after the last `NEVER` line, add:

```
NEVER  create an .ac.md row whose Source does not cite an EARS line or story-id
NEVER  overwrite an existing .ac.md that has non-untested rows — re-entry shows a diff and asks before touching it
```

10f. Workflow — insert between `STEP 8: Write the handoff` and `STEP 9: Validate`, and renumber the old STEP 9 to STEP 10:

```
STEP 9: Write the acceptance-criteria ledger
  - group := parent directory name of the resolved feature file (e.g. 01_user_auth).
  - $ mkdir -p _implementation/acceptance_criteria/<group>/
  - IF _implementation/acceptance_criteria/<group>/<feature_slug>.ac.md exists
      with any non-untested Status row: show a diff of proposed changes and
      ask before writing (re-entry; never silently reset pass/fail history).
  - Compose per contracts/acceptance_criteria.md:
    - frontmatter: feature_ref (resolved feature path), screen_refs (the screen
      files read in STEP 2), story_refs (copied from feature frontmatter),
      derived_from counts, last_updated (today).
    - one `## AC-n:` section per EARS line used in STEP 5 (Given/When/Then +
      asserts + Test type + Seed scenario); backend rules become `### AC-Bn:`
      sections under `## Backend Acceptance Criteria` when present.
    - trailing `## Criteria Status` table: one row per AC-n/AC-Bn with
      `| <ID> | <story-id>: <EARS line verbatim> | untested | - | - |`.
  - Write the file.

STEP 10: Validate
  - $ python3 impl-plan/plan-vertical/validator.py _implementation/slices/<slice_id>/plan.md \
        --ac _implementation/acceptance_criteria/<group>/<feature_slug>.ac.md --ac-initial
  - On failure: report the validator errors and STOP. Do not commit.
  - Empty UI/Logic/Data cells produce a WARNING (stderr), not a failure;
    surface the warning to the user.
```

(Delete the old `STEP 9: Validate` block — its content is folded into STEP 10 above with the extended command.)

10g. Replace the EMIT line with:

```
EMIT  [impl-plan-plan-vertical] completed slice_id=<id> tier=<tier> rows=<n> tests=<n> ac_criteria=<n>
```

10h. CHECKLIST — after the final item, add:

```
  - [ ] _implementation/acceptance_criteria/<group>/<feature_slug>.ac.md written; every Status row `untested`; validator --ac --ac-initial exits 0
```

- [ ] **Step 11: Verify registry**

Run: `python3 skaileup/contracts/scripts/verify_artifacts.py`
Expected: `0 errors`, exit 0 (see Step 9 note if it flags the two Task-3 skills).

- [ ] **Step 12: Commit**

```bash
git add skaileup/contracts/scripts/ac_lib.py skaileup/contracts/acceptance_criteria.md skaileup/contracts/artifacts.yaml skaileup/11_impl-plan/03_plan-vertical/SKILL.md skaileup/11_impl-plan/03_plan-vertical/validator.py skaileup/11_impl-plan/03_plan-vertical/examples/team-todo-comments.ac.md skaileup/11_impl-plan/03_plan-vertical/tests/test_ac_validator.py
git commit -m "feat(impl-plan): produce acceptance-criteria ledger (.ac.md)

Builds the unbuilt spine specced in contracts/acceptance_criteria.md:
plan-vertical now writes _implementation/acceptance_criteria/<group>/
<feature>.ac.md with a Criteria Status table (all untested). Adds shared
ac_lib.py validation, registers artifact id acceptance-criteria, extends
the plan-vertical validator with --ac/--ac-initial + tests.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Per-criterion status updates (impl-slice-test + impl-quality-test-e2e)

**Files:**
- Modify: `skaileup/12_impl-slice/04_test/SKILL.md`
- Modify: `skaileup/12_impl-slice/04_test/validator.py` (add `--ac`)
- Modify: `skaileup/13_impl-quality/06_test-e2e/SKILL.md`
- Test: `skaileup/12_impl-slice/04_test/tests/test_ac_update.py` (new)

**Interfaces:**
- Consumes: `.ac.md` `## Criteria Status` table (Task 2 shape, `ac_lib.validate_ac_file`); `feature_path` from `plan.md` frontmatter (to derive `<group>/<feature_slug>.ac.md`); test.md `[PASS|FAIL]` tags.
- Produces: updated Status rows `| AC-n | ... | pass|fail | impl-slice-test | YYYY-MM-DD |` and (e2e) `| ... | impl-quality-test-e2e | ... |`. Both skills declare `produces: - id: acceptance-criteria` (registry already lists them from Task 2 Step 9).

- [ ] **Step 1: Write the failing test**

Create `skaileup/12_impl-slice/04_test/tests/test_ac_update.py`:

```python
"""Tests for impl-slice-test validator --ac cross-check."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
GOLDEN_AC = (
    SKILL_DIR.parent.parent
    / "11_impl-plan"
    / "03_plan-vertical"
    / "examples"
    / "team-todo-comments.ac.md"
)

_spec = importlib.util.spec_from_file_location(
    "impl_slice_test_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def test_validate_ac_updates_accepts_updated_ledger(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace(
        "| untested | - | - |", "| pass | impl-slice-test | 2026-07-05 |", 1
    )
    f = tmp_path / "updated.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = validator.validate_ac_updates(f)
    assert errors == []


def test_validate_ac_updates_rejects_bad_updater(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace(
        "| untested | - | - |", "| pass | someone | 2026-07-05 |", 1
    )
    f = tmp_path / "bad-updater.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = validator.validate_ac_updates(f)
    assert any("Updated by" in e for e in errors)


def test_validate_ac_updates_rejects_structurally_broken(tmp_path: Path):
    f = tmp_path / "broken.ac.md"
    f.write_text("---\nfeature_ref: x\n---\nno table here\n", encoding="utf-8")
    errors = validator.validate_ac_updates(f)
    assert errors  # structural errors from ac_lib bubble up


def test_cli_accepts_ac_flag(tmp_path: Path):
    """--ac wired into the CLI (exit 2 on a broken ledger, error mentions [ac])."""
    ac = tmp_path / "broken.ac.md"
    ac.write_text("---\nfeature_ref: x\n---\nno table\n", encoding="utf-8")
    done = SKILL_DIR / "examples" / "team-todo-comments-test-done.md"
    slug_dir = tmp_path / "team-todo-comments"
    slug_dir.mkdir()
    target = slug_dir / "test.md"
    target.write_text(done.read_text(encoding="utf-8"), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SKILL_DIR / "validator.py"), str(target), "--ac", str(ac)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 2
    assert "[ac]" in proc.stderr
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest -q skaileup/12_impl-slice/04_test/tests/test_ac_update.py`
Expected: FAIL with `AttributeError: ... has no attribute 'validate_ac_updates'`

- [ ] **Step 3: Implement `--ac` in the impl-slice-test validator**

In `skaileup/12_impl-slice/04_test/validator.py`:

3a. After `import yaml`, add:

```python
_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "contracts" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import ac_lib  # noqa: E402
```

(`.parent.parent.parent` from `skaileup/12_impl-slice/04_test/validator.py` is `skaileup/`.)

3b. Add before `def main(...)`:

```python
AC_UPDATERS = {"impl-slice-test", "impl-quality-test-e2e"}


def validate_ac_updates(ac_path: Path) -> list[str]:
    """Structural ac_lib checks + updated rows must name a known updater skill."""
    errors = [f"[ac] {e}" for e in ac_lib.validate_ac_file(ac_path)]
    if errors:
        return errors
    _, body = ac_lib.split_frontmatter(ac_path.read_text(encoding="utf-8"))
    for row in ac_lib.parse_status_rows(body):
        if len(row) < 5:
            continue
        rid, status, updated_by = row[0], row[2], row[3]
        if status != "untested" and updated_by not in AC_UPDATERS:
            errors.append(
                f"[ac] {rid}: 'Updated by' is {updated_by!r}; must be one of "
                f"{sorted(AC_UPDATERS)}"
            )
    return errors
```

3c. In `main()`, add after `parser.add_argument("--plan", default=None)`:

```python
    parser.add_argument("--ac", default=None)
```

and after `errors, warnings = validate(Path(args.path), plan_path)`:

```python
    if args.ac:
        errors = errors + validate_ac_updates(Path(args.ac))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest -q skaileup/12_impl-slice/04_test/tests/`
Expected: all PASS (new file + pre-existing `test_impl_slice_test_validator.py`).

- [ ] **Step 5: Extend impl-slice-test SKILL.md**

All edits to `skaileup/12_impl-slice/04_test/SKILL.md`:

5a. Frontmatter `metadata.artifacts` — replace:

```yaml
    produces:
      - id: slice-impl-test
```

with:

```yaml
    produces:
      - id: slice-impl-test
      - id: acceptance-criteria
```

5b. READS block — add after the `? pyproject.toml` line:

```
  ? _implementation/acceptance_criteria/{group}/{slice_id}.ac.md — AC ledger; statuses updated in STEP 7
```

5c. WRITES block — replace:

```
WRITES
  _implementation/slices/{slice_id}/test.md                              — handoff for impl-slice-recap
```

with:

```
WRITES
  _implementation/slices/{slice_id}/test.md                              — handoff for impl-slice-recap
  _implementation/acceptance_criteria/{group}/{slice_id}.ac.md           — Status rows flipped pass/fail for criteria this gate exercised
```

5d. REFERENCES block — add:

```
  contracts/acceptance_criteria.md                            — Criteria Status table + ownership rules
```

5e. Constraints — after the last `MUST` line, add:

```
MUST  update the AC ledger after writing test.md: flip a Criteria Status row to pass/fail ONLY when a [PASS]/[FAIL]-tagged check in this test.md covers that criterion's Source EARS line; stamp `impl-slice-test` + today's date
MUST  leave rows this slice did not exercise as-is (untested rows stay untested)
```

and after the last `NEVER` line:

```
NEVER  flip an AC row to pass without a matching [PASS]-tagged manual check or automated test in this test.md
```

5f. Workflow — insert between `STEP 6: Write the handoff` and `STEP 7: Validate`, renumbering old STEP 7 to STEP 8:

```
STEP 7: Update the acceptance-criteria ledger
  - Derive the ledger path: <group> and <feature_slug> from the plan.md
    frontmatter feature_path's last two segments →
    _implementation/acceptance_criteria/<group>/<feature_slug>.ac.md.
  - IF the ledger is missing: WARN
    > "[impl-slice-test] AC ledger missing — run impl-plan-plan-vertical
    >  (it creates the .ac.md) before relying on trace."
    and skip to STEP 8.
  - For each row in `## Criteria Status`: if a [PASS]-tagged bullet in this
    test.md covers the row's Source EARS line (the plan.md automated tests
    were copied from the same EARS lines — match on the EARS text), set
    Status=pass; if a [FAIL]-tagged bullet covers it, set Status=fail.
    In both cases set `Updated by` = impl-slice-test and `Date` = today.
  - Do not touch rows with no matching bullet. Update frontmatter last_updated.

STEP 8: Validate
  - $ python3 impl-slice/test/validator.py _implementation/slices/<slice_id>/test.md \
        --plan _implementation/slices/<slice_id>/plan.md \
        --ac _implementation/acceptance_criteria/<group>/<feature_slug>.ac.md
  - (Omit --ac if the ledger was missing in STEP 7.)
  - On failure: report errors and STOP. Do not advance.
```

(Delete the old `STEP 7: Validate` block — folded into STEP 8 above.)

5g. Replace the EMIT line with:

```
EMIT  [impl-slice-test] completed slice_id=<id> decision=<value> blockers=<n> ac_updated=<n>
```

5h. CHECKLIST — add as final item:

```
  - [ ] AC ledger rows flipped for exercised criteria (or missing-ledger warning surfaced); validator --ac exits 0
```

- [ ] **Step 6: Extend impl-quality-test-e2e SKILL.md**

All edits to `skaileup/13_impl-quality/06_test-e2e/SKILL.md`:

6a. Frontmatter `metadata.artifacts` — replace:

```yaml
    produces:
      - id: e2e-report
      - id: e2e-screenshots
```

with:

```yaml
    produces:
      - id: e2e-report
      - id: e2e-screenshots
      - id: acceptance-criteria
```

6b. WRITES block — replace:

```
WRITES
e2e-screenshots/\*_/_.png — per-journey step screenshots
? e2e-test-report.md — optional full markdown report
```

with:

```
WRITES
e2e-screenshots/\*_/_.png — per-journey step screenshots
? e2e-test-report.md — optional full markdown report
? \_implementation/acceptance_criteria/\*\*/\*.ac.md — journey/snapshot Status rows flipped pass/fail per journey outcome
```

6c. MUST block — after `MUST update last_updated on feature files for every passing journey`, add:

```
MUST update the AC ledgers for journeys run: for each feature covered by a journey, flip its .ac.md snapshot/journey rows (and any AC row whose Source EARS line was evaluated) to pass/fail; stamp `impl-quality-test-e2e` + today's date
```

6d. STEP 7 — replace the step body:

```
STEP 7: Update feature tracking (feedback loop)

- For every successfully tested journey:
  - Find corresponding feature in \_concept/experience/features/
  - Update last_updated in frontmatter to today's date
```

with:

```
STEP 7: Update feature tracking (feedback loop)

- For every successfully tested journey:
  - Find corresponding feature in \_concept/experience/features/
  - Update last_updated in frontmatter to today's date
- For every journey run (pass or fail):
  - Resolve \_implementation/acceptance_criteria/<group>/<feature_slug>.ac.md
    for each feature the journey covers (group/slug from the feature path;
    skip with a warning if the ledger does not exist)
  - Flip the Criteria Status rows whose Source EARS line the journey
    evaluated: pass if all its criteria held, fail on the failing criterion
  - Stamp `Updated by: impl-quality-test-e2e`, `Date: <today>`; never touch
    rows the journey did not evaluate
```

6e. CHECKLIST — after `- [ ] Feature last_updated updated via feedback loop for passing journeys`, add:

```
- [ ] AC ledgers updated for every journey run (pass/fail rows stamped impl-quality-test-e2e)
```

- [ ] **Step 7: Verify registry + run all touched tests**

Run: `python3 skaileup/contracts/scripts/verify_artifacts.py`
Expected: `0 errors, 0 warnings` (all three `acceptance-criteria` producers now declare `produces`).
Run: `pytest -q skaileup/12_impl-slice/04_test/tests/ skaileup/11_impl-plan/03_plan-vertical/tests/`
Expected: all PASS.

- [ ] **Step 8: Commit**

```bash
git add skaileup/12_impl-slice/04_test/SKILL.md skaileup/12_impl-slice/04_test/validator.py skaileup/12_impl-slice/04_test/tests/test_ac_update.py skaileup/13_impl-quality/06_test-e2e/SKILL.md
git commit -m "feat(quality): per-criterion AC status updates

impl-slice-test flips .ac.md Criteria Status rows it exercises (PASS/FAIL
tagged checks only); impl-quality-test-e2e flips journey/snapshot rows on
journey outcomes. Adds --ac cross-check to the slice-test validator.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: `ops-trace` — two-way reconciler skill

**Files:**
- Create: `skaileup/14_ops/12_trace/SKILL.md`
- Create: `skaileup/14_ops/12_trace/validator.py`
- Create: `skaileup/14_ops/12_trace/tests/test_ops_trace_validator.py`
- Create: `skaileup/14_ops/12_trace/tests/fixtures/trace_green.yaml`
- Modify: `skaileup/contracts/artifacts.yaml` (new id `trace`)
- Modify: `skaileup/14_ops/DOMAIN.md` (skill row + sequence)

**Interfaces:**
- Consumes: feature frontmatter `slice_ref`/`commits`/`source_files` (Task 1), `.ac.md` Criteria Status (Tasks 2-3), `_implementation/slices/<id>/index.md` (freeze marker), `_implementation/eval-feature/<group>.yaml` key `verdict` ∈ `approved|needs_revision|escalate` (existing ops-eval-feature output), doc pages' `_sources[].path` (contracts/doc_tracking.md), `git ls-files`.
- Produces: `_implementation/trace.yaml` (schema below — consumed by Task 5's eval-product gate), artifact id `trace`, skill name `ops-trace`. Validator CLI: `python3 skaileup/14_ops/12_trace/validator.py <path/to/trace.yaml>`.

**Pinned `trace.yaml` schema** (the plan's single source of truth — validator and SKILL.md both encode exactly this):

```yaml
schema_version: 1
generated: "2026-07-05"            # ISO date
features:                          # one row per file under _concept/experience/features/**/
  - feature_path: _concept/experience/features/01_user_auth/login.md
    feature_slug: login
    group: 01_user_auth
    slice_ref: _implementation/slices/login/   # "" when missing
    frozen: true                   # slice_ref dir exists AND contains index.md
    commits: [abc1234]             # copied from feature frontmatter; [] when missing
    source_files_count: 7          # len(feature frontmatter source_files)
    ac_file: _implementation/acceptance_criteria/01_user_auth/login.ac.md  # "" when missing
    ac_counts: {pass: 6, fail: 0, untested: 0}
    eval_group_file: _implementation/eval-feature/01_user_auth.yaml        # "" when missing
    eval_verdict: approved         # approved | needs_revision | escalate | missing
    docs: true                     # true | false | null (null = no docs site to check)
    status: green                  # green | amber | red
orphans:                           # Direction 2 — advisory only
  - src/utils/legacy.ts
summary:
  features_total: 12
  green: 11
  amber: 1
  red: 0
  orphans_count: 1
overall: green                     # green | red — green iff summary.red == 0
```

Status rules (hard vs advisory): **red** if any of — not `frozen`, `commits` empty, `source_files_count == 0`, `ac_file` missing, any `ac_counts.fail > 0` or `ac_counts.untested > 0`, or `eval_verdict` ∈ `needs_revision|escalate`. **amber** if all hard checks pass but `docs` is `false`, or `eval_verdict == missing` (eval-feature never ran for the group). **green** otherwise. `overall: green` iff `summary.red == 0` (ambers are surfaced, not blocking).

- [ ] **Step 1: Write the failing test + green fixture**

Create `skaileup/14_ops/12_trace/tests/fixtures/trace_green.yaml` with EXACTLY the pinned-schema example above (copy the fenced block verbatim, keeping `overall: green`, `red: 0`).

Create `skaileup/14_ops/12_trace/tests/test_ops_trace_validator.py`:

```python
"""Tests for the ops-trace validator (trace.yaml schema)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
GREEN = THIS_DIR / "fixtures" / "trace_green.yaml"

_spec = importlib.util.spec_from_file_location(
    "ops_trace_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def mutate(tmp_path: Path, transform) -> Path:
    data = yaml.safe_load(GREEN.read_text(encoding="utf-8"))
    transform(data)
    f = tmp_path / "trace.yaml"
    f.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return f


def test_green_fixture_passes():
    assert validator.validate(GREEN) == []


def test_missing_top_key_fails(tmp_path: Path):
    f = mutate(tmp_path, lambda d: d.pop("summary"))
    assert any("summary" in e for e in validator.validate(f))


def test_bad_status_enum_fails(tmp_path: Path):
    def t(d):
        d["features"][0]["status"] = "blue"
    f = mutate(tmp_path, t)
    assert any("status" in e for e in validator.validate(f))


def test_overall_green_with_red_rows_fails(tmp_path: Path):
    def t(d):
        d["features"][0]["status"] = "red"
        d["summary"]["red"] = 1
        d["summary"]["green"] = d["summary"]["green"] - 1
        # overall left green — inconsistent on purpose
    f = mutate(tmp_path, t)
    assert any("overall" in e for e in validator.validate(f))


def test_summary_count_mismatch_fails(tmp_path: Path):
    def t(d):
        d["summary"]["features_total"] = 99
    f = mutate(tmp_path, t)
    assert any("features_total" in e for e in validator.validate(f))


def test_bad_verdict_enum_fails(tmp_path: Path):
    def t(d):
        d["features"][0]["eval_verdict"] = "maybe"
    f = mutate(tmp_path, t)
    assert any("eval_verdict" in e for e in validator.validate(f))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest -q skaileup/14_ops/12_trace/tests/`
Expected: FAIL with `FileNotFoundError` (no `validator.py` yet).

- [ ] **Step 3: Implement the validator**

Create `skaileup/14_ops/12_trace/validator.py`:

```python
#!/usr/bin/env python3
"""Validator for ops-trace output (`_implementation/trace.yaml`).

Usage:
    python3 validator.py <path/to/trace.yaml>

Exit codes:
    0 — valid
    2 — validation failure (errors printed to stderr)
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REQUIRED_TOP_KEYS = {"schema_version", "generated", "features", "orphans", "summary", "overall"}
REQUIRED_FEATURE_KEYS = {
    "feature_path", "feature_slug", "group", "slice_ref", "frozen", "commits",
    "source_files_count", "ac_file", "ac_counts", "eval_group_file",
    "eval_verdict", "docs", "status",
}
ALLOWED_STATUSES = {"green", "amber", "red"}
ALLOWED_OVERALL = {"green", "red"}
ALLOWED_VERDICTS = {"approved", "needs_revision", "escalate", "missing"}
REQUIRED_AC_COUNT_KEYS = {"pass", "fail", "untested"}
REQUIRED_SUMMARY_KEYS = {"features_total", "green", "amber", "red", "orphans_count"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    path = Path(path)
    if not path.exists():
        return [f"file not found: {path}"]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return ["top level must be a mapping"]

    missing = REQUIRED_TOP_KEYS - set(data)
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")
        return errors

    features = data["features"]
    if not isinstance(features, list):
        errors.append("'features' must be a list")
        return errors

    counted = {"green": 0, "amber": 0, "red": 0}
    for i, row in enumerate(features):
        rid = row.get("feature_slug", f"features[{i}]") if isinstance(row, dict) else f"features[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{rid}: row must be a mapping")
            continue
        row_missing = REQUIRED_FEATURE_KEYS - set(row)
        if row_missing:
            errors.append(f"{rid}: missing keys {sorted(row_missing)}")
        status = row.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{rid}: status={status!r} not in {sorted(ALLOWED_STATUSES)}")
        else:
            counted[status] += 1
        if row.get("eval_verdict") not in ALLOWED_VERDICTS:
            errors.append(
                f"{rid}: eval_verdict={row.get('eval_verdict')!r} not in {sorted(ALLOWED_VERDICTS)}"
            )
        ac_counts = row.get("ac_counts")
        if not isinstance(ac_counts, dict) or set(ac_counts) != REQUIRED_AC_COUNT_KEYS:
            errors.append(f"{rid}: ac_counts must have exactly keys {sorted(REQUIRED_AC_COUNT_KEYS)}")
        commits = row.get("commits")
        if not isinstance(commits, list):
            errors.append(f"{rid}: commits must be a list")
        if row.get("docs") not in (True, False, None):
            errors.append(f"{rid}: docs must be true, false, or null")

    summary = data["summary"]
    if not isinstance(summary, dict) or REQUIRED_SUMMARY_KEYS - set(summary):
        errors.append(f"summary must contain keys {sorted(REQUIRED_SUMMARY_KEYS)}")
    else:
        if summary["features_total"] != len(features):
            errors.append(
                f"summary.features_total={summary['features_total']} but "
                f"{len(features)} feature rows present"
            )
        for k in ("green", "amber", "red"):
            if summary[k] != counted[k]:
                errors.append(
                    f"summary.{k}={summary[k]} but counted {counted[k]} rows"
                )
        orphans = data["orphans"]
        if not isinstance(orphans, list):
            errors.append("'orphans' must be a list")
        elif summary["orphans_count"] != len(orphans):
            errors.append(
                f"summary.orphans_count={summary['orphans_count']} but "
                f"{len(orphans)} orphans listed"
            )

    overall = data["overall"]
    if overall not in ALLOWED_OVERALL:
        errors.append(f"overall={overall!r} not in {sorted(ALLOWED_OVERALL)}")
    else:
        expected = "green" if counted["red"] == 0 else "red"
        if overall != expected:
            errors.append(
                f"overall={overall!r} inconsistent with red-row count "
                f"{counted['red']} (expected {expected!r}; green iff zero red rows)"
            )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validator.py <path/to/trace.yaml>", file=sys.stderr)
        return 2
    errors = validate(Path(argv[1]))
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest -q skaileup/14_ops/12_trace/tests/`
Expected: 6 passed.
Also: `python3 skaileup/14_ops/12_trace/validator.py skaileup/14_ops/12_trace/tests/fixtures/trace_green.yaml`
Expected: `OK`, exit 0.

- [ ] **Step 5: Write the SKILL.md**

Create `skaileup/14_ops/12_trace/SKILL.md` with exactly this content:

````markdown
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
````

- [ ] **Step 6: Register the artifact id + DOMAIN.md row**

6a. In `skaileup/contracts/artifacts.yaml`, insert after the `eval-product-result:` entry:

```yaml
  trace:
    path: _implementation/trace.yaml
    kind: durable
    side: impl
    produced_by: ops-trace
    description: Two-way traceability matrix — per-feature roll-up (frozen/commits/ACs/eval/docs) + orphan code list.
```

6b. In `skaileup/14_ops/DOMAIN.md`:
- Add after the `**ops-eval-product**` bullet:

```markdown
- **ops-trace** (`trace/`) — Two-way traceability reconciler; asserts every feature is shipped/tested/evaluated/documented and lists orphan code; produces `_implementation/trace.yaml`.
```

- Replace the sequence block:

```
ops-eval-concept  →  (implementation runs)  →  ops-eval-feature (per group)  →  ops-eval-product
```

with:

```
ops-eval-concept  →  (implementation runs)  →  ops-eval-feature (per group)  →  ops-trace  →  ops-eval-product
```

- [ ] **Step 7: Verify registry**

Run: `python3 skaileup/contracts/scripts/verify_artifacts.py`
Expected: `0 errors`, exit 0.
Run: `pytest -q skaileup/14_ops/12_trace/tests/`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add skaileup/14_ops/12_trace/ skaileup/contracts/artifacts.yaml skaileup/14_ops/DOMAIN.md
git commit -m "feat(ops): add ops-trace two-way traceability skill

Direction 1: per-feature roll-up (frozen slice, commits/source_files
back-links, AC statuses, eval-feature verdict keyed on NN_group, docs)
into _implementation/trace.yaml. Direction 2: git ls-files minus
source_files union -> advisory orphan list. Validator + tests + registry.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Gate `ops-eval-product` on trace.yaml

**Files:**
- Modify: `skaileup/14_ops/07_eval-product/SKILL.md`
- Modify: `skaileup/14_ops/07_eval-product/validator.py`

**Interfaces:**
- Consumes: `_implementation/trace.yaml` keys `overall` (`green|red`) and `summary.{red,amber}` (Task 4 schema); artifact id `trace`.
- Produces: hard release gate — eval-product refuses to run its grading unless `overall == green`, and its validator refuses an `approved` verdict without a green trace.

- [ ] **Step 1: Extend the SKILL.md**

All edits to `skaileup/14_ops/07_eval-product/SKILL.md`:

1a. Frontmatter `metadata.artifacts` — replace:

```yaml
    requires:
      - id: brief
        gate: hard
```

with:

```yaml
    requires:
      - id: brief
        gate: hard
      - id: trace
        gate: hard
```

1b. Frontmatter `prerequisites.files` — after the `_implementation/eval-feature` entry, add:

```yaml
      - path: '_implementation/trace.yaml'
        gate: hard
        description: 'Two-way traceability matrix required — run ops-trace first; release refuses on any red feature row'
```

1c. Frontmatter `prerequisites.reads` — add:

```yaml
      - path: '_implementation/trace.yaml'
        description: 'Traceability matrix — overall must be green (zero red rows)'
```

1d. READS block — after the `\_implementation/eval-feature/\*.yaml` line, add:

```
! \_implementation/trace.yaml — traceability matrix; overall must be green
```

1e. MUST/NEVER block — after `MUST write eval-product.yaml before reporting`, add:

```
MUST refuse to grade unless \_implementation/trace.yaml exists with overall: green (zero red feature rows) — report each red row's feature_slug + which check failed
MUST surface trace.yaml amber rows (docs missing / eval run missing) in the final report even when proceeding
```

and after `NEVER re-check individual acceptance criteria (eval-feature did that)`, add:

```
NEVER approve a release while trace.yaml is missing, stale (older than the newest slice index.md), or overall: red
```

1f. Process — replace:

```
STEP 1: Verify all feature groups approved.
Check \_implementation/eval-feature/. If any file has verdict != "approved":
"eval-product blocked: not all feature groups approved. Run eval-feature for: <list>"
```

with:

```
STEP 1: Verify traceability + all feature groups approved.
Read \_implementation/trace.yaml. If missing:
"eval-product blocked: no trace matrix. Run ops-trace first."
If overall != "green": list every features[] row with status "red" (slug +
failed check) and report:
"eval-product blocked: trace matrix has <n> red feature rows. Repair via the
skill named per row (impl-slice-commit / impl-plan-plan-vertical /
impl-slice-test / ops-eval-feature), re-run ops-trace, then retry."
Note amber rows for the final report.
Check \_implementation/eval-feature/. If any file has verdict != "approved":
"eval-product blocked: not all feature groups approved. Run eval-feature for: <list>"
```

- [ ] **Step 2: Extend the validator**

In `skaileup/14_ops/07_eval-product/validator.py` (structure mirrors `skaileup/14_ops/06_eval-feature/validator.py`: `validate(cwd)` building a `Validator` then `return v.result()`): add immediately before the `return v.result()` line:

```python
    # Release gate: an approved product verdict requires a green trace matrix.
    def check_trace_gate():
        import yaml as _yaml
        report = v.read_json("_implementation/eval-product.yaml")
        if report is None:
            return True, ""  # absence of the report is caught by earlier checks
        if report.get("verdict") != "approved":
            return True, ""
        trace_path = Path(cwd) / "_implementation" / "trace.yaml"
        if not trace_path.exists():
            return False, "verdict=approved but _implementation/trace.yaml is missing"
        try:
            trace = _yaml.safe_load(trace_path.read_text(encoding="utf-8")) or {}
        except _yaml.YAMLError as exc:
            return False, f"trace.yaml unreadable: {exc}"
        if trace.get("overall") != "green":
            return False, f"verdict=approved but trace.yaml overall={trace.get('overall')!r}"
        return True, ""

    v.must(
        "approved verdict requires _implementation/trace.yaml with overall: green",
        check_trace_gate,
    )
```

If the file does not already import `Path`, add `from pathlib import Path` next to its existing imports.

- [ ] **Step 3: Smoke-test the gate**

```bash
cd "$(mktemp -d)" && mkdir -p _implementation
printf '{"verdict": "approved"}\n' > _implementation/eval-product.yaml
python3 /Users/matthias/.superset/worktrees/4ab1967b-09ee-47d3-b5f3-30d3d0afad59/main/skaileup/14_ops/07_eval-product/validator.py . ; cd -
```

Expected: output includes the failed rule `approved verdict requires _implementation/trace.yaml with overall: green` (non-zero/failed result — exact reporting per `validator_lib.main`). Then add a green `trace.yaml` (copy `skaileup/14_ops/12_trace/tests/fixtures/trace_green.yaml`) into the same temp `_implementation/` and re-run: the trace-gate rule must now pass (other rules may still fail on the minimal fixture — only the trace-gate rule's flip matters here).

- [ ] **Step 4: Commit**

```bash
git add skaileup/14_ops/07_eval-product/SKILL.md skaileup/14_ops/07_eval-product/validator.py
git commit -m "feat(ops): gate eval-product on trace.yaml

eval-product now hard-requires _implementation/trace.yaml with
overall: green (zero red trace rows) before grading, surfaces amber
rows, and its validator refuses an approved verdict without it.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: `impl-quality-review-feature` — feature-wise code review skill

**Files:**
- Create: `skaileup/13_impl-quality/13_review-feature/SKILL.md`
- Create: `skaileup/13_impl-quality/13_review-feature/validator.py`
- Create: `skaileup/13_impl-quality/13_review-feature/tests/test_review_feature_validator.py`
- Create: `skaileup/13_impl-quality/13_review-feature/tests/fixtures/review_approve.yaml`
- Modify: `skaileup/contracts/artifacts.yaml` (new id `feature-review-result`)
- Modify: `skaileup/13_impl-quality/DOMAIN.md` (skill row)

**Interfaces:**
- Consumes: feature frontmatter `commits`/`source_files`/`slice_ref` (Task 1), `.ac.md` (Task 2), slice dossier `plan.md`/`recap.md`/`refactor.md`, `git show <sha>`; checklists from `skaileup/13_impl-quality/03_audit/references/analysis_checklists.md` (sections `## Sub-agent 1: Logic & Runtime Errors`, `## Sub-agent 2: UI/UX & Accessibility`, `## Sub-agent 3: Security & Data Integrity`); evaluator stance from `evaluate-contract` (fallback: inlined).
- Produces: `_implementation/review/<feature_slug>.yaml` (schema below), artifact id `feature-review-result`, skill name `impl-quality-review-feature` (consumed by Tasks 7-8 flow wiring). Validator CLI: `python3 skaileup/13_impl-quality/13_review-feature/validator.py <path/to/review.yaml>`.

**Pinned review schema** (`_implementation/review/<feature_slug>.yaml`):

```yaml
schema_version: 1
feature_slug: login
feature_path: _concept/experience/features/01_user_auth/login.md
slice_ref: _implementation/slices/login/
commits_reviewed: [abc1234]
files_reviewed:
  - src/routes/login.ts
findings:                       # [] allowed
  - id: F-1
    severity: high              # critical | high | medium | low
    category: security          # logic | security | ui_ux
    file: src/routes/login.ts
    line: 42
    ac_ref: AC-2                # optional; "" when not tied to a criterion
    summary: "Password compared with == instead of constant-time check"
    recommendation: "Use crypto.timingSafeEqual via the auth helper"
counts: {critical: 0, high: 1, medium: 0, low: 0}
verdict: needs_changes          # approve | needs_changes; approve requires critical == 0 AND high == 0
last_updated: "2026-07-05"
```

- [ ] **Step 1: Write the failing test + fixture**

Create `skaileup/13_impl-quality/13_review-feature/tests/fixtures/review_approve.yaml`:

```yaml
schema_version: 1
feature_slug: login
feature_path: _concept/experience/features/01_user_auth/login.md
slice_ref: _implementation/slices/login/
commits_reviewed: [abc1234]
files_reviewed:
  - src/routes/login.ts
findings:
  - id: F-1
    severity: low
    category: ui_ux
    file: src/routes/login.ts
    line: 88
    ac_ref: ""
    summary: "Submit button lacks aria-busy during pending state"
    recommendation: "Set aria-busy=true while the mutation is in flight"
counts: {critical: 0, high: 0, medium: 0, low: 1}
verdict: approve
last_updated: "2026-07-05"
```

Create `skaileup/13_impl-quality/13_review-feature/tests/test_review_feature_validator.py`:

```python
"""Tests for the impl-quality-review-feature validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
APPROVE = THIS_DIR / "fixtures" / "review_approve.yaml"

_spec = importlib.util.spec_from_file_location(
    "review_feature_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def mutate(tmp_path: Path, transform) -> Path:
    data = yaml.safe_load(APPROVE.read_text(encoding="utf-8"))
    transform(data)
    f = tmp_path / "review.yaml"
    f.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return f


def test_approve_fixture_passes():
    assert validator.validate(APPROVE) == []


def test_missing_key_fails(tmp_path: Path):
    f = mutate(tmp_path, lambda d: d.pop("verdict"))
    assert any("verdict" in e for e in validator.validate(f))


def test_bad_severity_fails(tmp_path: Path):
    def t(d):
        d["findings"][0]["severity"] = "urgent"
    f = mutate(tmp_path, t)
    assert any("severity" in e for e in validator.validate(f))


def test_approve_with_high_finding_fails(tmp_path: Path):
    def t(d):
        d["findings"][0]["severity"] = "high"
        d["counts"] = {"critical": 0, "high": 1, "medium": 0, "low": 0}
        # verdict left approve — inconsistent on purpose
    f = mutate(tmp_path, t)
    assert any("approve" in e for e in validator.validate(f))


def test_counts_mismatch_fails(tmp_path: Path):
    def t(d):
        d["counts"] = {"critical": 3, "high": 0, "medium": 0, "low": 1}
    f = mutate(tmp_path, t)
    assert any("counts" in e for e in validator.validate(f))


def test_finding_missing_location_fails(tmp_path: Path):
    def t(d):
        d["findings"][0].pop("line")
    f = mutate(tmp_path, t)
    assert any("line" in e for e in validator.validate(f))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest -q skaileup/13_impl-quality/13_review-feature/tests/`
Expected: FAIL with `FileNotFoundError` (no `validator.py` yet).

- [ ] **Step 3: Implement the validator**

Create `skaileup/13_impl-quality/13_review-feature/validator.py`:

```python
#!/usr/bin/env python3
"""Validator for impl-quality-review-feature output
(`_implementation/review/<feature_slug>.yaml`).

Usage:
    python3 validator.py <path/to/review.yaml>

Exit codes:
    0 — valid
    2 — validation failure (errors printed to stderr)
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REQUIRED_TOP_KEYS = {
    "schema_version", "feature_slug", "feature_path", "slice_ref",
    "commits_reviewed", "files_reviewed", "findings", "counts",
    "verdict", "last_updated",
}
REQUIRED_FINDING_KEYS = {
    "id", "severity", "category", "file", "line", "ac_ref",
    "summary", "recommendation",
}
ALLOWED_SEVERITIES = {"critical", "high", "medium", "low"}
ALLOWED_CATEGORIES = {"logic", "security", "ui_ux"}
ALLOWED_VERDICTS = {"approve", "needs_changes"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    path = Path(path)
    if not path.exists():
        return [f"file not found: {path}"]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return ["top level must be a mapping"]

    missing = REQUIRED_TOP_KEYS - set(data)
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")
        return errors

    for key in ("commits_reviewed", "files_reviewed", "findings"):
        if not isinstance(data[key], list):
            errors.append(f"'{key}' must be a list")

    counted = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    if isinstance(data["findings"], list):
        for i, f in enumerate(data["findings"]):
            fid = f.get("id", f"findings[{i}]") if isinstance(f, dict) else f"findings[{i}]"
            if not isinstance(f, dict):
                errors.append(f"{fid}: finding must be a mapping")
                continue
            f_missing = REQUIRED_FINDING_KEYS - set(f)
            if f_missing:
                errors.append(f"{fid}: missing keys {sorted(f_missing)}")
            sev = f.get("severity")
            if sev not in ALLOWED_SEVERITIES:
                errors.append(f"{fid}: severity={sev!r} not in {sorted(ALLOWED_SEVERITIES)}")
            else:
                counted[sev] += 1
            if f.get("category") not in ALLOWED_CATEGORIES:
                errors.append(
                    f"{fid}: category={f.get('category')!r} not in {sorted(ALLOWED_CATEGORIES)}"
                )
            if "line" in f and not isinstance(f.get("line"), int):
                errors.append(f"{fid}: line must be an integer")

    counts = data["counts"]
    if not isinstance(counts, dict) or set(counts) != set(counted):
        errors.append(f"counts must have exactly keys {sorted(counted)}")
    else:
        for k, n in counted.items():
            if counts[k] != n:
                errors.append(f"counts.{k}={counts[k]} but {n} findings have that severity")

    verdict = data["verdict"]
    if verdict not in ALLOWED_VERDICTS:
        errors.append(f"verdict={verdict!r} not in {sorted(ALLOWED_VERDICTS)}")
    elif verdict == "approve" and (counted["critical"] > 0 or counted["high"] > 0):
        errors.append(
            "verdict=approve requires zero critical and zero high findings "
            f"(got critical={counted['critical']}, high={counted['high']})"
        )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validator.py <path/to/review.yaml>", file=sys.stderr)
        return 2
    errors = validate(Path(argv[1]))
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest -q skaileup/13_impl-quality/13_review-feature/tests/`
Expected: 6 passed.

- [ ] **Step 5: Write the SKILL.md**

Create `skaileup/13_impl-quality/13_review-feature/SKILL.md` with exactly this content:

````markdown
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
````

- [ ] **Step 6: Register the artifact id + DOMAIN.md row**

6a. In `skaileup/contracts/artifacts.yaml`, insert after the `trace:` entry added in Task 4:

```yaml
  feature-review-result:
    path: _implementation/review/        # {feature_slug}.yaml
    kind: durable
    side: impl
    produced_by: impl-quality-review-feature
    description: Per-feature code-review verdict (approve|needs_changes) + file:line findings.
```

6b. In `skaileup/13_impl-quality/DOMAIN.md`, add after the `**impl-quality-debug-handoff**` bullet:

```markdown
- **impl-quality-review-feature** (`review-feature/`) — Adversarial per-feature code review scoped to the feature's back-linked `commits[]`/`source_files[]`; writes `_implementation/review/<feature_slug>.yaml` with approve/needs_changes + file:line findings.
```

- [ ] **Step 7: Verify registry + tests**

Run: `python3 skaileup/contracts/scripts/verify_artifacts.py`
Expected: `0 errors`, exit 0.
Run: `pytest -q skaileup/13_impl-quality/13_review-feature/tests/`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add skaileup/13_impl-quality/13_review-feature/ skaileup/contracts/artifacts.yaml skaileup/13_impl-quality/DOMAIN.md
git commit -m "feat(impl-quality): add review-feature skill

Feature-scoped adversarial code review over the back-linked commits[]/
source_files[], using the audit checklists + evaluator stance; outputs
_implementation/review/<slug>.yaml (approve|needs_changes, file:line
findings) with a debug-self-verify failure path. Validator + tests.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: Flow wiring — optional review node in `skaileup-slice-impl`

**Files:**
- Modify: `skaileup/flows/skaileup-slice-impl/skaileup-slice-impl.flow.yaml`
- Modify: `skaileup/flows/skaileup-slice-impl/skaileup-slice-impl.md`
- Test: `python3 skaileup/flows/_meta/verify_flows.py`

**Interfaces:**
- Consumes: skill name `impl-quality-review-feature` (Task 6 — resolves via its SKILL.md `name:`).
- Produces: node id `i-review-feature` between `i-recap` and `i-refactor` (mirrors the existing optional-node pattern of `i-implement-page`); `requires:` ref `skill:@skaile-ai/impl-quality-review-feature`.

- [ ] **Step 1: Run the verifier to capture the failing state expectation**

Run: `python3 skaileup/flows/_meta/verify_flows.py`
Expected NOW (pre-edit): exit 0. After adding ONLY the node (next step, before the requires ref) it must fail with a missing-requires error — that ordering proves the two-sided check works.

- [ ] **Step 2: Add the node + edges**

In `skaileup/flows/skaileup-slice-impl/skaileup-slice-impl.flow.yaml`:

2a. Insert a new node after the `i-recap` node block:

```yaml
  - id: i-review-feature
    type: skill
    position:
      x: 1500
      y: 100
    data:
      skill: impl-quality-review-feature
      label: 'Slice: Feature Code Review (opt)'
      optional: true
      subagent: true
      parameters: {}
```

2b. Replace the edge:

```yaml
  - id: e-i-recap-i-refactor
    source: i-recap
    target: i-refactor
    type: flow
```

with:

```yaml
  - id: e-i-recap-i-review-feature
    source: i-recap
    target: i-review-feature
    type: optional
  - id: e-i-review-feature-i-refactor
    source: i-review-feature
    target: i-refactor
    type: flow
```

Run: `python3 skaileup/flows/_meta/verify_flows.py`
Expected: exit 2, error naming `skaileup-slice-impl` with a missing `skill:@skaile-ai/impl-quality-review-feature` in `requires:` (exact wording per the verifier).

- [ ] **Step 3: Add the requires ref**

In the same file's `requires:` block, after `- skill:@skaile-ai/impl-slice-recap`, add:

```yaml
  - skill:@skaile-ai/impl-quality-review-feature
```

Also extend the flow `description:` — replace the fragment `-> test -> recap -> refactor -> commit -> git-finish.` with `-> test -> recap -> review-feature(opt) -> refactor -> commit -> git-finish.`

Run: `python3 skaileup/flows/_meta/verify_flows.py`
Expected: `OK: 12 flows consistent — each requires: manifest exactly covers its nodes (0 warning(s))`, exit 0.

- [ ] **Step 4: Update the flow doc**

In `skaileup/flows/skaileup-slice-impl/skaileup-slice-impl.md`, add to the node/step listing (after the Recap entry, matching the doc's existing list style):

```markdown
- **Slice: Feature Code Review (optional)** — `impl-quality-review-feature` reviews the slice's feature scoped to its back-linked commits/source files (post-recap the dossier is complete enough to review; the back-link lands at commit, so pre-freeze runs review the recap's Files-touched set). Verdict `needs_changes` routes back to implement/debug-self-verify before refactor+commit.
```

(Read the file first and match its heading/list conventions; the sentence above is the content to convey.)

- [ ] **Step 5: Commit**

```bash
git add skaileup/flows/skaileup-slice-impl/skaileup-slice-impl.flow.yaml skaileup/flows/skaileup-slice-impl/skaileup-slice-impl.md
git commit -m "feat(flows): optional review-feature node in skaileup-slice-impl

Adds i-review-feature (impl-quality-review-feature, optional, subagent)
between i-recap and i-refactor, with the matching two-sided requires: ref.
verify_flows.py exits 0.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: Flow wiring — trace + review in the tier quality gates

**Files:**
- Modify: `skaileup/flows/appbuilder-standard/appbuilder-standard.flow.yaml`
- Modify: `skaileup/flows/appbuilder-standard/appbuilder-standard.md`
- Modify: `skaileup/flows/appbuilder-complex/appbuilder-complex.flow.yaml`
- Modify: `skaileup/flows/appbuilder-complex/appbuilder-complex.md`
- Test: `python3 skaileup/flows/_meta/verify_flows.py`

**Interfaces:**
- Consumes: skill names `ops-trace` (Task 4), `impl-quality-review-feature` (Task 6).
- Produces: nodes `q-review-feature` (optional, iterate per feature) and `q-trace` (required) between `q-ready` and `ops-review` in both tier flows; two new `requires:` skill refs per flow.

**Variant selection:** If `skaileup/flows/quality-gate/quality-gate.flow.yaml` exists (flow-restructure plan landed), apply **Variant A**: make these exact node/edge/requires additions ONCE inside that sub-flow (between its ready node and its terminal node) and leave the tier flows untouched — the tiers already delegate via `flow:@skaile-ai/quality-gate`, whose manifest transitively provides the two skills. Otherwise apply **Variant B** below (current repo state: no quality-gate flow exists; `ls skaileup/flows/` to confirm).

- [ ] **Step 1: Edit appbuilder-standard (Variant B)**

In `skaileup/flows/appbuilder-standard/appbuilder-standard.flow.yaml`:

1a. `requires:` — after `- skill:@skaile-ai/impl-quality-ready`, add:

```yaml
  - skill:@skaile-ai/impl-quality-review-feature
  - skill:@skaile-ai/ops-trace
```

1b. Nodes — after the `q-ready` node block, insert:

```yaml
  - id: q-review-feature
    type: skill
    position:
      x: 8100
      y: 100
    data:
      skill: impl-quality-review-feature
      label: 'Feature Code Review (per feature, opt)'
      optional: true
      subagent: true
      parameters: {}
  - id: q-trace
    type: skill
    position:
      x: 8100
      y: 300
    data:
      skill: ops-trace
      label: 'Ops Trace (two-way traceability)'
      optional: false
      parameters: {}
```

1c. Edges — replace:

```yaml
  - id: e-q-ready-ops-review
    source: q-ready
    target: ops-review
    type: flow
```

with:

```yaml
  - id: e-q-ready-q-review-feature
    source: q-ready
    target: q-review-feature
    type: optional
  - id: e-q-review-feature-q-trace
    source: q-review-feature
    target: q-trace
    type: flow
  - id: e-q-trace-ops-review
    source: q-trace
    target: ops-review
    type: flow
```

1d. `description:` — replace the fragment `Quality: unit + integration + e2e +\n  ready.` with `Quality: unit + integration + e2e +\n  ready + per-feature code review (opt) + ops-trace matrix.` (keep YAML folded-scalar indentation intact).

- [ ] **Step 2: Edit appbuilder-complex (Variant B, same content)**

Apply the identical three edits to `skaileup/flows/appbuilder-complex/appbuilder-complex.flow.yaml`:
- `requires:` — the same two `skill:` lines after `- skill:@skaile-ai/impl-quality-ready` (line ~77).
- Nodes — the same `q-review-feature` + `q-trace` blocks after its `q-ready` node (line ~502), positions `x: 8100/y: 100` and `x: 8100/y: 300` (positions are cosmetic).
- Edges — replace its `e-q-ready-ops-review` edge (line ~706) with the same three-edge chain as Step 1c.
- `description:` — add the same quality-clause mention of per-feature review + ops-trace, matching that file's phrasing.

- [ ] **Step 3: Verify flows**

Run: `python3 skaileup/flows/_meta/verify_flows.py`
Expected: `OK: 12 flows consistent — each requires: manifest exactly covers its nodes (0 warning(s))`, exit 0.

- [ ] **Step 4: Update both flow docs**

In `skaileup/flows/appbuilder-standard/appbuilder-standard.md` and `skaileup/flows/appbuilder-complex/appbuilder-complex.md`, extend the quality-section description (match each doc's existing list/table style) with:

```markdown
- **Feature Code Review (optional, per feature)** — `impl-quality-review-feature` re-runs per feature over its back-linked commits/source files; `needs_changes` verdicts route fixes through `impl-quality-debug-self-verify`.
- **Ops Trace** — `ops-trace` builds `_implementation/trace.yaml` (every feature: frozen slice, commits, source files, AC statuses, eval verdict, docs + orphan code list). `ops-eval-product` refuses release unless the matrix is green.
```

- [ ] **Step 5: Commit**

```bash
git add skaileup/flows/appbuilder-standard/ skaileup/flows/appbuilder-complex/
git commit -m "feat(flows): wire ops-trace + review-feature into standard/complex quality gate

q-review-feature (optional, per feature) and q-trace run between q-ready
and ops-review in both tier flows, with two-sided requires: updates.
verify_flows.py exits 0. (Variant B — apply inside the quality-gate
sub-flow instead once the flow-restructure plan lands.)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 9: Final verification sweep

**Files:**
- Modify: none expected (fix-forward only if a check fails)

**Interfaces:**
- Consumes: everything above.
- Produces: evidence that the whole plan holds together.

- [ ] **Step 1: Run every gate**

```bash
python3 skaileup/contracts/scripts/verify_artifacts.py
python3 skaileup/flows/_meta/verify_flows.py
pytest -q skaileup/12_impl-slice/07_commit/tests/ skaileup/12_impl-slice/04_test/tests/ skaileup/11_impl-plan/03_plan-vertical/tests/ skaileup/14_ops/12_trace/tests/ skaileup/13_impl-quality/13_review-feature/tests/
python3 skaileup/flows/_meta/test_verify.py 2>/dev/null || pytest -q skaileup/flows/_meta/test_verify.py
```

Expected: verify_artifacts `0 errors` exit 0; verify_flows `OK: 12 flows consistent` exit 0; all pytest suites PASS.

- [ ] **Step 2: Grep for consistency of the load-bearing names**

```bash
grep -rn "acceptance-criteria" skaileup/contracts/artifacts.yaml skaileup/11_impl-plan/03_plan-vertical/SKILL.md skaileup/12_impl-slice/04_test/SKILL.md skaileup/13_impl-quality/06_test-e2e/SKILL.md | wc -l
grep -rn "feature-review-result\|ops-trace\|impl-quality-review-feature" skaileup/contracts/artifacts.yaml skaileup/flows/*/*.flow.yaml | wc -l
grep -rn "slice_ref" skaileup/contracts/frontmatter.md skaileup/12_impl-slice/07_commit/SKILL.md skaileup/14_ops/12_trace/SKILL.md | wc -l
```

Expected: each count ≥ 3 (ids/names appear on both sides of every contract edge). Investigate any zero.

- [ ] **Step 3: Confirm clean tree**

Run: `git status --porcelain`
Expected: empty (everything committed across Tasks 1-8). If a fix was needed in this task, commit it as:

```bash
git commit -m "fix(trace): post-sweep consistency fixes

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Self-Review Notes (author)

- **Coverage vs spec:** R1.1 → Task 1; R1.2 → Tasks 2-3; R2 (ops-trace + eval-product gate + trace.yaml schema + orphans) → Tasks 4-5; R3 → Task 6; R4 (both flow layers, two-sided requires, verify_flows, flow docs) → Tasks 7-8; cross-cutting verification → Task 9.
- **Fallbacks stated:** dedup plan absent → inline evaluator stance + existing `evaluate-contract` reference (Task 6); flow-restructure absent → Variant B direct tier wiring (Task 8).
- **Key-name consistency:** `slice_ref`/`commits`/`source_files` (Tasks 1, 4, 6); artifact ids `acceptance-criteria`/`trace`/`feature-review-result` used identically in registry, skill frontmatter, and SKILL bodies; status enums identical in contracts, SKILL.md MUSTs, validators, and fixtures.
- **Known pre-existing inconsistency** (`product-spec/features` vs `experience/features` in plan-vertical) handled by dual-path resolution everywhere a feature file is resolved — NOT fixed here (out of scope; would touch the plan-vertical DoD verbatim strings).
