#!/usr/bin/env python3
"""
Validator for `impl-quality/debug-self-verify` outputs.

Schema-shape check on `_debug/<id>/protocol.md`:

- Required H1 heading: `# Verification Protocol —`
- Required H2 headings (in order):
    `## Bug Summary`
    `## Hypothesis Under Test`
    `## Verification Steps`
    `## Success Criteria`
    `## Failure Exit Conditions`
    `## Notes for Future Re-runs`
- Under `## Verification Steps`: at least one `### Step ` heading
- Each `### Step ` block must contain bullets:
    `- **Command:**`
    `- **Expected output (success):**`
    `- **Pass criterion:**`
  (the `- **Expected output (still-broken):**` bullet is optional)
- `## Success Criteria` must contain at least one `- [ ]` checkbox
- Exit code 0 if shape valid; 1 with diagnostic if not.

Usage:
    python validator.py <path-to-protocol.md>
    python validator.py --help
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

USAGE = (
    "usage: python validator.py <path-to-protocol.md>\n"
    "       python validator.py --help\n"
    "\n"
    "Validates a `_debug/<id>/protocol.md` produced by impl-quality-debug-self-verify.\n"
    "Exit codes: 0 = valid, 1 = invalid (with diagnostic on stderr), 2 = bad usage.\n"
)

REQUIRED_H1_PREFIX = "# Verification Protocol —"

REQUIRED_H2_ORDER = [
    "## Bug Summary",
    "## Hypothesis Under Test",
    "## Verification Steps",
    "## Success Criteria",
    "## Failure Exit Conditions",
    "## Notes for Future Re-runs",
]

REQUIRED_STEP_BULLETS = [
    "- **Command:**",
    "- **Expected output (success):**",
    "- **Pass criterion:**",
]


def fail(msg: str) -> int:
    print(f"validator: FAIL — {msg}", file=sys.stderr)
    return 1


def ok(msg: str) -> int:
    print(f"validator: OK — {msg}")
    return 0


def validate(path: Path) -> int:
    if not path.exists():
        return fail(f"file not found: {path}")
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    errors: list[str] = []

    # 1. H1 prefix
    h1_lines = [ln for ln in lines if ln.startswith("# ") and not ln.startswith("## ")]
    if not h1_lines:
        errors.append("missing required H1 heading (expected line starting with `# Verification Protocol —`)")
    elif not h1_lines[0].startswith(REQUIRED_H1_PREFIX):
        errors.append(
            f"first H1 heading is `{h1_lines[0]}` but expected to start with `{REQUIRED_H1_PREFIX}`"
        )

    # 2. Required H2 headings, in order
    h2_lines = [ln.strip() for ln in lines if ln.startswith("## ")]
    # match by exact prefix because a heading like "## Bug Summary — login bug" is acceptable
    cursor = 0
    missing: list[str] = []
    for required in REQUIRED_H2_ORDER:
        found_at = -1
        for idx in range(cursor, len(h2_lines)):
            if h2_lines[idx] == required or h2_lines[idx].startswith(required + " "):
                found_at = idx
                break
        if found_at == -1:
            missing.append(required)
        else:
            cursor = found_at + 1
    if missing:
        errors.append(
            "missing or out-of-order required H2 headings: " + ", ".join(repr(m) for m in missing)
        )

    # 3. At least one ### Step under ## Verification Steps
    # find the slice of lines from `## Verification Steps` up to the next H2
    in_steps_section = False
    steps_section_lines: list[str] = []
    for ln in lines:
        if ln.strip() == "## Verification Steps" or ln.strip().startswith("## Verification Steps "):
            in_steps_section = True
            continue
        if in_steps_section and ln.startswith("## ") and not ln.startswith("### "):
            in_steps_section = False
            continue
        if in_steps_section:
            steps_section_lines.append(ln)

    step_headings = [ln for ln in steps_section_lines if ln.startswith("### Step ")]
    if not step_headings:
        errors.append("`## Verification Steps` must contain at least one `### Step ` heading")

    # 4. Each ### Step block must contain the three required bullets
    # Re-parse the steps section into per-step blocks
    blocks: list[tuple[str, list[str]]] = []
    current_name: str | None = None
    current_body: list[str] = []
    for ln in steps_section_lines:
        if ln.startswith("### Step "):
            if current_name is not None:
                blocks.append((current_name, current_body))
            current_name = ln.strip()
            current_body = []
        else:
            current_body.append(ln)
    if current_name is not None:
        blocks.append((current_name, current_body))

    for name, body in blocks:
        body_text = "\n".join(body)
        for required_bullet in REQUIRED_STEP_BULLETS:
            if required_bullet not in body_text:
                errors.append(f"`{name}` is missing required bullet `{required_bullet}`")

    # 5. ## Success Criteria must have at least one `- [ ]` checkbox
    in_success = False
    success_lines: list[str] = []
    for ln in lines:
        if ln.strip() == "## Success Criteria" or ln.strip().startswith("## Success Criteria "):
            in_success = True
            continue
        if in_success and ln.startswith("## "):
            in_success = False
            continue
        if in_success:
            success_lines.append(ln)
    has_checkbox = any(re.match(r"\s*- \[ \] ", ln) for ln in success_lines)
    if not has_checkbox:
        errors.append("`## Success Criteria` must contain at least one `- [ ]` checkbox")

    if errors:
        for e in errors:
            print(f"validator: FAIL — {e}", file=sys.stderr)
        return 1

    return ok(f"protocol shape valid ({len(blocks)} step(s)): {path}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    arg = argv[1]
    if arg in ("--help", "-h"):
        print(USAGE)
        return 0
    return validate(Path(arg))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
