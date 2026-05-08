#!/usr/bin/env python3
"""
Validator for `impl-quality/debug-handoff` outputs.

Schema-shape check on `_debug/<id>/handoff.md`:

- Required H1 heading: `# Debug Handoff —`
- Required H2 headings (in order):
    `## Bug Description`
    `## Repro Steps`
    `## Environment`
    `## Attempts So Far`
    `## Current Hypothesis`
    `## Suggested Next Steps`
    `## Files & Paths Involved`
    `## Open Questions for the Next Agent`
    `## Out-of-Scope (do NOT do these)`
- `## Attempts So Far` must contain a markdown table with header row
    `| # | What was tried | Outcome | Why ruled out |`
- `## Current Hypothesis` body must contain one of: `low`, `medium`, `high` (case-insensitive)
- `## Suggested Next Steps` must contain a numbered list (at least one `1. ` line)
- The literal `<id>` placeholder must NOT appear unresolved in the body
- Exit code 0 if shape valid; 1 with diagnostic if not.

Usage:
    python validator.py <path-to-handoff.md>
    python validator.py --help
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

USAGE = (
    "usage: python validator.py <path-to-handoff.md>\n"
    "       python validator.py --help\n"
    "\n"
    "Validates a `_debug/<id>/handoff.md` produced by impl-quality-debug-handoff.\n"
    "Exit codes: 0 = valid, 1 = invalid (with diagnostic on stderr), 2 = bad usage.\n"
)

REQUIRED_H1_PREFIX = "# Debug Handoff —"

REQUIRED_H2_ORDER = [
    "## Bug Description",
    "## Repro Steps",
    "## Environment",
    "## Attempts So Far",
    "## Current Hypothesis",
    "## Suggested Next Steps",
    "## Files & Paths Involved",
    "## Open Questions for the Next Agent",
    "## Out-of-Scope (do NOT do these)",
]

ATTEMPTS_HEADER_RE = re.compile(
    r"^\|\s*#\s*\|\s*What was tried\s*\|\s*Outcome\s*\|\s*Why ruled out\s*\|\s*$"
)
CONFIDENCE_RE = re.compile(r"\b(low|medium|high)\b", re.IGNORECASE)
NUMBERED_ITEM_RE = re.compile(r"^\s*1\.\s+\S")


def fail_lines(errors: list[str]) -> int:
    for e in errors:
        print(f"validator: FAIL — {e}", file=sys.stderr)
    return 1


def section_body(lines: list[str], heading: str) -> list[str]:
    """Return all lines under `heading` (H2) up to the next H2 or end-of-file."""
    body: list[str] = []
    in_section = False
    for ln in lines:
        stripped = ln.strip()
        if stripped == heading or stripped.startswith(heading + " "):
            in_section = True
            continue
        if in_section and ln.startswith("## "):
            break
        if in_section:
            body.append(ln)
    return body


def validate(path: Path) -> int:
    if not path.exists():
        return fail_lines([f"file not found: {path}"])
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []

    # 1. H1 prefix
    h1_lines = [ln for ln in lines if ln.startswith("# ") and not ln.startswith("## ")]
    if not h1_lines:
        errors.append(
            "missing required H1 heading (expected line starting with `# Debug Handoff —`)"
        )
    elif not h1_lines[0].startswith(REQUIRED_H1_PREFIX):
        errors.append(
            f"first H1 heading is `{h1_lines[0]}` but expected to start with `{REQUIRED_H1_PREFIX}`"
        )

    # 2. Required H2 headings, in order
    h2_lines = [ln.strip() for ln in lines if ln.startswith("## ")]
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
            "missing or out-of-order required H2 headings: "
            + ", ".join(repr(m) for m in missing)
        )

    # 3. Attempts So Far must contain the canonical header row
    attempts_body = section_body(lines, "## Attempts So Far")
    has_header = any(ATTEMPTS_HEADER_RE.match(ln) for ln in attempts_body)
    if not has_header:
        errors.append(
            "`## Attempts So Far` must contain the header row "
            "`| # | What was tried | Outcome | Why ruled out |`"
        )

    # 4. Current Hypothesis must include confidence keyword
    hyp_body = "\n".join(section_body(lines, "## Current Hypothesis"))
    if not CONFIDENCE_RE.search(hyp_body):
        errors.append(
            "`## Current Hypothesis` must contain one of: low / medium / high (case-insensitive)"
        )

    # 5. Suggested Next Steps must contain a numbered list (at least `1. `)
    nxt_body = section_body(lines, "## Suggested Next Steps")
    if not any(NUMBERED_ITEM_RE.match(ln) for ln in nxt_body):
        errors.append("`## Suggested Next Steps` must contain a numbered list (at least one `1. ` line)")

    # 6. The literal `<id>` placeholder must not appear unresolved in the body.
    # Note: the schema example block uses <id>; we only flag occurrences OUTSIDE fenced code blocks.
    in_fence = False
    fence_re = re.compile(r"^\s*```")
    leaked: list[int] = []
    for i, ln in enumerate(lines, start=1):
        if fence_re.match(ln):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if "<id>" in ln:
            leaked.append(i)
    if leaked:
        errors.append(
            f"unresolved `<id>` placeholder appears at line(s): {leaked} — replace with the actual bug slug"
        )

    if errors:
        return fail_lines(errors)

    print(f"validator: OK — handoff shape valid: {path}")
    return 0


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
