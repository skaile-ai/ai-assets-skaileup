#!/usr/bin/env python3
"""Validator for concept-slice-design-feature outputs.

Three modes:
    A. Standalone feature.md   — python3 validator.py <path/to/feature.md>
    B. Standalone screen.md    — python3 validator.py <path/to/screen.md>
    C. Manifest                — python3 validator.py --manifest <path/to/manifest.json>

Mode is auto-detected from the path/extension or --manifest flag.

Manifest schema:
    {
      "feature_slug": "team-todo-comments",
      "feature_group": "team-todo",
      "tier": "appbuilder-standard",
      "files": [<path>, ...]
    }

Exit codes:
    0 — valid
    2 — validation failure
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

WALKTHROUGH_EXT_BY_TIER = {
    "appbuilder-simple": "html",
    "appbuilder-standard": "astro",
    "appbuilder-complex": "html",
}

FEATURE_REQUIRED_KEYS = {
    "priority",
    "roles",
    "permissions",
    "story_refs",
    "agent_notes",
    "screens",
    "data_entities",
    "last_updated",
}

SCREEN_REQUIRED_KEYS = {
    "implements",
    "data_entities",
    "last_updated",
}

KEBAB_RE = re.compile(r"^[a-z][a-z0-9-]{0,47}$")


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("File does not start with YAML frontmatter (---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Could not parse frontmatter — need two `---` lines")
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    return fm, body


# ─── Mode A — feature.md ────────────────────────────────────────────────────


def validate_feature_md(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"file not found: {path}"]

    text = path.read_text(encoding="utf-8")
    try:
        fm, body = split_frontmatter(text)
    except ValueError as exc:
        return [str(exc)]

    missing = FEATURE_REQUIRED_KEYS - set(fm)
    if missing:
        errors.append(f"feature.md missing frontmatter keys: {sorted(missing)}")

    screens = fm.get("screens")
    if not isinstance(screens, list) or len(screens) == 0:
        errors.append("feature.md `screens:` must be a non-empty list")

    if "## Acceptance Criteria" not in body:
        errors.append("feature.md body must contain '## Acceptance Criteria' section")

    return errors


# ─── Mode B — screen.md ─────────────────────────────────────────────────────


def validate_screen_md(path: Path, feature_slug: str | None = None) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"file not found: {path}"]

    text = path.read_text(encoding="utf-8")
    try:
        fm, _ = split_frontmatter(text)
    except ValueError as exc:
        return [str(exc)]

    missing = SCREEN_REQUIRED_KEYS - set(fm)
    if missing:
        errors.append(f"screen.md missing frontmatter keys: {sorted(missing)}")

    if not isinstance(fm.get("implements"), list) or not fm.get("implements"):
        errors.append("screen.md `implements:` must be a non-empty list of feature paths")

    # Path-segment rule: parent dir of the screen MUST equal feature_slug
    if feature_slug is not None:
        parent_name = path.parent.name
        if parent_name != feature_slug:
            errors.append(
                f"screen.md path-segment rule violated: parent dir {parent_name!r} "
                f"must equal feature_slug {feature_slug!r}"
            )

    return errors


# ─── Mode C — manifest ──────────────────────────────────────────────────────


def _classify(path: Path) -> str:
    """Return 'feature', 'screen', 'walkthrough', or 'unknown'."""
    parts = path.parts
    if "product-spec" in parts and "features" in parts and path.suffix == ".md":
        return "feature"
    if "experience" in parts and "screens" in parts and path.suffix == ".md":
        return "screen"
    if "mockup-walkthrough" in parts:
        return "walkthrough"
    return "unknown"


def validate_manifest(manifest_path: Path) -> list[str]:
    errors: list[str] = []
    if not manifest_path.exists():
        return [f"manifest not found: {manifest_path}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"manifest is not valid JSON: {exc}"]

    feature_slug = manifest.get("feature_slug")
    feature_group = manifest.get("feature_group")
    tier = manifest.get("tier")
    files = manifest.get("files") or []

    if not isinstance(feature_slug, str) or not KEBAB_RE.match(feature_slug):
        errors.append(f"manifest.feature_slug invalid: {feature_slug!r}")
    if not isinstance(feature_group, str) or not KEBAB_RE.match(feature_group):
        errors.append(f"manifest.feature_group invalid: {feature_group!r}")
    if tier not in WALKTHROUGH_EXT_BY_TIER:
        errors.append(
            f"manifest.tier invalid: {tier!r}; must be one of {sorted(WALKTHROUGH_EXT_BY_TIER)}"
        )
    if not isinstance(files, list) or not files:
        errors.append("manifest.files must be a non-empty list")

    if errors:
        return errors

    base_dir = manifest_path.parent
    has_feature = False
    has_walkthrough = False
    screen_count = 0

    for rel in files:
        path = (base_dir / rel).resolve()
        kind = _classify(Path(rel))

        # Per-kind path-segment checks + content validation
        if kind == "feature":
            has_feature = True
            stem = path.stem
            if stem != feature_slug:
                errors.append(
                    f"feature path-segment rule violated: {rel} stem {stem!r} "
                    f"must equal feature_slug {feature_slug!r}"
                )
            errors.extend(validate_feature_md(path))

        elif kind == "screen":
            screen_count += 1
            # The first dir under "screens/" must equal feature_slug
            parts = Path(rel).parts
            try:
                screens_idx = parts.index("screens")
                first_segment = parts[screens_idx + 1]
            except (ValueError, IndexError):
                errors.append(f"screen path malformed: {rel}")
                continue
            if first_segment != feature_slug:
                errors.append(
                    f"screen path-segment rule violated: {rel} first dir under screens/ "
                    f"is {first_segment!r}; must equal feature_slug {feature_slug!r}"
                )
            errors.extend(validate_screen_md(path, feature_slug=feature_slug))

        elif kind == "walkthrough":
            has_walkthrough = True
            stem = path.stem
            ext = path.suffix.lstrip(".")
            if stem != feature_slug:
                errors.append(
                    f"walkthrough path-segment rule violated: {rel} stem {stem!r} "
                    f"must equal feature_slug {feature_slug!r}"
                )
            expected_ext = WALKTHROUGH_EXT_BY_TIER.get(tier)
            if ext != expected_ext:
                errors.append(
                    f"walkthrough extension mismatch: {rel} has .{ext}; "
                    f"tier {tier!r} requires .{expected_ext}"
                )
            # tier dir under mockup-walkthrough MUST equal manifest.tier
            parts = Path(rel).parts
            try:
                wm_idx = parts.index("mockup-walkthrough")
                tier_segment = parts[wm_idx + 1]
            except (ValueError, IndexError):
                errors.append(f"walkthrough path malformed: {rel}")
                continue
            if tier_segment != tier:
                errors.append(
                    f"walkthrough tier-dir mismatch: {rel} tier dir is {tier_segment!r}; "
                    f"manifest.tier is {tier!r}"
                )
            if not path.exists():
                errors.append(f"walkthrough stub does not exist: {path}")

        else:
            errors.append(f"unknown file kind for path: {rel}")

    if not has_feature:
        errors.append("manifest must include exactly one feature.md")
    if not has_walkthrough:
        errors.append("manifest must include the walkthrough stub")
    if screen_count == 0:
        errors.append("manifest must include at least one screen.md")

    return errors


# ─── CLI ────────────────────────────────────────────────────────────────────


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--manifest":
        errors = validate_manifest(Path(argv[2]))
    elif len(argv) == 2:
        path = Path(argv[1])
        kind = _classify(path)
        if kind == "feature":
            errors = validate_feature_md(path)
        elif kind == "screen":
            # Standalone screen mode: derive feature_slug from path
            parts = path.parts
            try:
                screens_idx = parts.index("screens")
                feature_slug = parts[screens_idx + 1]
            except (ValueError, IndexError):
                feature_slug = None
            errors = validate_screen_md(path, feature_slug=feature_slug)
        else:
            print(
                f"could not classify path {argv[1]!r} as feature.md or screen.md",
                file=sys.stderr,
            )
            return 2
    else:
        print(
            "Usage: validator.py <path/to/feature.md|screen.md>\n"
            "       validator.py --manifest <path/to/manifest.json>",
            file=sys.stderr,
        )
        return 2

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
