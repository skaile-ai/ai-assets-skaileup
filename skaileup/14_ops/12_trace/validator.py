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
