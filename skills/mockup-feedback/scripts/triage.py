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


# A specRef key is routable only if some renderer emits it. `feature` is not:
# the overlay's resolveTarget returns element/screen/journey/route/provisional,
# and tree/09_mockup/walkthrough/README.md declares no `data-spec-feature` attribute. Routing
# a key nothing produces reads as coverage the feedback loop does not have.
#
# `journey` routes to the whole of stories.yaml because journeys have never lived
# in a per-journey file — the value identifies a journey *within* that file, and
# patching addresses the section, not the path.
SCREEN_DIR = "07_screens"
JOURNEYS_FILE = "04_journeys/stories.yaml"


def resolve_file(spec_ref: dict, concept_root: Path) -> tuple[str | None, str | None]:
    """Resolve a specRef dict to a relative _concept/ path.

    Returns (relative_path, None) on success or (None, reason_string) on failure.
    Lookup priority: screen > journey.
    """
    screen = spec_ref.get("screen")
    if screen:
        rel = f"{SCREEN_DIR}/{screen}.md"
        if (concept_root / rel).is_file():
            return rel, None
        return None, f"file not found: _concept/{rel}"

    if spec_ref.get("journey"):
        if (concept_root / JOURNEYS_FILE).is_file():
            return JOURNEYS_FILE, None
        return None, f"file not found: _concept/{JOURNEYS_FILE}"

    return None, "no specRef target (screen and journey both absent or null)"


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
        "triagedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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
