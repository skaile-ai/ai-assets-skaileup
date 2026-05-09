#!/usr/bin/env python3
"""triage.py — mockup-feedback-triage deterministic router.

Reads a session JSON, resolves each annotation's specRef to a _concept/ file path,
groups annotations by file, writes triage/<sid>.json.

Usage:
  python triage.py <session-json> <concept-root> <output-dir>

Exit codes:
  0  success (even if some annotations are unresolved)
  1  fatal error (bad args, malformed session JSON)
"""
from __future__ import annotations

import json
import sys
import datetime
from pathlib import Path


def resolve_file(spec_ref: dict, concept_root: Path) -> tuple[str | None, str | None]:
    """Resolve a specRef dict to a relative _concept/ path.

    Returns (relative_path, None) on success or (None, reason_string) on failure.
    Lookup priority: screen > feature > journey.
    """
    for key, subdir in [
        ("screen",  "experience/screens"),
        ("feature", "experience/features"),
        ("journey", "experience/journeys"),
    ]:
        val = spec_ref.get(key)
        if val:
            rel = f"{subdir}/{val}.md"
            if (concept_root / rel).is_file():
                return rel, None
            return None, f"file not found: _concept/{rel}"
    return None, "no specRef target (screen/feature/journey all absent or null)"


def triage_session(session: dict, concept_root: Path) -> dict:
    groups: dict[str, list[str]] = {}
    unresolved: list[dict] = []

    for ann in session.get("annotations", []):
        ann_id = ann.get("id", "<missing-id>")
        spec_ref = ann.get("specRef") or {}
        file_rel, reason = resolve_file(spec_ref, concept_root)
        if file_rel:
            groups.setdefault(file_rel, []).append(ann_id)
        else:
            unresolved.append({"annotationId": ann_id, "reason": reason})

    return {
        "sessionId": session["sessionId"],
        "triagedAt": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "groups": [{"file": f, "annotations": ids} for f, ids in groups.items()],
        "unresolved": unresolved,
    }


def main() -> int:
    if len(sys.argv) < 4:
        print(
            "Usage: python triage.py <session-json> <concept-root> <output-dir>",
            file=sys.stderr,
        )
        return 1

    session_path = Path(sys.argv[1])
    concept_root = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])

    try:
        session = json.loads(session_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot read session JSON: {exc}", file=sys.stderr)
        return 1

    if "sessionId" not in session or "annotations" not in session:
        print("ERROR: session JSON missing 'sessionId' or 'annotations'", file=sys.stderr)
        return 1

    result = triage_session(session, concept_root)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{session['sessionId']}.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    n_ann = len(session.get("annotations", []))
    n_groups = len(result["groups"])
    n_unresolved = len(result["unresolved"])
    print(
        f"{n_ann} annotation(s) triaged across {n_groups} file(s); "
        f"{n_unresolved} unresolved"
    )
    if result["unresolved"]:
        for u in result["unresolved"]:
            print(f"  UNRESOLVED {u['annotationId']}: {u['reason']}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
