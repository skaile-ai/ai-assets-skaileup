#!/usr/bin/env python3
"""Validator for impl-slice-commit.

Three deterministic modes — does NOT actually run `git`; that is the skill
body's job. The validator pins (A) the commit-plan JSON shape, (B) the
post-commit FREEZE of `_implementation/slices/<id>/` (dir kept, index.md present,
progress.yaml removed), and (C) the pre-flight gate that all four handoffs exist
with correct decisions.

Usage:
    # Mode A: validate a commit-plan JSON.
    python3 validator.py --plan <path/to/commit-plan.json> [--expected-files <file>]

    # Mode B: assert the lifecycle terminator FROZE _implementation/slices/<id>/
    #         (the dir still exists and contains index.md; progress.yaml is gone).
    python3 validator.py --post-commit <path/to/_implementation/slices/<id>/>

    # Mode C: pre-flight — assert all 4 handoffs exist with correct values.
    python3 validator.py --pre-flight <slice_id> [--root <repo-root>]

Exit codes:
    0 — valid
    2 — validation failure
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ALLOWED_TYPES = {"feat", "fix", "chore", "test", "docs", "refactor"}
SLICE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,47}$")
SUMMARY_MAX = 80

REQUIRED_BODY_LINES = ("Slice:", "Feature:", "Feature spec:")

# Mode C — required handoffs and their decisions.
HANDOFF_FILES = ("test.md", "recap.md", "refactor.md", "plan.md")
DECISION_DONE_RE = re.compile(r"^Decision: Done$", re.MULTILINE)
APPROVAL_RESOLVED_RE = re.compile(
    r"^Approval status: (approved|rejected|modified)$", re.MULTILINE
)


# ── Mode A: commit-plan JSON ──────────────────────────────────────


def validate_plan(plan_path: Path, expected_files_path: Path | None) -> list[str]:
    errors: list[str] = []
    if not plan_path.exists():
        return [f"file not found: {plan_path}"]
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]

    # Top-level keys
    for key in ("slice_id", "feature_title", "feature_path", "commits"):
        if key not in plan:
            errors.append(f"commit-plan missing top-level key: {key!r}")

    slice_id = plan.get("slice_id")
    if isinstance(slice_id, str) and not SLICE_ID_RE.match(slice_id):
        errors.append(
            f"slice_id {slice_id!r} does not match ^[a-z][a-z0-9-]{{1,47}}$"
        )

    commits = plan.get("commits")
    if not isinstance(commits, list):
        errors.append("'commits' must be a list")
        return errors
    if len(commits) < 1:
        errors.append("'commits' must contain ≥ 1 entry")
        return errors

    union_files: list[str] = []
    for idx, commit in enumerate(commits, start=1):
        if not isinstance(commit, dict):
            errors.append(f"commit {idx} must be an object")
            continue
        ctype = commit.get("type")
        if ctype not in ALLOWED_TYPES:
            errors.append(
                f"commit {idx} type={ctype!r}; must be one of {sorted(ALLOWED_TYPES)}"
            )
        summary = commit.get("summary", "")
        if not isinstance(summary, str) or not summary.strip():
            errors.append(f"commit {idx} missing/empty 'summary'")
        elif len(summary) > SUMMARY_MAX:
            errors.append(
                f"commit {idx} summary length {len(summary)} > {SUMMARY_MAX} chars"
            )
        files = commit.get("files")
        if not isinstance(files, list) or not files:
            errors.append(f"commit {idx} 'files' must be a non-empty list")
        else:
            union_files.extend(files)
        body = commit.get("body", "")
        if not isinstance(body, str):
            errors.append(f"commit {idx} 'body' must be a string")
        else:
            for required_line in REQUIRED_BODY_LINES:
                if required_line not in body:
                    errors.append(
                        f"commit {idx} body missing required line prefix "
                        f"{required_line!r}"
                    )

    # Cross-check union of files against expected list, if provided.
    if expected_files_path is not None:
        if not expected_files_path.exists():
            errors.append(f"--expected-files path not found: {expected_files_path}")
        else:
            expected = {
                line.strip()
                for line in expected_files_path.read_text(
                    encoding="utf-8"
                ).splitlines()
                if line.strip()
            }
            actual = set(union_files)
            missing = expected - actual
            extra = actual - expected
            if missing:
                errors.append(
                    f"commit-plan files miss expected entries: {sorted(missing)}"
                )
            if extra:
                errors.append(
                    f"commit-plan files include unexpected entries: {sorted(extra)}"
                )

    return errors


# ── Mode B: post-commit dir-frozen ────────────────────────────────


def validate_post_commit(slice_dir: Path) -> list[str]:
    """The lifecycle terminator FREEZES the slice: the dir is kept and gains an
    index.md; only the transient progress.yaml is removed. (Suggestion-B: slices
    are durable per-feature documentation, not throwaway scratch.)"""
    errors: list[str] = []
    if not slice_dir.exists():
        return [
            f"lifecycle terminator failed: {slice_dir} does not exist "
            "(expected the frozen slice dossier to be kept, not deleted)"
        ]
    if not (slice_dir / "index.md").exists():
        errors.append(
            f"lifecycle terminator failed: {slice_dir / 'index.md'} missing "
            "(expected a frozen dossier index)"
        )
    if (slice_dir / "progress.yaml").exists():
        errors.append(
            f"{slice_dir / 'progress.yaml'} still exists "
            "(transient resume state should be removed on freeze)"
        )
    return errors


# ── Mode C: pre-flight 4-handoff gate ─────────────────────────────


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("File does not start with YAML frontmatter (---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Could not parse frontmatter — need two `---` lines")
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


def validate_pre_flight(slice_id: str, root: Path) -> list[str]:
    errors: list[str] = []
    if not SLICE_ID_RE.match(slice_id):
        errors.append(
            f"slice_id {slice_id!r} does not match ^[a-z][a-z0-9-]{{1,47}}$"
        )
    slice_dir = root / "_implementation" / "slices" / slice_id
    if not slice_dir.is_dir():
        errors.append(f"slice dir does not exist: {slice_dir}")
        return errors

    found: dict[str, Path] = {}
    for f in HANDOFF_FILES:
        p = slice_dir / f
        if not p.exists():
            errors.append(f"missing handoff: {p}")
        else:
            found[f] = p

    # test.md must contain "Decision: Done".
    if "test.md" in found:
        text = found["test.md"].read_text(encoding="utf-8")
        if not DECISION_DONE_RE.search(text):
            errors.append(
                f"{found['test.md']} does not contain 'Decision: Done'"
            )

    # refactor.md must contain "Approval status: approved|rejected|modified".
    if "refactor.md" in found:
        text = found["refactor.md"].read_text(encoding="utf-8")
        if not APPROVAL_RESOLVED_RE.search(text):
            errors.append(
                f"{found['refactor.md']} does not contain "
                "'Approval status: approved|rejected|modified'"
            )

    return errors


# ── CLI ───────────────────────────────────────────────────────────


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan", help="Mode A: path to commit-plan.json")
    group.add_argument(
        "--post-commit", help="Mode B: path to _implementation/slices/<id>/ that should be frozen (kept, with index.md)"
    )
    group.add_argument("--pre-flight", help="Mode C: slice_id to verify gates for")
    parser.add_argument(
        "--expected-files",
        default=None,
        help="(Mode A) path to a newline-separated list of expected files to cross-check",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="(Mode C) repo root containing _implementation/slices/<id>/ (default: CWD)",
    )
    args = parser.parse_args(argv[1:])

    errors: list[str] = []
    if args.plan:
        expected = Path(args.expected_files) if args.expected_files else None
        errors = validate_plan(Path(args.plan), expected)
    elif args.post_commit:
        errors = validate_post_commit(Path(args.post_commit))
    elif args.pre_flight:
        errors = validate_pre_flight(args.pre_flight, Path(args.root))

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
