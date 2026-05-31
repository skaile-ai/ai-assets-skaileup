#!/usr/bin/env python3
"""
Frontmatter audit for the skaileup skill collection.

Checks every SKILL.md file under skaileup/ for:
  - Missing metadata.version
  - Missing metadata.stage
  - Missing metadata.tags (or empty list)
  - Use of deprecated metadata.user_inputs
  - Use of deprecated root/metadata reads_from or writes_to
  - Skills with stage: stable and no validator.py

Usage:
    python3 docs/scripts/audit.py [--json] [--strict]

Exit codes:
    0  No violations (or only warnings)
    1  One or more violations found (use --strict to make warnings into errors)
"""

import sys
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
SKAILEUP = REPO_ROOT / "skaileup"


def extract_frontmatter(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[4:end]


def check_skill(path: Path) -> list[dict]:
    violations = []
    text = path.read_text()
    fm = extract_frontmatter(text)
    if fm is None:
        violations.append({
            "file": str(path.relative_to(REPO_ROOT)),
            "level": "error",
            "code": "NO_FRONTMATTER",
            "message": "No valid YAML frontmatter found",
        })
        return violations

    rel = str(path.relative_to(REPO_ROOT))

    # Check for deprecated fields (simple text scan — avoids YAML parse dependency)
    has_user_inputs = bool(re.search(r"^\s+user_inputs\s*:", fm, re.MULTILINE))
    has_reads_from = bool(re.search(r"^\s*reads_from\s*:", fm, re.MULTILINE))
    has_writes_to = bool(re.search(r"^\s*writes_to\s*:", fm, re.MULTILINE))

    if has_user_inputs:
        violations.append({
            "file": rel,
            "level": "error",
            "code": "DEPRECATED_USER_INPUTS",
            "message": "metadata.user_inputs is deprecated — migrate to metadata.prerequisites",
        })

    if has_reads_from:
        violations.append({
            "file": rel,
            "level": "error",
            "code": "DEPRECATED_READS_FROM",
            "message": "reads_from is deprecated — migrate to metadata.prerequisites.reads",
        })

    if has_writes_to:
        violations.append({
            "file": rel,
            "level": "error",
            "code": "DEPRECATED_WRITES_TO",
            "message": "writes_to is deprecated — migrate to metadata.prerequisites.produces",
        })

    # Check for metadata block presence
    has_metadata = bool(re.search(r"^metadata\s*:", fm, re.MULTILINE))
    if not has_metadata:
        violations.append({
            "file": rel,
            "level": "error",
            "code": "NO_METADATA",
            "message": "No metadata: block found",
        })
        return violations

    # Check required metadata fields
    has_version = bool(re.search(r"^\s+version\s*:", fm, re.MULTILINE))
    has_stage = bool(re.search(r"^\s+stage\s*:", fm, re.MULTILINE))
    has_tags = bool(re.search(r"^\s+tags\s*:\s*\[.+\]", fm, re.MULTILINE)) or \
               bool(re.search(r"^\s+tags\s*:\s*\n\s+-", fm, re.MULTILINE))

    if not has_version:
        violations.append({
            "file": rel,
            "level": "error",
            "code": "MISSING_VERSION",
            "message": "metadata.version is required (semver)",
        })

    if not has_stage:
        violations.append({
            "file": rel,
            "level": "error",
            "code": "MISSING_STAGE",
            "message": "metadata.stage is required (alpha|beta|stable)",
        })

    if not has_tags:
        violations.append({
            "file": rel,
            "level": "warning",
            "code": "MISSING_TAGS",
            "message": "metadata.tags is required (at least 2-3 tags)",
        })

    # Check stable skills have validator.py
    stage_match = re.search(r"^\s+stage\s*:\s*(.+)$", fm, re.MULTILINE)
    if stage_match:
        stage = stage_match.group(1).strip().strip("'\"")
        if stage == "stable":
            validator = path.parent / "validator.py"
            if not validator.exists():
                violations.append({
                    "file": rel,
                    "level": "error",
                    "code": "STABLE_NO_VALIDATOR",
                    "message": "stage: stable skill must have a validator.py",
                })

    return violations


def main():
    as_json = "--json" in sys.argv
    strict = "--strict" in sys.argv

    all_violations: list[dict] = []
    skill_files = sorted(SKAILEUP.rglob("SKILL.md"))

    for skill_file in skill_files:
        all_violations.extend(check_skill(skill_file))

    errors = [v for v in all_violations if v["level"] == "error"]
    warnings = [v for v in all_violations if v["level"] == "warning"]

    if as_json:
        print(json.dumps({"violations": all_violations, "errors": len(errors), "warnings": len(warnings)}, indent=2))
    else:
        if all_violations:
            for v in all_violations:
                icon = "✗" if v["level"] == "error" else "⚠"
                print(f"  {icon} [{v['code']}] {v['file']}")
                print(f"      {v['message']}")
        print(f"\n{len(skill_files)} skills audited: {len(errors)} errors, {len(warnings)} warnings")

    fail_count = len(errors) + (len(warnings) if strict else 0)
    sys.exit(1 if fail_count > 0 else 0)


if __name__ == "__main__":
    main()
