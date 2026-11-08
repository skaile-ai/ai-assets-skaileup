#!/usr/bin/env python3
"""apply.py — mockup-feedback-apply deterministic patcher.

Parses the review.md checklist, applies the approved patches to _concept/ files
(best-effort), checks model.yaml with `@skaile/model` when it changed, resolves
the answered notes in the annotation inbox, appends the devlog, writes
applied/<round-id>.json and creates one git commit.

Usage:
  python apply.py <patches-json> <review-md> <concept-root> <feedback-root> [--force] [--dry-run]

Anchors a diff header may carry (`@@ <anchor> @@`):
  ## Heading             markdown section; removes match a consecutive block, no removes append
  frontmatter:elements   removes/adds inside the file's YAML frontmatter
  before:## Heading      adds inserted right above that heading line
  yaml:entity/<Id>/fields  adds only: one-line field entries `      <name>: { … }`, inserted
                           after the last line of that entity's `    fields:` block in model.yaml
  yaml:model/entities      adds only: one new entity block starting `  <Id>:`, inserted after
                           the last line of the top-level `entities:` block in model.yaml

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
import shutil
import subprocess
import sys
from pathlib import Path

DATAMODEL_DIR = "10_blueprint/datamodel"
MODEL_FILE = f"{DATAMODEL_DIR}/model.yaml"
PACKAGE_DIR = "09_mockup/storybook"
PROPOSAL_BY = "by: mockup-feedback"


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
    if anchor.startswith("yaml:entity/") and anchor.endswith("/fields"):
        return _add_entity_fields(file_content, anchor[len("yaml:entity/"):-len("/fields")], removes, adds)
    if anchor == "yaml:model/entities":
        return _add_entity(file_content, removes, adds)
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


# ── model.yaml anchors (format fixed by tree/10_blueprint/datamodel/model.md) ─

def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _block_end(lines: list[str], start: int, indent: int) -> int:
    """Index after the last content line of the block opened at `start`: every following line
    indented deeper than `indent`, blank and comment lines included only when content follows."""
    end = start + 1
    for i in range(start + 1, len(lines)):
        text = lines[i].strip()
        if not text or text.startswith("#"):
            continue
        if _indent(lines[i]) <= indent:
            break
        end = i + 1
    return end


def _entities_block(lines: list[str]) -> int | None:
    return next((i for i, l in enumerate(lines) if l.rstrip() == "entities:"), None)


def _entity_at(lines: list[str], ents_at: int, entity: str) -> int | None:
    end = _block_end(lines, ents_at, 0)
    return next((i for i in range(ents_at + 1, end) if re.match(rf"^  {re.escape(entity)}:\s*(#.*)?$", lines[i])), None)


def _check_proposal(text: str, what: str) -> str | None:
    if "proposed: {" not in text or PROPOSAL_BY not in text:
        return f"{what} lacks the proposal marker `proposed: {{ {PROPOSAL_BY}, on: <date>, source: <inboxId> }}`"
    return None


def _with_newline(lines: list[str], at: int) -> list[str]:
    """`lines[:at]` with a final newline, so text inserted after the file's last line stays apart."""
    head = lines[:at]
    if head and not head[-1].endswith("\n"):
        head[-1] += "\n"
    return head


def _add_entity_fields(content: str, entity: str, removes: list[str], adds: list[str]) -> tuple[str, str | None]:
    if removes:
        return content, "model proposal takes adds only"
    if not adds:
        return content, "model proposal has no add lines"
    for line in adds:
        if not re.match(r"^      \w+: \{.*\}$", line):
            return content, f"field line does not match `      <name>: {{ type: …, proposed: {{ … }} }}`: {line!r}"
        err = _check_proposal(line, "field line")
        if err:
            return content, err

    lines = content.splitlines(keepends=True)
    ents_at = _entities_block(lines)
    if ents_at is None:
        return content, "top-level `entities:` block not found in model.yaml"
    start = _entity_at(lines, ents_at, entity)
    if start is None:
        return content, f"entity not found in model.yaml: {entity}"
    end = _block_end(lines, start, 2)
    fields_at = next((i for i in range(start + 1, end) if lines[i].rstrip() == "    fields:"), None)
    if fields_at is None:
        return content, f"block `    fields:` not found in entity {entity}"
    close = _block_end(lines, fields_at, 4)

    existing = {m.group(1) for l in lines[fields_at + 1:close] if (m := re.match(r"^      (\w+):", l))}
    for line in adds:
        name = re.match(r"^      (\w+):", line).group(1)  # type: ignore[union-attr]
        if name in existing:
            return content, f"field already exists in {entity}: {name}"
        existing.add(name)

    new_lines = _with_newline(lines, close) + [a + "\n" for a in adds] + lines[close:]
    return "".join(new_lines), None


def _add_entity(content: str, removes: list[str], adds: list[str]) -> tuple[str, str | None]:
    if removes:
        return content, "model proposal takes adds only"
    block = list(adds)
    while block and not block[-1].strip():
        block.pop()
    if not block:
        return content, "model proposal has no add lines"
    m = re.match(r"^  (\w+):$", block[0])
    if not m or any(l.strip() and _indent(l) <= 2 for l in block[1:]):
        return content, "entity block must start `  <Id>:` and indent every further line deeper"
    entity = m.group(1)
    if not any(re.match(r"^    proposed: \{", l) for l in block[1:]):
        return content, "entity block lacks its entity-level `    proposed: { … }` line"
    err = _check_proposal("\n".join(block), "entity block")
    if err:
        return content, err

    lines = content.splitlines(keepends=True)
    ents_at = _entities_block(lines)
    if ents_at is None:
        return content, "top-level `entities:` block not found in model.yaml"
    if _entity_at(lines, ents_at, entity) is not None:
        return content, f"entity already exists in model.yaml: {entity}"
    close = _block_end(lines, ents_at, 0)

    new_lines = _with_newline(lines, close) + [b + "\n" for b in block] + lines[close:]
    return "".join(new_lines), None


# ── Review.md parsing ─────────────────────────────────────────────────────────

def parse_checked_ids(review_md: str) -> set[str]:
    return set(re.findall(r"- \[x\] \*\*([^*]+)\*\*", review_md))


# ── Data-model check ─────────────────────────────────────────────────────────

MODEL_TOOL = "@skaile/model@1"
MODEL_TOOL_TIMEOUT = 180


class ModelToolError(Exception):
    """`@skaile/model` could not be run at all; the message says why."""


def run_model_tool(command: str, datamodel: Path) -> subprocess.CompletedProcess:
    """`bunx @skaile/model@1 <command> <dir>` (`npx --yes` without Bun), run to the end; raises
    `ModelToolError` when neither runner is on PATH or the run outlasts `MODEL_TOOL_TIMEOUT` seconds."""
    if shutil.which("bunx"):
        runner = ["bunx"]
    elif shutil.which("npx"):
        runner = ["npx", "--yes"]
    else:
        raise ModelToolError(f"neither `bunx` (Bun) nor `npx` (Node) is on PATH to run `{MODEL_TOOL} {command}`")
    try:
        return subprocess.run([*runner, MODEL_TOOL, command, str(datamodel)],
                              capture_output=True, text=True, timeout=MODEL_TOOL_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise ModelToolError(f"`{MODEL_TOOL} {command}` did not finish within {MODEL_TOOL_TIMEOUT} s") from None


def run_check(datamodel_dir: Path) -> str | None:
    """Run `@skaile/model@1 check` on the datamodel directory. Returns its output on failure, else None."""
    try:
        result = run_model_tool("check", datamodel_dir)
    except ModelToolError as exc:
        return f"{MODEL_TOOL} check could not run: {exc}"
    if result.returncode == 0:
        return None
    out = "\n".join(l.rstrip() for l in (result.stdout + result.stderr).splitlines() if l.strip())
    return out or f"{MODEL_TOOL} check exited {result.returncode}"


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

    # Load all files that will be edited (in-memory)
    file_contents: dict[str, str | None] = {}
    for pid in checked_ids:
        rel = patches_by_id[pid]["file"]
        if rel not in file_contents:
            fp = concept_root / rel
            file_contents[rel] = fp.read_text(encoding="utf-8") if fp.is_file() else None
    originals = dict(file_contents)

    # Apply patches best-effort (deterministic order by patch ID)
    applied_items: list[dict] = []
    n_applied = 0
    n_failed  = 0

    for pid in sorted(checked_ids):
        patch   = patches_by_id[pid]
        rel     = patch["file"]
        content = file_contents.get(rel)

        item_base = {
            "inboxId": patch["inboxId"],
            "patchId": pid,
            "kind":    patch["kind"],
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

        new_content, err = apply_diff(content, patch["diff"])
        if err:
            applied_items.append({**item_base, "status": "failed", "error": err})
            n_failed += 1
        else:
            file_contents[rel] = new_content
            applied_items.append({**item_base, "status": "applied"})
            n_applied += 1

    def short_circuit() -> int:
        print(
            f"ERROR: all {n_failed} patch(es) failed — no artifacts written. "
            "The round can be retried without --force after fixing the diffs.",
            file=sys.stderr,
        )
        for item in applied_items:
            if item["status"] == "failed":
                print(f"  FAILED {item['patchId']}: {item.get('error')}", file=sys.stderr)
        return 2

    if n_applied == 0:
        return short_circuit()

    if dry_run:
        print(
            f"DRY-RUN: {n_applied} would be applied, {n_failed} would fail "
            "(model check and note resolution not run)"
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

    # model.yaml first: `@skaile/model check` must accept it, otherwise the proposals fail and the
    # file is restored byte for byte.
    datamodel_dir = concept_root / DATAMODEL_DIR
    model_ids = {i["patchId"] for i in applied_items if i["status"] == "applied" and i["target"]["file"] == MODEL_FILE}
    checked_model = False
    if model_ids:
        write_text(concept_root / MODEL_FILE, file_contents[MODEL_FILE])  # type: ignore[arg-type]
        check_err = run_check(datamodel_dir)
        if check_err:
            restore_all()
            before.clear()
            file_contents[MODEL_FILE] = originals[MODEL_FILE]
            print(f"@skaile/model check rejected model.yaml; restored it:\n{check_err}", file=sys.stderr)
            for item in applied_items:
                if item["patchId"] in model_ids:
                    item["status"] = "failed"
                    item["error"] = f"@skaile/model check rejected model.yaml: {check_err}"
                    n_applied -= 1
                    n_failed += 1
            if n_applied == 0:
                return short_circuit()
        else:
            checked_model = True

    # Remaining edited files
    files_with_applied = {
        item["target"]["file"] for item in applied_items if item["status"] == "applied"
    }
    for rel, content in file_contents.items():
        if rel in files_with_applied and rel != MODEL_FILE and content is not None:
            write_text(concept_root / rel, content)

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
    if checked_model:
        print("@skaile/model check accepted model.yaml")
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
