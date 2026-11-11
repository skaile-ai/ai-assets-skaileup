#!/usr/bin/env python3
"""apply.py — mockup-feedback-apply deterministic patcher.

Parses the review.md checklist, applies the approved content patches to _concept/
files (best-effort), files the approved proposals as entries of one proposal file
`_concept/proposals/<date>-mockup-feedback-<round>.yaml` (the owner artifacts
themselves are never touched), resolves the answered notes in the annotation inbox,
appends the devlog, writes applied/<round-id>.json and creates one git commit.

Usage:
  python apply.py <patches-json> <review-md> <concept-root> <feedback-root> [--force] [--dry-run]

Anchors a diff header may carry (`@@ <anchor> @@`):
  ## Heading             markdown section; removes match a consecutive block, no removes append
  frontmatter:elements   removes/adds inside the file's YAML frontmatter
  before:## Heading      adds inserted right above that heading line

A `proposal` patch carries no diff: its `target` (project-relative owner artifact),
`anchor`, `payload` and `source` become one entry `p<n>` with `status: proposed`.

Exit codes:
  0  success (at least one patch applied)
  1  pre-flight failure (dirty tree, already applied, schema error)
  2  all-failed short-circuit (no patches applied; no artifacts written)
"""
from __future__ import annotations

import datetime
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

MODEL_FILE = "10_blueprint/datamodel/model.yaml"
PACKAGE_DIR = "09_mockup/storybook"
PROPOSALS_DIR = "proposals"
PROPOSED_BY = "mockup-feedback"


# ── Diff application ──────────────────────────────────────────────────────────

def apply_diff(file_content: str, diff_text: str) -> tuple[str, str | None]:
    """Apply an anchored diff. Returns (new_content, error_or_None)."""
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
    if anchor.startswith("before:"):
        return _insert_before(file_content, anchor[len("before:"):].strip(), removes, adds)
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
        return content, "frontmatter diff must have at least one remove line"

    try:
        start = fm_lines.index(removes[0])
    except ValueError:
        return content, f"frontmatter remove line not found: {removes[0]!r}"

    for offset, r in enumerate(removes):
        if start + offset >= len(fm_lines) or fm_lines[start + offset] != r:
            return content, f"frontmatter remove block not consecutive at offset {offset}"

    new_fm = "\n".join(fm_lines[:start] + adds + fm_lines[start + len(removes):])
    return "---\n" + new_fm + "\n---\n" + rest, None


def _insert_before(content: str, heading: str, removes: list[str], adds: list[str]) -> tuple[str, str | None]:
    if removes:
        return content, "before: anchor takes adds only"
    if not adds:
        return content, "before: anchor has no add lines"
    file_lines = content.splitlines(keepends=True)
    for i, line in enumerate(file_lines):
        if line.rstrip("\n") == heading:
            return "".join(file_lines[:i] + [a + "\n" for a in adds] + file_lines[i:]), None
    return content, f"heading not found: {heading!r}"


# ── Review.md parsing ─────────────────────────────────────────────────────────

def parse_checked_ids(review_md: str) -> set[str]:
    return set(re.findall(r"- \[x\] \*\*([^*]+)\*\*", review_md))


# ── Proposals (format: tree/proposals/README.md) ──────────────────────────────

MODEL_TARGET = f"_concept/{MODEL_FILE}"
MODEL_ANCHOR = re.compile(r"^entities\.[A-Za-z_]\w*(?:\.fields\.[A-Za-z_]\w*)?$")
GLOSSARY_ANCHOR = re.compile(r"^term:\S(?:.*\S)?$")


def is_glossary_target(target: str) -> bool:
    return target == "_concept/glossary.md" or Path(target).name in ("CONTEXT.md", "GLOSSARY.md")


def check_proposal(patch: dict) -> str | None:
    """Why an approved proposal patch cannot be filed, or None."""
    missing = [k for k in ("target", "anchor", "payload", "source") if patch.get(k) in (None, "", {}, [])]
    if missing:
        return "proposal lacks " + ", ".join(missing)
    if "diff" in patch or "file" in patch:
        return "a proposal carries target/anchor/payload, never diff/file"
    target, anchor, payload = patch["target"], patch["anchor"], patch["payload"]
    if target == MODEL_TARGET:
        if not isinstance(anchor, str) or not MODEL_ANCHOR.match(anchor):
            return f"model anchor must be entities.<Entity> or entities.<Entity>.fields.<field>: {anchor!r}"
        if not isinstance(payload, dict):
            return "a model proposal's payload must be a YAML mapping"
    elif is_glossary_target(target):
        if not isinstance(anchor, str) or not GLOSSARY_ANCHOR.match(anchor):
            return f"glossary anchor must be term:<Bold Term>: {anchor!r}"
        if not isinstance(payload, str) or not payload.strip():
            return "a glossary proposal's payload must be a markdown string"
    else:
        return f"target {target!r} is neither {MODEL_TARGET} nor a glossary"
    if not isinstance(patch["source"], str) or not patch["source"].strip():
        return "a proposal's source must be a string naming the note"
    return None


_PLAIN = re.compile(r"^[A-Za-z_./][\w ./-]*$")
_RESERVED = {"true", "false", "yes", "no", "on", "off", "null", "y", "n"}


def _scalar(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return json.dumps(value)
    if isinstance(value, (dict, list)):
        return "{}" if isinstance(value, dict) else "[]"
    text = str(value)
    if _PLAIN.match(text) and text == text.rstrip() and text.lower() not in _RESERVED:
        return text
    return json.dumps(text, ensure_ascii=False)


def _emit(head: str, value, pad: str) -> list[str]:
    """YAML block lines of one node: `head` is `<key>:` or `-`, `pad` its indentation."""
    if isinstance(value, dict) and value:
        body = [l for k, v in value.items() for l in _emit(f"{_scalar(k)}:", v, pad + "  ")]
    elif isinstance(value, list) and value:
        body = [l for v in value for l in _emit("-", v, pad + "  ")]
    elif isinstance(value, str) and "\n" in value.rstrip("\n") and value[:1] not in (" ", "\t") \
            and not value.endswith("\n\n"):
        chomp = "|" if value.endswith("\n") else "|-"
        lines = value.rstrip("\n").split("\n")
        return [f"{pad}{head} {chomp}"] + [f"{pad}  {l}" if l else "" for l in lines]
    else:
        return [f"{pad}{head} {_scalar(value)}"]
    if head == "-" and isinstance(value, dict):
        return [f"{pad}- {body[0][len(pad) + 2:]}"] + body[1:]
    return [f"{pad}{head}"] + body


def proposal_scope(round_id: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", round_id.lower()).strip("-") or "round"


def proposal_path(concept_root: Path, on: str, scope: str) -> Path:
    """`proposals/<on>-mockup-feedback-<scope>.yaml`; a second run of the same day and round takes `-2`, `-3`."""
    base = f"{on}-{PROPOSED_BY}-{scope}"
    path, n = concept_root / PROPOSALS_DIR / f"{base}.yaml", 1
    while path.exists():
        n += 1
        path = concept_root / PROPOSALS_DIR / f"{base}-{n}.yaml"
    return path


def proposal_file_text(on: str, scope: str, entries: list[dict]) -> str:
    lines = [f"proposed_by: {PROPOSED_BY}", f"proposed_on: {on}", f"scope: {_scalar(scope)}", "entries:"]
    for entry in entries:
        lines += _emit("-", entry, "  ")
    return "\n".join(lines) + "\n"


# ── Note resolution ───────────────────────────────────────────────────────────

def plan_resolutions(
    patches_by_id: dict[str, dict], checked: set[str], applied: set[str]
) -> tuple[list[dict], list[dict]]:
    """Returns (resolvable entries, entries that stay open).

    A note is resolvable once every patch that lists it in `resolves` is checked
    and applied; it stays open while any of them is unchecked or failed.
    """
    ids: list[str] = []
    for pid in sorted(checked):
        for entry in patches_by_id[pid].get("resolves", []):
            if entry["id"] not in ids:
                ids.append(entry["id"])

    resolvable: list[dict] = []
    stay_open: list[dict] = []
    for nid in ids:
        listing = sorted(
            pid for pid, p in patches_by_id.items()
            if any(e["id"] == nid for e in p.get("resolves", []))
        )
        blockers = [pid for pid in listing if pid not in applied]
        if blockers:
            stay_open.append({
                "id": nid,
                "state": "open",
                "reason": "patch not applied: " + ", ".join(blockers),
            })
            continue
        entry = next(e for e in patches_by_id[listing[0]]["resolves"] if e["id"] == nid)
        resolvable.append({"id": nid, "status": entry["status"], "resolution": entry["resolution"]})
    return resolvable, stay_open


def resolve_notes(resolvable: list[dict], concept_root: Path, run: bool = True) -> list[dict]:
    """Close the notes through the mockup package's resolve.ts; record what could not run.
    With `run=False` nothing is closed: every note comes back `pending` with its command."""
    package_dir = concept_root / PACKAGE_DIR
    tsx = package_dir / "node_modules" / ".bin" / "tsx"
    script = package_dir / "scripts" / "resolve.ts"
    installed = tsx.is_file() and script.is_file()
    execute = run and installed

    groups: dict[tuple[str, str], list[str]] = {}
    for entry in resolvable:
        groups.setdefault((entry["status"], entry["resolution"]), []).append(entry["id"])

    out: list[dict] = []
    for (status, resolution), ids in groups.items():
        args = ["--ids", ",".join(ids), "--status", status, "--resolution", resolution]
        command = f"cd {shlex.quote(str(package_dir))} && " + ("" if installed else "npm install && ") + (
            "npx tsx scripts/resolve.ts " + " ".join(shlex.quote(a) for a in args)
        )
        error = None
        if execute:
            try:
                r = subprocess.run(
                    [str(tsx.resolve()), "scripts/resolve.ts"] + args,
                    cwd=package_dir, capture_output=True, text=True, timeout=60,
                )
                if r.returncode != 0:
                    tail = [l.strip() for l in (r.stderr or r.stdout).splitlines() if l.strip()][-3:]
                    error = " | ".join(tail)[:400] or f"resolve.ts exited {r.returncode}"
            except (OSError, subprocess.TimeoutExpired) as exc:
                error = f"resolve.ts could not run: {exc}"
        for nid in ids:
            base = {"id": nid, "status": status, "resolution": resolution}
            if execute and error is None:
                out.append({**base, "state": "resolved"})
            else:
                rec = {**base, "state": "pending", "command": command}
                if error:
                    rec["error"] = error
                out.append(rec)
    return out


# ── Devlog ────────────────────────────────────────────────────────────────────

def build_devlog_block(round_id: str, items: list[dict]) -> str:
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    by_file: dict[str, list[dict]] = {}
    for item in items:
        if item["status"] == "applied":
            f = item["target"]["file"]
            by_file.setdefault(f, []).append(item)

    lines = [f"\n## {today} · round {round_id}\n"]
    for f, file_items in by_file.items():
        lines.append(f"### {f}\n")
        for item in file_items:
            cat = item["target"].get("category") or item["kind"]
            body = (item.get("body") or "")[:80]
            lines.append(f"- {item['patchId']} applied ({cat}): {body!r}\n")
        lines.append("\n")
    return "".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def check_resolves(patch: dict) -> str | None:
    resolves = patch.get("resolves")
    if not isinstance(resolves, list) or not resolves:
        return f"patch {patch['id']!r} has no resolves[]"
    if patch.get("inboxId") not in {e.get("id") for e in resolves if isinstance(e, dict)}:
        return f"patch {patch['id']!r}: resolves[] does not list its own inboxId"
    for e in resolves:
        if not isinstance(e, dict) or e.get("status") not in ("implemented", "rejected"):
            return f"patch {patch['id']!r}: resolves[].status must be implemented or rejected"
        if not str(e.get("resolution", "")).strip():
            return f"patch {patch['id']!r}: resolves[].resolution must be non-empty"
    return None


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

    rid = patches_data.get("roundId", "unknown")
    applied_path = feedback_root / "applied" / f"{rid}.json"
    devlog_path  = feedback_root / "devlog.md"

    # Pre-flight: idempotency
    if applied_path.exists() and not force:
        print(
            f"ERROR: round {rid!r} already applied "
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
    for pid in sorted(checked_ids):
        err = check_resolves(patches_by_id[pid])
        if err:
            print(f"ERROR: {err}", file=sys.stderr)
            return 1

    # Load all files the content patches edit (in-memory); a proposal edits no file
    file_contents: dict[str, str | None] = {}
    for pid in checked_ids:
        if patches_by_id[pid].get("kind") == "proposal":
            continue
        rel = patches_by_id[pid]["file"]
        if rel not in file_contents:
            fp = concept_root / rel
            file_contents[rel] = fp.read_text(encoding="utf-8") if fp.is_file() else None

    # The round's proposal file; written only when a proposal is approved and valid
    proposed_on = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    scope = proposal_scope(rid)
    proposals_file = proposal_path(concept_root, proposed_on, scope)
    proposals_rel = proposals_file.relative_to(concept_root).as_posix()
    entries: list[dict] = []

    # Apply patches best-effort (deterministic order by patch ID)
    applied_items: list[dict] = []
    n_applied = 0
    n_failed  = 0

    for pid in sorted(checked_ids):
        patch = patches_by_id[pid]
        base  = {"inboxId": patch["inboxId"], "patchId": pid, "kind": patch["kind"]}
        body  = {"body": patch.get("body", "")}

        if patch["kind"] == "proposal":
            entry_id = f"p{len(entries) + 1}"
            proposes = {"target": patch.get("target"), "anchor": patch.get("anchor")}
            err = check_proposal(patch)
            if err:
                applied_items.append({**base, "target": {"file": proposals_rel, "section": None, "category": None},
                                      "proposes": proposes, **body, "status": "failed", "error": err})
                n_failed += 1
                continue
            entries.append({"id": entry_id, "target": patch["target"], "anchor": patch["anchor"],
                            "payload": patch["payload"], "source": patch["source"], "status": "proposed"})
            applied_items.append({**base, "target": {"file": proposals_rel, "section": entry_id, "category": None},
                                  "proposes": proposes, **body, "status": "applied"})
            n_applied += 1
            continue

        rel     = patch["file"]
        content = file_contents.get(rel)
        item_base = {
            **base,
            "target": {
                "file":     rel,
                "section":  patch["section"],
                "category": patch.get("category"),
            },
            **body,
        }

        if rel == MODEL_FILE:
            applied_items.append({**item_base, "status": "failed",
                                  "error": f"{MODEL_FILE} takes proposals only (kind: proposal)"})
            n_failed += 1
            continue

        if content is None:
            applied_items.append({**item_base, "status": "failed", "error": f"file not found: {rel}"})
            n_failed += 1
            continue

        new_content, err = apply_diff(content, patch["diff"])
        if err:
            applied_items.append({**item_base, "status": "failed", "error": err})
            n_failed += 1
        else:
            file_contents[rel] = new_content
            applied_items.append({**item_base, "status": "applied"})
            n_applied += 1

    if n_applied == 0:
        print(
            f"ERROR: all {n_failed} patch(es) failed — no artifacts written. "
            "The round can be retried without --force after fixing the patches.",
            file=sys.stderr,
        )
        for item in applied_items:
            if item["status"] == "failed":
                print(f"  FAILED {item['patchId']}: {item.get('error')}", file=sys.stderr)
        return 2

    if dry_run:
        print(
            f"DRY-RUN: {n_applied} would be applied, {n_failed} would fail "
            "(note resolution not run)"
        )
        return 0

    # Disk writes, each remembered so a later failure restores the tree exactly.
    before: dict[Path, bytes | None] = {}

    def track(path: Path) -> None:
        if path not in before:
            before[path] = path.read_bytes() if path.is_file() else None

    def write_text(path: Path, text: str) -> None:
        track(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def restore_all() -> None:
        for path, data in before.items():
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(data)

    # Edited files, then the round's proposal file; no owner artifact is touched by a proposal
    files_with_applied = {
        item["target"]["file"] for item in applied_items if item["status"] == "applied"
    }
    for rel, content in file_contents.items():
        if rel in files_with_applied and content is not None:
            write_text(concept_root / rel, content)
    if entries:
        write_text(proposals_file, proposal_file_text(proposed_on, scope, entries))

    # The notes this round answers; they are closed only once the round is committed, so a failed
    # commit never leaves a note resolved for a change that is not in the history.
    applied_pids = {i["patchId"] for i in applied_items if i["status"] == "applied"}
    resolvable, stay_open = plan_resolutions(patches_by_id, checked_ids, applied_pids)

    def applied_record(resolutions: list[dict]) -> str:
        return json.dumps({
            "roundId":     rid,
            "appliedAt":   applied_at,
            "items":       [{k: v for k, v in i.items() if k != "kind"} for i in applied_items],
            "resolutions": sorted(resolutions, key=lambda r: r["id"]),
        }, indent=2)

    # Devlog and applied record; the record names every answered note `pending` until resolved
    applied_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    write_text(devlog_path, (devlog_path.read_text(encoding="utf-8") if devlog_path.exists() else "")
               + build_devlog_block(rid, applied_items))
    planned = resolve_notes(resolvable, concept_root, run=False)
    write_text(applied_path, applied_record(planned + stay_open))

    # Stage + commit
    files_to_stage = [str(p) for p in before if p.exists()]
    commit_msg = f"feedback: apply round {rid} ({n_applied} applied, {n_failed} failed)"
    staged = subprocess.run(["git", "add"] + files_to_stage, capture_output=True, text=True)
    result = staged if staged.returncode != 0 else subprocess.run(
        ["git", "commit", "-m", commit_msg], capture_output=True, text=True
    )

    if result.returncode != 0:
        subprocess.run(["git", "reset", "-q", "--"] + files_to_stage, check=False, capture_output=True)
        restore_all()
        print("ERROR: git commit failed — working tree restored, no note resolved.", file=sys.stderr)
        print(result.stdout + result.stderr, file=sys.stderr)
        return 1

    # Close the answered notes, then amend the record with what the inbox answered
    resolutions = resolve_notes(resolvable, concept_root) + stay_open
    if any(r["state"] == "resolved" for r in resolutions):
        applied_path.write_text(applied_record(resolutions), encoding="utf-8")
        subprocess.run(["git", "add", str(applied_path)], check=False, capture_output=True)
        subprocess.run(["git", "commit", "-q", "--amend", "--no-edit"], check=False, capture_output=True)

    print(f"Applied {n_applied} patch(es), {n_failed} failed; round {rid!r} committed")
    if entries:
        print(f"PROPOSED {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} in {proposals_rel}; "
              "the target owners settle them")
    for r in sorted(resolutions, key=lambda r: r["id"]):
        if r["state"] == "resolved":
            print(f"RESOLVED note {r['id']}: {r['status']}")
        elif r["state"] == "pending":
            print(f"PENDING resolution of {r['id']}: run  {r['command']}")
        elif r["state"] == "open":
            print(f"OPEN note {r['id']}: {r['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
