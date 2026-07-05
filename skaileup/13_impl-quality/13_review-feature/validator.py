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
