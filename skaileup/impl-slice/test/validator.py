#!/usr/bin/env python3
"""Validator for impl-slice-test handoff files (`_slice/impl/<id>/test.md`).

Usage:
    python3 validator.py <path/to/test.md> [--plan <path/to/plan.md>]

Without `--plan`, only in-file checks run. With `--plan`, the validator
additionally enforces that every bullet in plan.md `### Manual checks` and
`### Automated tests` appears in this test.md tagged.

Exit codes:
    0 — valid (warnings may still be printed to stderr)
    2 — validation failure (errors printed to stderr)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REQUIRED_FRONTMATTER_KEYS = {
    "slice_id",
    "feature_title",
    "feature_path",
    "phase",
    "tier",
    "created_at",
    "last_updated",
}

REQUIRED_TOP_SECTIONS = [
    "## Slice goal recap (1-2 lines)",
    "## Manual checks done",
    "## Automated tests run",
    "## Usability observations",
    "## Outstanding issues",
    "## Decision",
]

ALLOWED_TIERS = {"mvp", "simple-app", "standard-app", "complex-app"}
SLICE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,47}$")
DECISION_RE = re.compile(r"^Decision: (Done|Needs more work|Blocked)$", re.MULTILINE)
TAG_RE = re.compile(r"\[(PASS|FAIL|SKIPPED)\]")
BLOCKER_RE = re.compile(r"\[BLOCKER\]")
BULLET_RE = re.compile(r"^\s*-\s+(.*)$")


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("File does not start with YAML frontmatter (---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Could not parse frontmatter — need two `---` lines")
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    return fm, body


def extract_section(body: str, header: str) -> str:
    """Return text under `header` until the next same-or-higher-level header or EOF.

    Sub-sections (`### `) stop at the next `### ` or `## `. Top sections
    (`## `) stop at the next `## ` only.
    """
    lines = body.splitlines()
    out: list[str] = []
    inside = False
    is_subsection = header.startswith("### ")
    for line in lines:
        stripped = line.rstrip()
        if stripped == header:
            inside = True
            continue
        if inside:
            if is_subsection:
                if stripped.startswith("### ") and stripped != header:
                    break
                if stripped.startswith("## "):
                    break
            else:
                if stripped.startswith("## ") and stripped != header:
                    break
            out.append(line)
    return "\n".join(out).strip("\n")


def extract_bullets(section: str) -> list[str]:
    """Return the body text of every '- ...' bullet line in section."""
    bullets: list[str] = []
    for line in section.splitlines():
        m = BULLET_RE.match(line)
        if m:
            bullets.append(m.group(1).strip())
    return bullets


def strip_tag(bullet_text: str) -> str:
    """Remove leading [PASS|FAIL|SKIPPED] tag from a bullet body for matching."""
    return TAG_RE.sub("", bullet_text, count=1).strip(" -—:")


def normalize_for_match(s: str) -> str:
    """Lowercase + collapse whitespace for fuzzy bullet-equality."""
    return re.sub(r"\s+", " ", s.lower()).strip()


def validate(
    path: Path, plan_path: Path | None = None
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return ([f"file not found: {path}"], warnings)

    text = path.read_text(encoding="utf-8")
    try:
        fm, body = split_frontmatter(text)
    except ValueError as exc:
        return ([str(exc)], warnings)

    # Frontmatter shape
    missing = REQUIRED_FRONTMATTER_KEYS - set(fm)
    if missing:
        errors.append(f"missing frontmatter keys: {sorted(missing)}")

    if fm.get("phase") != "test":
        errors.append(f"phase must be 'test', got {fm.get('phase')!r}")

    tier = fm.get("tier")
    if tier not in ALLOWED_TIERS:
        errors.append(
            f"tier must be one of {sorted(ALLOWED_TIERS)}, got {tier!r}"
        )

    slice_id = fm.get("slice_id")
    if not isinstance(slice_id, str) or not SLICE_ID_RE.match(slice_id):
        errors.append(
            f"slice_id {slice_id!r} does not match ^[a-z][a-z0-9-]{{1,47}}$"
        )
    else:
        parent_name = path.parent.name
        if parent_name != slice_id:
            errors.append(
                f"slice_id {slice_id!r} does not match parent dir name {parent_name!r}"
            )

    body_lines = {line.rstrip() for line in body.splitlines()}
    for section in REQUIRED_TOP_SECTIONS:
        if section not in body_lines:
            errors.append(f"missing required body section: {section!r}")

    headers_in_order: list[str] = [
        line.rstrip()
        for line in body.splitlines()
        if line.rstrip() in REQUIRED_TOP_SECTIONS
    ]
    if (
        headers_in_order != REQUIRED_TOP_SECTIONS
        and set(headers_in_order) == set(REQUIRED_TOP_SECTIONS)
    ):
        errors.append(
            f"required body sections present but out of order. Got: {headers_in_order}"
        )

    # Manual checks done — every bullet must have a tag.
    if "## Manual checks done" in body_lines:
        sec = extract_section(body, "## Manual checks done")
        for bullet in extract_bullets(sec):
            if not TAG_RE.search(bullet):
                errors.append(
                    f"'## Manual checks done' bullet missing [PASS|FAIL|SKIPPED] tag: "
                    f"{bullet[:80]!r}"
                )

    # Automated tests run — every bullet must have a tag.
    if "## Automated tests run" in body_lines:
        sec = extract_section(body, "## Automated tests run")
        for bullet in extract_bullets(sec):
            if not TAG_RE.search(bullet):
                errors.append(
                    f"'## Automated tests run' bullet missing [PASS|FAIL|SKIPPED] tag: "
                    f"{bullet[:80]!r}"
                )

    # Decision line — exactly one valid value.
    decision_matches = DECISION_RE.findall(body)
    if len(decision_matches) == 0:
        errors.append(
            "no valid 'Decision: Done|Needs more work|Blocked' line found"
        )
    elif len(decision_matches) > 1:
        errors.append(
            f"multiple Decision lines found: {decision_matches}"
        )
    else:
        decision = decision_matches[0]
        if decision == "Done":
            outstanding = extract_section(body, "## Outstanding issues")
            if BLOCKER_RE.search(outstanding):
                errors.append(
                    "'Decision: Done' but '## Outstanding issues' contains a "
                    "[BLOCKER] item — refuse Done while blockers exist"
                )

    # Cross-file check vs plan.md (optional).
    if plan_path is not None:
        if not plan_path.exists():
            errors.append(f"--plan path not found: {plan_path}")
        else:
            try:
                plan_text = plan_path.read_text(encoding="utf-8")
                _, plan_body = split_frontmatter(plan_text)
            except ValueError as exc:
                errors.append(f"plan.md parse error: {exc}")
            else:
                # Manual checks: every plan bullet appears in test.md (tagged or not).
                plan_manual = extract_bullets(
                    extract_section(plan_body, "### Manual checks")
                )
                test_manual = extract_bullets(
                    extract_section(body, "## Manual checks done")
                )
                test_manual_norm = [
                    normalize_for_match(strip_tag(b)) for b in test_manual
                ]
                for plan_bullet in plan_manual:
                    target = normalize_for_match(plan_bullet)
                    matched = any(
                        target in cand or cand.startswith(target[:30])
                        for cand in test_manual_norm
                    )
                    if not matched:
                        errors.append(
                            f"plan.md '### Manual checks' bullet not present in "
                            f"test.md '## Manual checks done': {plan_bullet[:80]!r}"
                        )

                plan_auto = extract_bullets(
                    extract_section(plan_body, "### Automated tests")
                )
                test_auto = extract_bullets(
                    extract_section(body, "## Automated tests run")
                )
                test_auto_norm = [
                    normalize_for_match(strip_tag(b)) for b in test_auto
                ]
                for plan_bullet in plan_auto:
                    target = normalize_for_match(plan_bullet)
                    matched = any(
                        target in cand or cand.startswith(target[:30])
                        for cand in test_auto_norm
                    )
                    if not matched:
                        errors.append(
                            f"plan.md '### Automated tests' bullet not present in "
                            f"test.md '## Automated tests run': {plan_bullet[:80]!r}"
                        )

    return (errors, warnings)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--plan", default=None)
    args = parser.parse_args(argv[1:])

    plan_path = Path(args.plan) if args.plan else None
    errors, warnings = validate(Path(args.path), plan_path)
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
