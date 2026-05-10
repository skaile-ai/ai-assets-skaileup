#!/usr/bin/env python3
"""Validator for the `elements:` block schema (contracts/elements_block.md).

Two modes:

1. Fixture mode — the input file contains `<!-- example: <name> · expect: valid|invalid -->`
   sentinel comments. Each example's YAML block is extracted, validated, and the result
   is compared to the declared `expect:`. Overall exit is 0 iff every expectation matches.

2. Screen mode — the input file is a screen markdown file. Its YAML frontmatter is parsed;
   if `elements:` is absent (or `[]`), exit 0 (the field is optional). Otherwise validate
   each element entry.

Violations are printed as `<path>:<line>: <message>`. Exit 0 on success, 1 on failure.

Reuses `contracts/scripts/validator_lib.py` for the `Validator` class plumbing
(report-formatting). The schema-checking logic is local to this file.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

# Wire validator_lib onto sys.path; mirrors the pattern used by every existing
# validator.py in the repo (e.g. experience/screens/validator.py).
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "contracts" / "scripts"))
from validator_lib import Validator  # noqa: E402

SKILL = "lab-validate-elements-block"

# ── Enums (mirror contracts/elements_block.md) ────────────────────────────

KIND_ENUM = {
    "input", "button", "link", "image", "text",
    "region", "list", "form", "nav", "media", "custom",
}

STATES_ENUM = {
    "default", "focus", "hover", "active",
    "disabled", "loading", "error", "success", "empty",
}

KEBAB_RE = re.compile(r"^[a-z][a-z0-9-]*[a-z0-9]$")

DEFAULT_FIXTURE = "tests/elements_block_examples.md"

# ── Sentinel parsing ──────────────────────────────────────────────────────

# `<!-- example: <name> · expect: valid|invalid [· reason: <text>] -->`
# Anchored at line start so prose descriptions inside blockquotes don't match.
# Name must be kebab-case (rules out `<name>` placeholder text in docs).
SENTINEL_RE = re.compile(
    r"^<!--\s*example:\s*(?P<name>[a-z][a-z0-9-]*[a-z0-9])\s*·\s*expect:\s*(?P<expect>valid|invalid)\b",
    re.MULTILINE,
)


def _extract_examples(text: str) -> list[dict]:
    """Return [{name, expect, yaml_text, yaml_start_line}, ...] for each sentinel."""
    examples: list[dict] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = SENTINEL_RE.search(lines[i])
        if not m:
            i += 1
            continue
        # Find the next ```yaml fence
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith("```yaml"):
            j += 1
        if j >= len(lines):
            i += 1
            continue
        yaml_start_line = j + 2  # 1-based line number of first YAML content line
        k = j + 1
        body: list[str] = []
        while k < len(lines) and not lines[k].strip().startswith("```"):
            body.append(lines[k])
            k += 1
        examples.append({
            "name": m.group("name"),
            "expect": m.group("expect"),
            "yaml_text": "\n".join(body),
            "yaml_start_line": yaml_start_line,
        })
        i = k + 1
    return examples


# ── Schema checks ─────────────────────────────────────────────────────────

def _validate_elements(elements, line_offsets: dict | None = None) -> list[tuple[int, str]]:
    """Validate an `elements:` block. Returns [(line_offset, message), ...].

    *line_offsets* (optional) maps element index -> source-file line number.
    When omitted, the index is reported as the offset.
    """
    violations: list[tuple[int, str]] = []

    def _line_for(idx: int) -> int:
        if line_offsets and idx in line_offsets:
            return line_offsets[idx]
        return idx

    if not isinstance(elements, list):
        violations.append((1, "elements: must be a list"))
        return violations

    seen_ids: dict[str, list[int]] = {}
    for idx, entry in enumerate(elements):
        line = _line_for(idx)
        if not isinstance(entry, dict):
            violations.append((line, f"element[{idx}] must be a mapping"))
            continue

        # Required keys
        for key in ("id", "kind", "label", "states"):
            if key not in entry:
                violations.append((line, f"element[{idx}] missing required key '{key}'"))

        # id constraints
        eid = entry.get("id")
        if isinstance(eid, str):
            if "--" in eid or not KEBAB_RE.match(eid):
                violations.append((line, f"element[{idx}] id '{eid}' is not kebab-case"))
            seen_ids.setdefault(eid, []).append(idx)

        # kind enum
        kind = entry.get("kind")
        if kind is not None and kind not in KIND_ENUM:
            violations.append((line, f"element[{idx}] kind '{kind}' is not in the kind enum"))

        # states list
        states = entry.get("states")
        if states is not None:
            if not isinstance(states, list) or len(states) == 0:
                violations.append((line, f"element[{idx}] states must be a non-empty list"))
            else:
                for s in states:
                    if not isinstance(s, str) or s not in STATES_ENUM:
                        violations.append((line, f"element[{idx}] state '{s}' is not in the states enum"))

        # label type
        label = entry.get("label")
        if label is not None and not isinstance(label, str):
            violations.append((line, f"element[{idx}] label must be a string"))

        # Optional fields — type checks
        if "provisional" in entry and not isinstance(entry["provisional"], bool):
            violations.append((line, f"element[{idx}] provisional must be a boolean"))
        if "describes" in entry and not isinstance(entry["describes"], str):
            violations.append((line, f"element[{idx}] describes must be a string"))
        if "data_entity" in entry and not isinstance(entry["data_entity"], str):
            violations.append((line, f"element[{idx}] data_entity must be a string"))
        if "acceptance_refs" in entry:
            ar = entry["acceptance_refs"]
            if not isinstance(ar, list) or not all(isinstance(x, str) for x in ar):
                violations.append((line, f"element[{idx}] acceptance_refs must be a list of strings"))

    # Duplicate IDs (report each duplicate occurrence's line)
    for eid, indices in seen_ids.items():
        if len(indices) > 1:
            for idx in indices:
                violations.append((_line_for(idx), f"element[{idx}] duplicate id '{eid}'"))

    return violations


# ── Element-line mapping for fixture YAML ─────────────────────────────────

def _map_element_lines(yaml_text: str, yaml_start_line: int) -> dict[int, int]:
    """Map element index -> source-file line number for each entry under `elements:`.

    Only items that are list-children of the top-level `elements:` key are tracked;
    list-children of other keys (e.g. `implements:`) are ignored.
    """
    mapping: dict[int, int] = {}
    idx = -1
    in_elements = False
    for offset, raw in enumerate(yaml_text.splitlines()):
        if raw.startswith("elements:"):
            in_elements = True
            continue
        if in_elements:
            # Top-level key (no indent, ends with ':' or `key: value`) closes the block.
            if re.match(r"^\S", raw):
                in_elements = False
                continue
            if re.match(r"^  - \S", raw):
                idx += 1
                mapping[idx] = yaml_start_line + offset
    return mapping


# ── Mode dispatch ─────────────────────────────────────────────────────────

def _is_fixture(text: str) -> bool:
    return bool(SENTINEL_RE.search(text))


def _validate_fixture(target: Path, text: str) -> tuple[int, list[str]]:
    """Run validator in fixture mode. Returns (failed_count, violation_messages)."""
    examples = _extract_examples(text)
    rel = str(target)
    messages: list[str] = []
    failed = 0

    for ex in examples:
        try:
            parsed = yaml.safe_load(ex["yaml_text"]) or {}
        except yaml.YAMLError as e:
            messages.append(f"{rel}:{ex['yaml_start_line']}: example '{ex['name']}' — YAML parse error: {e}")
            failed += 1
            continue

        elements = parsed.get("elements", [])
        line_offsets = _map_element_lines(ex["yaml_text"], ex["yaml_start_line"])
        violations = _validate_elements(elements, line_offsets)
        verdict = "invalid" if violations else "valid"

        if verdict != ex["expect"]:
            failed += 1
            if ex["expect"] == "valid" and verdict == "invalid":
                messages.append(
                    f"{rel}:{ex['yaml_start_line']}: example '{ex['name']}' expected valid but got invalid:"
                )
                for line, msg in violations:
                    messages.append(f"  {rel}:{line}: {msg}")
            else:
                messages.append(
                    f"{rel}:{ex['yaml_start_line']}: example '{ex['name']}' expected invalid but got valid"
                )

    return failed, messages


def _validate_screen(target: Path, text: str) -> tuple[int, list[str]]:
    """Run validator in screen mode. Returns (failed_count, violation_messages)."""
    rel = str(target)
    if not text.startswith("---"):
        return 0, []  # No frontmatter; nothing to validate

    end = text.find("---", 3)
    if end < 0:
        return 1, [f"{rel}:1: malformed frontmatter (no closing ---)"]

    fm_text = text[3:end]
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        return 1, [f"{rel}:1: YAML parse error in frontmatter: {e}"]

    if "elements" not in fm or fm["elements"] in (None, []):
        return 0, []  # Optional field absent — pass

    # Compute line offsets for elements within the frontmatter
    fm_lines = fm_text.splitlines()
    in_elements = False
    line_offsets: dict[int, int] = {}
    idx = -1
    for offset, raw in enumerate(fm_lines):
        if raw.startswith("elements:"):
            in_elements = True
            continue
        if in_elements:
            if re.match(r"^\S", raw):
                in_elements = False
                continue
            if re.match(r"^  - \S", raw):
                idx += 1
                # +2 because frontmatter starts at line 1 with `---` and content begins line 2
                line_offsets[idx] = offset + 2

    violations = _validate_elements(fm["elements"], line_offsets)
    if not violations:
        return 0, []
    return len(violations), [f"{rel}:{line}: {msg}" for line, msg in violations]


def main() -> int:
    target_arg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FIXTURE
    target = Path(target_arg)
    if not target.exists():
        print(f"error: target file not found: {target}", file=sys.stderr)
        return 1

    text = target.read_text(encoding="utf-8")

    if _is_fixture(text):
        failed, messages = _validate_fixture(target, text)
    else:
        failed, messages = _validate_screen(target, text)

    # Use the Validator class for a consistent summary footer
    v = Validator(str(_REPO_ROOT), SKILL)
    if failed == 0:
        v.must("all expectations satisfied", lambda: (True, ""))
    else:
        v.must(
            "all expectations satisfied",
            lambda: (False, f"{failed} expectation(s) failed; see report above"),
        )

    for msg in messages:
        print(msg)

    result = v.result()
    if result["verdict"] == "PASS":
        print(f"PASS — {SKILL}: {result['passed']} checks passed")
        return 0
    print(f"FAIL — {SKILL}: {result['failed']} violation(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
