# `lab/compile-bundle` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `lab/compile-bundle` skill — a Python dev-tool that keeps `bundles/*.bundle.yaml` in sync with `flows/*.flow.yaml` by adding any missing `skill:` entries (additive only, inheritance-aware).

**Architecture:** A shared `_bundle_lib.py` handles data loading and ancestry resolution; `compile_bundle.py` computes and applies patches (additive text edits only); `validator.py` is a read-only coverage checker. `SKILL.md` tells an agent to run the script and commit the result.

**Tech Stack:** Python 3.12+ stdlib + PyYAML. pytest for unit tests. No new runtime dependencies.

**Spec:** `docs/devlog/2026-05-10-compile-bundle-design.md`
**Working directory:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

---

## File map

| File | Action | Responsibility |
|---|---|---|
| `lab/compile-bundle/_bundle_lib.py` | Create | Load flows/bundles, resolve ancestry — shared by both scripts |
| `lab/compile-bundle/compile_bundle.py` | Create | Compute missing skills, patch bundle YAML text, write |
| `lab/compile-bundle/validator.py` | Create | Read-only coverage check — every flow skill covered by its bundle |
| `lab/compile-bundle/SKILL.md` | Create | Agent prompt: run script, check diff, commit |
| `lab/compile-bundle/tests/test_bundle_lib.py` | Create | Unit tests for `_bundle_lib.py` |
| `lab/compile-bundle/tests/test_compile_bundle.py` | Create | Unit tests for `compile_bundle.py` |
| `lab/compile-bundle/tests/test_validator.py` | Create | Unit tests for `validator.py` |
| `lab/DOMAIN.md` | Modify | Add `lab-compile-bundle` to skills list |

---

## Task 1: Write `_bundle_lib.py` (shared data layer)

**Files:**
- Create: `lab/compile-bundle/_bundle_lib.py`
- Create: `lab/compile-bundle/tests/test_bundle_lib.py`

- [ ] **Step 1.1: Create directory and write failing tests**

```bash
mkdir -p lab/compile-bundle/tests
```

Write `lab/compile-bundle/tests/test_bundle_lib.py`:

```python
"""Tests for _bundle_lib.py — data loading and ancestry resolution."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from _bundle_lib import load_bundles, load_flows, resolve_ancestors


# ── Helpers ──────────────────────────────────────────────────────────


def write_flow(flows_dir: Path, stem: str, skills: list[str], optional: list[str] | None = None) -> None:
    nodes = [{"id": s, "type": "skill", "data": {"skill": s}} for s in skills]
    if optional:
        for s in optional:
            nodes.append({"id": s, "type": "skill", "data": {"skill": s}, "optional": True})
    flow = {"id": stem, "name": stem, "nodes": nodes, "edges": []}
    (flows_dir / f"{stem}.flow.yaml").write_text(yaml.dump(flow), encoding="utf-8")


def write_bundle(bundles_dir: Path, stem: str, skills: list[str], parents: list[str] | None = None) -> None:
    requires = [f"bundle:{p}" for p in (parents or [])] + [f"skill:{s}" for s in skills]
    data = {"name": stem, "requires": requires or None}
    (bundles_dir / f"{stem}.bundle.yaml").write_text(yaml.dump(data), encoding="utf-8")


# ── load_flows ────────────────────────────────────────────────────────


def test_load_flows_extracts_skills_in_document_order(tmp_path):
    d = tmp_path / "flows"
    d.mkdir()
    write_flow(d, "mvp", ["skill-a", "skill-b", "skill-c"])
    result = load_flows(d)
    assert result["mvp"] == ["skill-a", "skill-b", "skill-c"]


def test_load_flows_includes_optional_nodes(tmp_path):
    d = tmp_path / "flows"
    d.mkdir()
    write_flow(d, "mvp", ["skill-a"], optional=["skill-opt"])
    result = load_flows(d)
    assert "skill-opt" in result["mvp"]


def test_load_flows_skips_non_skill_type_nodes(tmp_path):
    d = tmp_path / "flows"
    d.mkdir()
    nodes = [
        {"id": "s", "type": "skill", "data": {"skill": "my-skill"}},
        {"id": "g", "type": "group", "data": {"label": "group-label"}},
    ]
    (d / "mvp.flow.yaml").write_text(yaml.dump({"id": "mvp", "nodes": nodes, "edges": []}))
    result = load_flows(d)
    assert result["mvp"] == ["my-skill"]


def test_load_flows_stem_strips_flow_yaml_suffix(tmp_path):
    d = tmp_path / "flows"
    d.mkdir()
    write_flow(d, "standard-app", ["s"])
    result = load_flows(d)
    assert "standard-app" in result


# ── load_bundles ──────────────────────────────────────────────────────


def test_load_bundles_splits_refs_correctly(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "simple-app", ["skill-a", "skill-b"], parents=["mvp"])
    result = load_bundles(d)
    b = result["simple-app"]
    assert b["bundle_refs"] == ["mvp"]
    assert b["skill_refs"] == ["skill-a", "skill-b"]
    assert b["other_refs"] == []


def test_load_bundles_absent_requires_treated_as_empty(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    (d / "empty.bundle.yaml").write_text("name: empty\n", encoding="utf-8")
    result = load_bundles(d)
    assert result["empty"]["skill_refs"] == []
    assert result["empty"]["bundle_refs"] == []


def test_load_bundles_stem_strips_bundle_yaml_suffix(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "standard-app", ["s"])
    result = load_bundles(d)
    assert "standard-app" in result


def test_load_bundles_preserves_raw_text(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    text = "name: mvp\ndescription: my bundle\nrequires:\n  - skill:abc\n"
    (d / "mvp.bundle.yaml").write_text(text, encoding="utf-8")
    result = load_bundles(d)
    assert result["mvp"]["raw_text"] == text


# ── resolve_ancestors ─────────────────────────────────────────────────


def test_resolve_ancestors_leaf_has_no_ancestors(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "mvp", ["skill-a", "skill-b"])
    bundles = load_bundles(d)
    assert resolve_ancestors("mvp", bundles) == set()


def test_resolve_ancestors_single_level(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "mvp", ["skill-a"])
    write_bundle(d, "simple-app", ["skill-b"], parents=["mvp"])
    bundles = load_bundles(d)
    assert resolve_ancestors("simple-app", bundles) == {"skill-a"}


def test_resolve_ancestors_multi_level(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "mvp", ["skill-a"])
    write_bundle(d, "simple-app", ["skill-b"], parents=["mvp"])
    write_bundle(d, "standard-app", ["skill-c"], parents=["simple-app"])
    bundles = load_bundles(d)
    # standard-app sees skill-a (from mvp) and skill-b (from simple-app)
    assert resolve_ancestors("standard-app", bundles) == {"skill-a", "skill-b"}


def test_resolve_ancestors_cycle_raises_with_path(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "a", [], parents=["b"])
    write_bundle(d, "b", [], parents=["a"])
    bundles = load_bundles(d)
    with pytest.raises(ValueError, match="Circular"):
        resolve_ancestors("a", bundles)
```

- [ ] **Step 1.2: Run tests — verify they all fail**

```bash
python -m pytest lab/compile-bundle/tests/test_bundle_lib.py -v 2>&1 | head -30
```

Expected: `ModuleNotFoundError: No module named '_bundle_lib'` (or similar import error).

- [ ] **Step 1.3: Write `_bundle_lib.py`**

Write `lab/compile-bundle/_bundle_lib.py`:

```python
"""_bundle_lib.py — shared data loading and ancestry resolution for compile-bundle.

Internal module — imported by compile_bundle.py and validator.py.
Not a standalone script.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

import yaml


class BundleData(TypedDict):
    bundle_refs: list[str]   # bare parent stems, e.g. ["mvp"]
    skill_refs: list[str]    # bare skill names, e.g. ["concept-brief"]
    other_refs: list[str]    # any other requires: entries (preserved verbatim)
    raw_text: str            # original file text for in-place patching
    path: Path               # file path for writing back


def load_flows(flows_dir: Path) -> dict[str, list[str]]:
    """Return {stem: [skill_name, ...]} in node document order.

    Stem is the filename without the .flow.yaml suffix.
    Includes nodes with optional: true — they are still required by the bundle.
    """
    result: dict[str, list[str]] = {}
    for path in sorted(flows_dir.glob("*.flow.yaml")):
        stem = path.name.removesuffix(".flow.yaml")
        try:
            flow = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            print(f"ERROR: malformed YAML in {path}: {exc}", file=sys.stderr)
            sys.exit(1)
        result[stem] = [
            node["data"]["skill"]
            for node in flow.get("nodes", [])
            if node.get("type") == "skill"
        ]
    return result


def load_bundles(bundles_dir: Path) -> dict[str, BundleData]:
    """Return {stem: BundleData} for each *.bundle.yaml file.

    Stem is the filename without the .bundle.yaml suffix.
    Missing requires: key is treated as an empty list.
    All skill:/bundle: prefixes are stripped; bare names are stored.
    """
    result: dict[str, BundleData] = {}
    for path in sorted(bundles_dir.glob("*.bundle.yaml")):
        stem = path.name.removesuffix(".bundle.yaml")
        raw_text = path.read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(raw_text) or {}
        except yaml.YAMLError as exc:
            print(f"ERROR: malformed YAML in {path}: {exc}", file=sys.stderr)
            sys.exit(1)
        requires = [str(r) for r in (data.get("requires") or [])]
        result[stem] = BundleData(
            bundle_refs=[r.removeprefix("bundle:") for r in requires if r.startswith("bundle:")],
            skill_refs=[r.removeprefix("skill:") for r in requires if r.startswith("skill:")],
            other_refs=[r for r in requires if not r.startswith(("bundle:", "skill:"))],
            raw_text=raw_text,
            path=path,
        )
    return result


def resolve_ancestors(
    stem: str,
    bundles: dict[str, BundleData],
    _path: tuple[str, ...] = (),
) -> set[str]:
    """Return the union of all bare skill names from all ancestor bundles.

    Resolution rule: bundle:foo → bundles[foo].
    Traversal order does not matter (result is a set union).
    Raises ValueError on circular inheritance with the full cycle path.
    """
    if stem in _path:
        idx = _path.index(stem)
        cycle = " → ".join(_path[idx:]) + f" → {stem}"
        raise ValueError(f"Circular bundle inheritance detected: {cycle}")
    _path = _path + (stem,)

    bundle = bundles.get(stem)
    if bundle is None:
        return set()

    ancestor_skills: set[str] = set()
    for parent_stem in bundle["bundle_refs"]:
        parent = bundles.get(parent_stem)
        if parent is None:
            continue
        ancestor_skills.update(parent["skill_refs"])
        ancestor_skills.update(resolve_ancestors(parent_stem, bundles, _path))
    return ancestor_skills
```

- [ ] **Step 1.4: Run tests — verify they all pass**

```bash
python -m pytest lab/compile-bundle/tests/test_bundle_lib.py -v
```

Expected: all green, 0 failures.

- [ ] **Step 1.5: Commit**

```bash
git add lab/compile-bundle/_bundle_lib.py lab/compile-bundle/tests/test_bundle_lib.py
git commit -m "feat: add _bundle_lib.py (shared data layer for compile-bundle)"
```

---

## Task 2: Write `compile_bundle.py`

**Files:**
- Create: `lab/compile-bundle/compile_bundle.py`
- Create: `lab/compile-bundle/tests/test_compile_bundle.py`

- [ ] **Step 2.1: Write failing tests**

Write `lab/compile-bundle/tests/test_compile_bundle.py`:

```python
"""Tests for compile_bundle.py — skill insertion logic and main integration."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from compile_bundle import insert_skills, main as compile_main


# ── insert_skills ─────────────────────────────────────────────────────


def test_insert_after_last_skill_line():
    raw = "requires:\n  - skill:skill-a\n  - skill:skill-b\n"
    result = insert_skills(raw, ["skill-c"])
    lines = result.splitlines()
    assert lines == ["requires:", "  - skill:skill-a", "  - skill:skill-b", "  - skill:skill-c"]


def test_insert_before_first_bundle_line_when_no_skills():
    raw = "requires:\n  - bundle:mvp\n"
    result = insert_skills(raw, ["skill-x"])
    lines = result.splitlines()
    assert lines == ["requires:", "  - skill:skill-x", "  - bundle:mvp"]


def test_insert_after_requires_key_when_list_is_empty():
    raw = "requires:\n"
    result = insert_skills(raw, ["skill-x"])
    lines = result.splitlines()
    assert lines == ["requires:", "  - skill:skill-x"]


def test_insert_preserves_other_fields():
    raw = "name: test\ndescription: foo\nrequires:\n  - skill:a\n"
    result = insert_skills(raw, ["skill-b"])
    assert "name: test" in result
    assert "description: foo" in result
    assert "  - skill:skill-b" in result


def test_insert_multiple_missing_in_flow_order():
    raw = "requires:\n  - skill:a\n"
    result = insert_skills(raw, ["skill-b", "skill-c"])
    lines = result.splitlines()
    assert lines.index("  - skill:skill-b") < lines.index("  - skill:skill-c")


def test_insert_format_has_no_space_after_colon():
    raw = "requires:\n"
    result = insert_skills(raw, ["my-skill"])
    assert "  - skill:my-skill\n" in result


# ── main (integration) ────────────────────────────────────────────────


def make_flow(flows_dir: Path, stem: str, skills: list[str]) -> None:
    nodes = [{"id": s, "type": "skill", "data": {"skill": s}} for s in skills]
    (flows_dir / f"{stem}.flow.yaml").write_text(
        yaml.dump({"id": stem, "nodes": nodes, "edges": []}), encoding="utf-8"
    )


def make_bundle(bundles_dir: Path, stem: str, content: str) -> Path:
    p = bundles_dir / f"{stem}.bundle.yaml"
    p.write_text(content, encoding="utf-8")
    return p


def run_main(flows_dir: Path, bundles_dir: Path) -> None:
    compile_main(flows_dir, bundles_dir)


def test_adds_missing_skill(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a", "skill-b"])
    make_bundle(b, "mvp", "name: mvp\nrequires:\n  - skill:skill-a\n")
    run_main(f, b)
    content = (b / "mvp.bundle.yaml").read_text()
    assert "skill:skill-b" in content
    assert "skill:skill-a" in content  # original preserved


def test_noop_when_bundle_is_already_complete(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a"])
    original = "name: mvp\nrequires:\n  - skill:skill-a\n"
    make_bundle(b, "mvp", original)
    run_main(f, b)
    assert (b / "mvp.bundle.yaml").read_text() == original


def test_skips_skills_covered_by_ancestor(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a"])
    make_flow(f, "simple-app", ["skill-a", "skill-b"])  # skill-a inherited from mvp
    make_bundle(b, "mvp", "name: mvp\nrequires:\n  - skill:skill-a\n")
    make_bundle(b, "simple-app", "name: simple-app\nrequires:\n  - bundle:mvp\n")
    run_main(f, b)
    content = (b / "simple-app.bundle.yaml").read_text()
    assert "skill:skill-b" in content
    # skill-a is covered by mvp ancestor — must NOT be duplicated
    assert content.count("skill-a") == 0


def test_preserves_user_added_skill_not_in_flow(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a"])
    make_bundle(b, "mvp", "name: mvp\nrequires:\n  - skill:skill-a\n  - skill:my-custom-tool\n")
    run_main(f, b)
    content = (b / "mvp.bundle.yaml").read_text()
    assert "my-custom-tool" in content


def test_warns_but_continues_when_no_bundle_for_flow(tmp_path, capsys):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "orphan-flow", ["skill-a"])
    # No matching bundle — should warn and not crash
    run_main(f, b)
    captured = capsys.readouterr()
    assert "orphan-flow" in captured.err
```

- [ ] **Step 2.2: Run tests — verify they fail**

```bash
python -m pytest lab/compile-bundle/tests/test_compile_bundle.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'compile_bundle'`.

- [ ] **Step 2.3: Write `compile_bundle.py`**

Write `lab/compile-bundle/compile_bundle.py`:

```python
#!/usr/bin/env python3
"""compile_bundle.py — sync bundles/*.bundle.yaml from flows/*.flow.yaml.

Additive only: adds missing skill: entries, never removes anything.
Inheritance-aware: skips skills already covered by ancestor bundles.

Run from repo root:
  python lab/compile-bundle/compile_bundle.py

Exit codes:
  0  Completed (bundles updated or already up to date)
  1  Internal error (parse failure, circular inheritance)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _bundle_lib import BundleData, load_bundles, load_flows, resolve_ancestors

FLOWS_DIR = Path("flows")
BUNDLES_DIR = Path("bundles")


def insert_skills(raw_text: str, missing: list[str]) -> str:
    """Insert missing skill lines at the correct position in bundle YAML text.

    Priority:
      1. After the last '  - skill:' line.
      2. Before the first '  - bundle:' line (if no skill lines exist).
      3. After the 'requires:' key line (if neither skill nor bundle lines exist).
    """
    lines = raw_text.splitlines(keepends=True)

    last_skill_idx: int | None = None
    first_bundle_idx: int | None = None
    requires_idx: int | None = None

    for i, line in enumerate(lines):
        if line.startswith("  - skill:"):
            last_skill_idx = i
        if first_bundle_idx is None and line.startswith("  - bundle:"):
            first_bundle_idx = i
        if requires_idx is None and line.strip() == "requires:":
            requires_idx = i

    if last_skill_idx is not None:
        insert_at = last_skill_idx + 1
    elif first_bundle_idx is not None:
        insert_at = first_bundle_idx
    elif requires_idx is not None:
        insert_at = requires_idx + 1
    else:
        insert_at = len(lines)

    new_lines = [f"  - skill:{name}\n" for name in missing]
    lines[insert_at:insert_at] = new_lines
    return "".join(lines)


def main(
    flows_dir: Path = FLOWS_DIR,
    bundles_dir: Path = BUNDLES_DIR,
) -> None:
    flows = load_flows(flows_dir)
    bundles = load_bundles(bundles_dir)

    any_updated = False

    for stem, flow_skills in sorted(flows.items()):
        if stem not in bundles:
            print(f"WARNING: no bundle for flow '{stem}' — skipping", file=sys.stderr)
            continue

        try:
            ancestor_skills = resolve_ancestors(stem, bundles)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)

        covered = set(bundles[stem]["skill_refs"]) | ancestor_skills
        missing = [s for s in flow_skills if s not in covered]

        if not missing:
            continue

        bundle = bundles[stem]
        new_text = insert_skills(bundle["raw_text"], missing)
        bundle["path"].write_text(new_text, encoding="utf-8")
        names = ", ".join(missing)
        print(f"Added {len(missing)} skill(s) to {stem}.bundle.yaml: [{names}]")
        any_updated = True

    if not any_updated:
        print("All bundles up to date.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2.4: Run unit tests — verify they pass**

```bash
python -m pytest lab/compile-bundle/tests/test_compile_bundle.py -v
```

Expected: all green.

- [ ] **Step 2.5: Run acceptance test (zero git diff)**

```bash
python lab/compile-bundle/compile_bundle.py
git diff bundles/
```

Expected output from script: `All bundles up to date.`
Expected output from git diff: empty (no changes).

If the diff is non-empty, the hand-authored bundles have gaps — inspect the output, check if it's correct, and update the expected result in the spec if so.

- [ ] **Step 2.6: Commit**

```bash
git add lab/compile-bundle/compile_bundle.py lab/compile-bundle/tests/test_compile_bundle.py
git commit -m "feat: add compile_bundle.py (flow→bundle sync script)"
```

---

## Task 3: Write `validator.py`

**Files:**
- Create: `lab/compile-bundle/validator.py`
- Create: `lab/compile-bundle/tests/test_validator.py`

- [ ] **Step 3.1: Write failing tests**

Write `lab/compile-bundle/tests/test_validator.py`:

```python
"""Tests for validator.py — read-only bundle coverage check."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))


def make_flow(flows_dir: Path, stem: str, skills: list[str]) -> None:
    nodes = [{"id": s, "type": "skill", "data": {"skill": s}} for s in skills]
    (flows_dir / f"{stem}.flow.yaml").write_text(
        yaml.dump({"id": stem, "nodes": nodes, "edges": []}), encoding="utf-8"
    )


def make_bundle(bundles_dir: Path, stem: str, skills: list[str], parents: list[str] | None = None) -> None:
    requires = [f"bundle:{p}" for p in (parents or [])] + [f"skill:{s}" for s in skills]
    (bundles_dir / f"{stem}.bundle.yaml").write_text(
        yaml.dump({"name": stem, "requires": requires or None}), encoding="utf-8"
    )


def run_validator(flows_dir: Path, bundles_dir: Path) -> int:
    """Run validator main() and return the exit code (captured from SystemExit)."""
    import validator as v
    try:
        v.main(flows_dir, bundles_dir)
        return 0
    except SystemExit as e:
        return int(e.code)


def test_passes_when_all_skills_covered(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a", "skill-b"])
    make_bundle(b, "mvp", ["skill-a", "skill-b"])
    assert run_validator(f, b) == 0


def test_fails_when_skill_missing_from_bundle(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a", "skill-b"])
    make_bundle(b, "mvp", ["skill-a"])  # skill-b missing
    assert run_validator(f, b) == 2


def test_passes_when_skill_covered_by_ancestor(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a"])
    make_flow(f, "simple-app", ["skill-a", "skill-b"])
    make_bundle(b, "mvp", ["skill-a"])
    make_bundle(b, "simple-app", ["skill-b"], parents=["mvp"])
    # skill-a is in mvp (ancestor) — simple-app is fully covered
    assert run_validator(f, b) == 0


def test_warns_and_continues_when_no_bundle_for_flow(tmp_path, capsys):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "orphan", ["skill-a"])
    rc = run_validator(f, b)
    captured = capsys.readouterr()
    assert "orphan" in captured.out or "orphan" in captured.err
    assert rc == 0  # warning only, no gap found


def test_ignores_bundle_with_no_matching_flow(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_bundle(b, "user-bundle", ["skill-a"])  # no matching flow
    assert run_validator(f, b) == 0
```

- [ ] **Step 3.2: Run tests — verify they fail**

```bash
python -m pytest lab/compile-bundle/tests/test_validator.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'validator'`.

- [ ] **Step 3.3: Write `validator.py`**

Write `lab/compile-bundle/validator.py`:

```python
#!/usr/bin/env python3
"""validator.py — check that every flow skill is covered by its bundle.

Read-only. Does not modify any files.

Run from repo root:
  python lab/compile-bundle/validator.py

Exit codes:
  0  All bundles cover their flows (or no gaps found)
  2  At least one coverage gap found
  1  Internal error (parse failure, circular inheritance)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _bundle_lib import load_bundles, load_flows, resolve_ancestors

FLOWS_DIR = Path("flows")
BUNDLES_DIR = Path("bundles")


def main(
    flows_dir: Path = FLOWS_DIR,
    bundles_dir: Path = BUNDLES_DIR,
) -> None:
    flows = load_flows(flows_dir)
    bundles = load_bundles(bundles_dir)

    gaps_found = False

    for stem, flow_skills in sorted(flows.items()):
        if stem not in bundles:
            print(f"WARNING: no bundle for flow '{stem}' — skipping")
            continue

        try:
            ancestor_skills = resolve_ancestors(stem, bundles)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)

        covered = set(bundles[stem]["skill_refs"]) | ancestor_skills
        missing = [s for s in flow_skills if s not in covered]

        if missing:
            print(f"FAIL: {stem}.bundle.yaml is missing {len(missing)} skill(s): {missing}")
            gaps_found = True

    if not gaps_found:
        print("PASS — all bundles cover their flows")
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3.4: Run unit tests — verify they pass**

```bash
python -m pytest lab/compile-bundle/tests/test_validator.py -v
```

Expected: all green.

- [ ] **Step 3.5: Run all tests together**

```bash
python -m pytest lab/compile-bundle/tests/ -v
```

Expected: all green, 0 failures.

- [ ] **Step 3.6: Run validator against real bundles**

```bash
python lab/compile-bundle/validator.py
```

Expected: `PASS — all bundles cover their flows` with exit code 0.

- [ ] **Step 3.7: Commit**

```bash
git add lab/compile-bundle/validator.py lab/compile-bundle/tests/test_validator.py
git commit -m "feat: add validator.py (read-only bundle coverage check)"
```

---

## Task 4: Write `SKILL.md` and update `lab/DOMAIN.md`

**Files:**
- Create: `lab/compile-bundle/SKILL.md`
- Modify: `lab/DOMAIN.md`

- [ ] **Step 4.1: Write `SKILL.md`**

Write `lab/compile-bundle/SKILL.md`:

```markdown
---
name: lab-compile-bundle
description: "Syncs bundles/*.bundle.yaml with flows/*.flow.yaml — adds any missing skill: entries to each bundle's requires: list. Additive only: never removes entries a user has added. Inheritance-aware: skips skills already provided by ancestor bundles."
metadata:
  version: "0.1.0"
  tags:
    - lab
    - bundle
    - flow
    - sync
    - maintenance
  stage: alpha
  prerequisites:
    reads:
      - path: "flows"
        description: "Flow YAML files — source of truth for tier skill membership"
      - path: "bundles"
        description: "Bundle YAML files — patched in place (additive only)"
    produces:
      - path: "bundles"
        description: "Updated bundle YAML files with any missing skill: entries added"
---

# Compile Bundle

## Overview

Reads every `flows/*.flow.yaml` and ensures its paired `bundles/*.bundle.yaml`
lists all referenced skills in `requires:`. Never removes existing entries —
user-added skills and custom bundle references are preserved.

**When to run:**
- After adding a skill node to any flow YAML
- Before shipping a tier to verify the bundle is complete
- As part of routine catalog maintenance

**Not needed when:**
- No flow files have changed
- You only modified skill YAML content (not which skills a flow references)

## Invariants

- **Additive only.** Never removes `requires:` entries.
- **Inheritance-aware.** Skills provided by an ancestor bundle (`bundle:mvp` etc.)
  are not added again to the child bundle.
- **Idempotent.** Running twice produces the same result.
- **Flow-node order.** New entries follow the order of nodes in the flow file.

---

ROLE  Bundle compiler — ensures every skill in a flow is covered by its bundle.

READS
  flows/*.flow.yaml     — source of truth for skill membership per tier
  bundles/*.bundle.yaml — patched in place; non-skill entries preserved

WRITES
  bundles/*.bundle.yaml — skill: entries added where missing (never removed)

REFERENCES
  lab/compile-bundle/compile_bundle.py — the script this skill runs
  lab/compile-bundle/validator.py      — post-run coverage check

## STEPS

STEP 1: Run the compiler from repo root

```bash
python lab/compile-bundle/compile_bundle.py
```

Expected output: `Added N skill(s) to <name>.bundle.yaml: [...]` for each
updated bundle, or `All bundles up to date.` if nothing changed.

STEP 2: Run the validator

```bash
python lab/compile-bundle/validator.py
```

Expected: exits 0 with `PASS — all bundles cover their flows`.
If exit 2: surface the gap list to the user before committing.

STEP 3: Show the diff

```bash
git diff bundles/
```

Show the diff output to the user.

STEP 4: Commit if changes were made

If `git diff bundles/` is non-empty:
```bash
git add bundles/
git commit -m "chore: sync bundles from flows"
```

If empty: report "All bundles are already up to date — no commit needed."

## MUST

- Run validator.py after compile_bundle.py and surface any failures before committing
- Show `git diff bundles/` to the user before committing
- Never commit if validator.py exits non-zero

## NEVER

- Manually edit bundle YAML (always use the script)
- Remove or reorder existing `requires:` entries
- Create new bundle files (script only patches existing ones)
- Run from a directory other than the repo root

## CHECKLIST

- [ ] `compile_bundle.py` ran without error (exit 0)
- [ ] `validator.py` exits 0
- [ ] `git diff bundles/` shown to user
- [ ] If changes: committed with `chore: sync bundles from flows`
- [ ] If no changes: reported "already up to date"
```

- [ ] **Step 4.2: Update `lab/DOMAIN.md`**

Edit `lab/DOMAIN.md`. Add after the `lab-compile-validators` entry in the Skills list:

```markdown
- **lab-compile-bundle** (`compile-bundle/`) — Syncs `bundles/*.bundle.yaml` with `flows/*.flow.yaml` by adding any missing `skill:` entries. Additive only — never removes user-added entries. Run after modifying a flow.
```

- [ ] **Step 4.3: Verify SKILL.md parses correctly**

```bash
python -c "
import yaml, sys
with open('lab/compile-bundle/SKILL.md') as f:
    content = f.read()
front = content.split('---')[1]
m = yaml.safe_load(front)
assert m['name'] == 'lab-compile-bundle', f'wrong name: {m[\"name\"]}'
assert 'produces' in m['metadata']['prerequisites']
print('SKILL.md frontmatter OK')
"
```

Expected: `SKILL.md frontmatter OK`

- [ ] **Step 4.4: Commit**

```bash
git add lab/compile-bundle/SKILL.md lab/DOMAIN.md
git commit -m "feat: add lab-compile-bundle SKILL.md and register in DOMAIN.md"
```

---

## Acceptance Criteria

- [ ] `python lab/compile-bundle/compile_bundle.py` prints `All bundles up to date.` on existing hand-authored bundles
- [ ] `git diff bundles/` is empty after running the script on existing bundles
- [ ] `python lab/compile-bundle/validator.py` exits 0
- [ ] `python -m pytest lab/compile-bundle/tests/ -v` — all tests pass
- [ ] `lab/compile-bundle/SKILL.md` has `name: lab-compile-bundle` and correct frontmatter
- [ ] `lab/DOMAIN.md` lists `lab-compile-bundle`
