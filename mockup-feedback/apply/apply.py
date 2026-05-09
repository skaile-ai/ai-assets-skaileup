#!/usr/bin/env python3
"""apply.py — mockup-feedback-apply deterministic patcher.

Parses review.md checklist, applies approved section-anchored diffs to _concept/
files (best-effort), appends devlog, writes applied/<sid>.json, creates one git commit.

Usage:
  python apply.py <patches-json> <review-md> <concept-root> <feedback-root> [--force] [--dry-run]

Exit codes:
  0  success (at least one patch applied)
  1  pre-flight failure (dirty tree, already applied, schema error)
  2  all-failed short-circuit (no patches applied; no artifacts written)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import datetime
from pathlib import Path


# ── Diff application ──────────────────────────────────────────────────────────

def apply_section_diff(file_content: str, diff_text: str) -> tuple[str, str | None]:
    """Apply a section-anchored diff. Returns (new_content, error_or_None)."""
    lines = diff_text.strip().splitlines()
    if not lines:
        return file_content, "empty diff"
    m = re.match(r"^@@ (.+?) @@$", lines[0].strip())
    if not m:
        return file_content, f"diff missing valid @@ anchor header: {lines[0]!r}"

    anchor  = m.group(1)
    removes = [l[1:] for l in lines[1:] if l.startswith("-")]
    adds    = [l[1:] for l in lines[1:] if l.startswith("+")]

    if anchor == "frontmatter:elements":
        return _patch_frontmatter(file_content, removes, adds)
    return _patch_section(file_content, anchor, removes, adds)


def _patch_section(content: str, section_header: str, removes: list[str], adds: list[str]) -> tuple[str, str | None]:
    file_lines = content.splitlines(keepends=True)

    # Locate section header line
    sec_start = None
    for i, line in enumerate(file_lines):
        if line.rstrip("\n") == section_header:
            sec_start = i
            break

    if sec_start is None:
        if removes:
            return content, f"section not found: {section_header!r}"
        # create-section: append to end of file
        insert = "".join(a + "\n" for a in adds)
        return content + ("\n" if not content.endswith("\n") else "") + insert, None

    # Find section body range (up to next heading or EOF)
    sec_end = len(file_lines)
    for i in range(sec_start + 1, len(file_lines)):
        if re.match(r"^#{1,6} ", file_lines[i]):
            sec_end = i
            break

    body = [l.rstrip("\n") for l in file_lines[sec_start + 1:sec_end]]

    if not removes:
        # Pure insert at end of section body
        new_lines = (
            file_lines[:sec_end]
            + [a + "\n" for a in adds]
            + file_lines[sec_end:]
        )
        return "".join(new_lines), None

    # Find consecutive removes block
    try:
        start_idx = body.index(removes[0])
    except ValueError:
        return content, f"remove line not found in {section_header!r}: {removes[0]!r}"

    for offset, r in enumerate(removes):
        if start_idx + offset >= len(body) or body[start_idx + offset] != r:
            return content, (
                f"remove lines not consecutive in {section_header!r} at offset {offset}: "
                f"expected {r!r}"
            )

    new_body = body[:start_idx] + adds + body[start_idx + len(removes):]
    new_body_lines = [l + "\n" for l in new_body]
    new_lines = file_lines[:sec_start + 1] + new_body_lines + file_lines[sec_end:]
    return "".join(new_lines), None


def _patch_frontmatter(content: str, removes: list[str], adds: list[str]) -> tuple[str, str | None]:
    if not content.startswith("---\n"):
        return content, "file does not start with frontmatter ---"
    close = content.find("\n---\n", 4)
    if close < 0:
        return content, "frontmatter closing --- not found"

    fm_lines = content[4:close].splitlines()
    rest     = content[close + 5:]

    if not removes:
        return content, "provisional-promotion diff must have at least one remove line"

    try:
        start = fm_lines.index(removes[0])
    except ValueError:
        return content, f"frontmatter remove line not found: {removes[0]!r}"

    for offset, r in enumerate(removes):
        if start + offset >= len(fm_lines) or fm_lines[start + offset] != r:
            return content, f"frontmatter remove block not consecutive at offset {offset}"

    new_fm = "\n".join(fm_lines[:start] + adds + fm_lines[start + len(removes):])
    return "---\n" + new_fm + "\n---\n" + rest, None


# ── Review.md parsing ─────────────────────────────────────────────────────────

def parse_checked_ids(review_md: str) -> set[str]:
    return set(re.findall(r"- \[x\] \*\*([^*]+)\*\*", review_md))


# ── Devlog ────────────────────────────────────────────────────────────────────

def build_devlog_block(session_id: str, items: list[dict]) -> str:
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    by_file: dict[str, list[dict]] = {}
    for item in items:
        if item["status"] == "applied":
            f = item["target"]["file"]
            by_file.setdefault(f, []).append(item)

    lines = [f"\n## {today} · session {session_id}\n"]
    for f, file_items in by_file.items():
        lines.append(f"### {f}\n")
        for item in file_items:
            cat = item["target"].get("category") or "derived"
            body = (item.get("body") or "")[:80]
            lines.append(f"- {item['patchId']} applied ({cat}): {body!r}\n")
        lines.append("\n")
    return "".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    raw_args = sys.argv[1:]
    dry_run = "--dry-run" in raw_args
    force   = "--force"   in raw_args
    args    = [a for a in raw_args if not a.startswith("--")]

    if len(args) < 4:
        print(
            "Usage: python apply.py <patches-json> <review-md> "
            "<concept-root> <feedback-root> [--force] [--dry-run]",
            file=sys.stderr,
        )
        return 1

    patches_path  = Path(args[0])
    review_path   = Path(args[1])
    concept_root  = Path(args[2])
    feedback_root = Path(args[3])

    # Load inputs
    try:
        patches_data = json.loads(patches_path.read_text(encoding="utf-8"))
        review_md    = review_path.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: cannot read input files: {exc}", file=sys.stderr)
        return 1

    sid = patches_data.get("sessionId", "unknown")
    applied_path = feedback_root / "applied" / f"{sid}.json"
    devlog_path  = feedback_root / "devlog.md"

    # Pre-flight: idempotency
    if applied_path.exists() and not force:
        print(
            f"ERROR: session {sid!r} already applied "
            f"(found {applied_path}). Use --force to re-apply.",
            file=sys.stderr,
        )
        return 1

    # Pre-flight: working tree clean
    if not dry_run:
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        )
        if result.stdout.strip():
            print("ERROR: working tree is dirty. Commit or stash changes first.", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
            return 1

    # Parse review.md
    checked_ids = parse_checked_ids(review_md)
    if not checked_ids:
        print("WARNING: no checked patches in review.md — nothing to apply.", file=sys.stderr)
        return 0

    # Cross-reference checked IDs against patches JSON
    patches_by_id = {p["id"]: p for p in patches_data.get("patches", [])}
    missing = checked_ids - set(patches_by_id)
    if missing:
        print(
            f"ERROR: checked IDs in review.md not found in patches.json: {missing}",
            file=sys.stderr,
        )
        return 1

    # Load all files that will be edited (in-memory)
    file_contents: dict[str, str] = {}
    for pid in checked_ids:
        patch = patches_by_id[pid]
        rel = patch["file"]
        if rel not in file_contents:
            fp = concept_root / rel
            file_contents[rel] = fp.read_text(encoding="utf-8") if fp.is_file() else None  # type: ignore[assignment]

    # Apply patches best-effort (deterministic order by patch ID)
    applied_items: list[dict] = []
    n_applied = 0
    n_failed  = 0

    for pid in sorted(checked_ids):
        patch   = patches_by_id[pid]
        rel     = patch["file"]
        content = file_contents.get(rel)

        item_base = {
            "annotationId": patch["annotationId"],
            "patchId":      pid,
            "target": {
                "file":     rel,
                "section":  patch["section"],
                "category": patch.get("category"),
            },
            "body": patch.get("body", ""),
        }

        if content is None:
            applied_items.append({**item_base, "status": "failed", "error": f"file not found: {rel}"})
            n_failed += 1
            continue

        new_content, err = apply_section_diff(content, patch["diff"])
        if err:
            applied_items.append({**item_base, "status": "failed", "error": err})
            n_failed += 1
        else:
            file_contents[rel] = new_content
            applied_items.append({**item_base, "status": "applied"})
            n_applied += 1

    # All-failed short-circuit
    if n_applied == 0:
        print(
            f"ERROR: all {n_failed} patch(es) failed — no artifacts written. "
            "Session can be retried without --force after fixing the diffs.",
            file=sys.stderr,
        )
        for item in applied_items:
            if item["status"] == "failed":
                print(f"  FAILED {item['patchId']}: {item.get('error')}", file=sys.stderr)
        return 2

    if dry_run:
        print(f"DRY-RUN: {n_applied} would be applied, {n_failed} would fail")
        return 0

    # Determine which files actually changed (had at least one applied patch)
    files_with_applied = {
        item["target"]["file"]
        for item in applied_items
        if item["status"] == "applied"
    }

    # Write edited files to disk
    for rel, content in file_contents.items():
        if rel in files_with_applied and content is not None:
            (concept_root / rel).write_text(content, encoding="utf-8")

    # Append devlog
    devlog_path.parent.mkdir(parents=True, exist_ok=True)
    with devlog_path.open("a", encoding="utf-8") as fh:
        fh.write(build_devlog_block(sid, applied_items))

    # Write applied/<sid>.json
    applied_data = {
        "sessionId": sid,
        "appliedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items":     applied_items,
    }
    applied_path.parent.mkdir(parents=True, exist_ok=True)
    applied_path.write_text(json.dumps(applied_data, indent=2), encoding="utf-8")

    # Stage + commit
    files_to_stage = (
        [str(concept_root / rel) for rel in files_with_applied]
        + [str(devlog_path), str(applied_path)]
    )
    subprocess.run(["git", "add"] + files_to_stage, check=True)
    commit_msg = f"feedback: apply session {sid} ({n_applied} applied, {n_failed} failed)"
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg], capture_output=True, text=True
    )

    if result.returncode != 0:
        # Rollback: unstage + revert disk + delete applied JSON
        subprocess.run(
            ["git", "restore", "--staged", "--worktree", "--"] + files_to_stage,
            check=False,
        )
        if applied_path.exists():
            applied_path.unlink()
        print("ERROR: git commit failed — working tree restored.", file=sys.stderr)
        print(result.stdout + result.stderr, file=sys.stderr)
        return 1

    print(f"Applied {n_applied} patch(es), {n_failed} failed; session {sid!r} committed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
