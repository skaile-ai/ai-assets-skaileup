# `lab/archive` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `lab/archive` skill — a Python dev-tool that rolls up old entries from `_feedback/devlog.md` into quarterly archive files when the total entry count reaches 500, keeping the live devlog lean.

**Architecture:** A single `archive.py` script parses the devlog's `## YYYY-MM-DD ·` entries, keeps the most recent 200 in `devlog.md`, and moves older entries verbatim into `_feedback/devlog.archive/<YYYY>-QN.md` files grouped by calendar quarter. No LLM calls; no external deps beyond Python stdlib.

**Tech Stack:** Python 3.12+ stdlib only. pytest for tests.

**Spec references:**
- `REFACTOR_MOCKUP.md §5` — devlog format and append protocol
- `docs/devlog/2026-05-07-skill-graph-migration.md` Task 3E — trigger and output spec

**Working directory:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

---

## Devlog format (source of truth: REFACTOR_MOCKUP.md §5)

```markdown
# Feedback Devlog

## 2026-05-06 · session abc123 · astro walkthrough
**Reviewer:** stakeholder · **Cumulative scope:** auth, dashboard

### experience/screens/auth/login.md
- submit-button moved to right side per layout convention
  (target: submit-button, comment: "should be on the right")

## 2026-05-04 · session xyz789 · static-html walkthrough
**Reviewer:** stakeholder · **Cumulative scope:** auth

### product-spec/features/01_auth/login.md
- added acceptance criterion: tab order email → password → submit
```

- Each **entry** is a block starting with `## YYYY-MM-DD ·` and ending just before the next such line.
- The file header is everything before the first `## YYYY-MM-DD ·` line (the `# Feedback Devlog` title).
- Entries are newest-first (apply skill prepends each new entry at the top).
- An "entry count" is the number of `## YYYY-MM-DD ·` lines in the file.

---

## File map

| File | Action | Responsibility |
|---|---|---|
| `lab/archive/archive.py` | Create | Core logic: parse devlog, split by keep/archive, write quarterly archive files, rewrite devlog |
| `lab/archive/tests/test_archive.py` | Create | Unit tests for parsing, quarter assignment, split logic, file I/O |
| `lab/archive/SKILL.md` | Create | Agent prompt: when to run, steps, MUST/NEVER |
| `lab/DOMAIN.md` | Modify | Add `lab-archive` to Skills list |

---

## Task 1: Write `archive.py` + tests

**Files:**
- Create: `lab/archive/archive.py`
- Create: `lab/archive/tests/test_archive.py`

- [ ] **Step 1.1: Create directories and write failing tests**

```bash
mkdir -p lab/archive/tests
```

Write `lab/archive/tests/test_archive.py`:

```python
"""Tests for archive.py — devlog rollup logic."""
from __future__ import annotations

import sys
from pathlib import Path
from datetime import date

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from archive import parse_entries, quarter_key, main as archive_main


# ── Helpers ──────────────────────────────────────────────────────────

HEADER = "# Feedback Devlog\n\n"

def make_entry(date_str: str, session: str = "s1", body: str = "- some change") -> str:
    return (
        f"## {date_str} · session {session} · walkthrough\n"
        f"**Reviewer:** tester · **Cumulative scope:** auth\n\n"
        f"### experience/screens/auth/login.md\n"
        f"{body}\n"
    )

def make_devlog(entries: list[str]) -> str:
    """Build a devlog string with header + given entries (newest-first)."""
    return HEADER + "\n\n".join(entries) + "\n"


# ── parse_entries ──────────────────────────────────────────────────────

def test_parse_entries_returns_header_and_list():
    text = make_devlog([make_entry("2026-05-06"), make_entry("2026-05-04")])
    header, entries = parse_entries(text)
    assert "# Feedback Devlog" in header
    assert len(entries) == 2


def test_parse_entries_extracts_dates_correctly():
    text = make_devlog([make_entry("2026-05-06"), make_entry("2026-04-01")])
    _, entries = parse_entries(text)
    dates = [e[0] for e in entries]
    assert date(2026, 5, 6) in dates
    assert date(2026, 4, 1) in dates


def test_parse_entries_sorts_newest_first():
    # Even if file order is mixed, result should be newest-first
    text = make_devlog([make_entry("2026-04-01"), make_entry("2026-05-06")])
    _, entries = parse_entries(text)
    assert entries[0][0] == date(2026, 5, 6)
    assert entries[1][0] == date(2026, 4, 1)


def test_parse_entries_empty_devlog_returns_empty_list():
    text = "# Feedback Devlog\n"
    header, entries = parse_entries(text)
    assert entries == []
    assert "# Feedback Devlog" in header


def test_parse_entries_preserves_full_entry_text():
    body = "- moved button right (target: submit-btn, comment: 'alignment')"
    entry = make_entry("2026-05-06", body=body)
    text = make_devlog([entry])
    _, entries = parse_entries(text)
    assert body in entries[0][1]


# ── quarter_key ───────────────────────────────────────────────────────

def test_quarter_key_q1():
    assert quarter_key(date(2026, 1, 15)) == "2026-Q1"
    assert quarter_key(date(2026, 3, 31)) == "2026-Q1"

def test_quarter_key_q2():
    assert quarter_key(date(2026, 4, 1)) == "2026-Q2"
    assert quarter_key(date(2026, 6, 30)) == "2026-Q2"

def test_quarter_key_q3():
    assert quarter_key(date(2026, 7, 1)) == "2026-Q3"
    assert quarter_key(date(2026, 9, 30)) == "2026-Q3"

def test_quarter_key_q4():
    assert quarter_key(date(2026, 10, 1)) == "2026-Q4"
    assert quarter_key(date(2026, 12, 31)) == "2026-Q4"


# ── main (integration) ───────────────────────────────────────────────

def make_entries_list(n: int, base_year: int = 2025) -> list[str]:
    """Generate n entries with dates spread across multiple years/months."""
    entries = []
    for i in range(n):
        year = base_year + i // 12
        month = (i % 12) + 1
        day = 15
        entries.append(make_entry(f"{year}-{month:02d}-{day:02d}", session=f"s{i}"))
    return entries


def test_main_noop_when_under_threshold(tmp_path):
    devlog = tmp_path / "devlog.md"
    entries = make_entries_list(10)
    devlog.write_text(make_devlog(entries), encoding="utf-8")
    archive_dir = tmp_path / "archive"

    archive_main(devlog_path=devlog, archive_dir=archive_dir, trigger_count=500, keep_count=200)

    # File unchanged
    assert len(parse_entries(devlog.read_text())[1]) == 10
    assert not archive_dir.exists()


def test_main_archives_old_entries_when_over_threshold(tmp_path):
    devlog = tmp_path / "devlog.md"
    # 300 entries spanning 2024 and 2025 — over a threshold of 100, keep 50
    entries = make_entries_list(300, base_year=2024)
    devlog.write_text(make_devlog(entries), encoding="utf-8")
    archive_dir = tmp_path / "archive"

    archive_main(devlog_path=devlog, archive_dir=archive_dir, trigger_count=100, keep_count=50)

    # devlog now has exactly 50 entries
    _, kept = parse_entries(devlog.read_text())
    assert len(kept) == 50

    # Archive files exist
    assert archive_dir.exists()
    archive_files = list(archive_dir.glob("*.md"))
    assert len(archive_files) > 0

    # Total archived entries = 300 - 50 = 250
    total_archived = 0
    for f in archive_files:
        _, archived = parse_entries(f.read_text())
        total_archived += len(archived)
    assert total_archived == 250


def test_main_keeps_newest_entries_in_devlog(tmp_path):
    devlog = tmp_path / "devlog.md"
    # 10 entries: 2026-05 through 2025-08 (newest first when sorted)
    entries = [
        make_entry("2026-05-15", session="newest"),
        make_entry("2026-04-15", session="s2"),
        make_entry("2026-03-15", session="s3"),
        make_entry("2026-02-15", session="s4"),
        make_entry("2026-01-15", session="s5"),
        make_entry("2025-12-15", session="s6"),
        make_entry("2025-11-15", session="s7"),
        make_entry("2025-10-15", session="oldest"),
    ]
    devlog.write_text(make_devlog(entries), encoding="utf-8")
    archive_dir = tmp_path / "archive"

    # threshold=5, keep=3 — keeps the 3 newest
    archive_main(devlog_path=devlog, archive_dir=archive_dir, trigger_count=5, keep_count=3)

    remaining_text = devlog.read_text()
    assert "newest" in remaining_text
    assert "oldest" not in remaining_text


def test_main_groups_archived_entries_by_quarter(tmp_path):
    devlog = tmp_path / "devlog.md"
    entries = [
        make_entry("2025-05-15", session="q2"),   # 2025-Q2
        make_entry("2025-04-15", session="q2b"),  # 2025-Q2
        make_entry("2025-01-15", session="q1"),   # 2025-Q1
        make_entry("2024-12-15", session="q4"),   # 2024-Q4
    ]
    devlog.write_text(make_devlog(entries), encoding="utf-8")
    archive_dir = tmp_path / "archive"

    # threshold=2, keep=0 — archive everything
    archive_main(devlog_path=devlog, archive_dir=archive_dir, trigger_count=2, keep_count=0)

    assert (archive_dir / "2025-Q2.md").exists()
    assert (archive_dir / "2025-Q1.md").exists()
    assert (archive_dir / "2024-Q4.md").exists()

    _, q2_entries = parse_entries((archive_dir / "2025-Q2.md").read_text())
    assert len(q2_entries) == 2


def test_main_appends_to_existing_archive_file(tmp_path):
    devlog = tmp_path / "devlog.md"
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()

    # Pre-existing archive file for 2025-Q1
    existing_archive = archive_dir / "2025-Q1.md"
    existing_archive.write_text(
        "# Devlog Archive — 2025-Q1\n\n" + make_entry("2025-03-01", session="old"),
        encoding="utf-8",
    )

    entries = [make_entry("2025-01-15", session="new-q1")]
    devlog.write_text(make_devlog(entries), encoding="utf-8")

    archive_main(devlog_path=devlog, archive_dir=archive_dir, trigger_count=1, keep_count=0)

    content = existing_archive.read_text()
    assert "old" in content
    assert "new-q1" in content


def test_main_exits_0_when_devlog_missing(tmp_path, capsys):
    devlog = tmp_path / "nonexistent.md"
    archive_dir = tmp_path / "archive"
    # Should not raise; should print a message
    archive_main(devlog_path=devlog, archive_dir=archive_dir, trigger_count=500, keep_count=200)
    captured = capsys.readouterr()
    assert "No devlog" in captured.out or "nothing" in captured.out.lower()


def test_main_preserves_devlog_header(tmp_path):
    devlog = tmp_path / "devlog.md"
    entries = make_entries_list(10, base_year=2024)
    devlog.write_text(make_devlog(entries), encoding="utf-8")
    archive_dir = tmp_path / "archive"

    archive_main(devlog_path=devlog, archive_dir=archive_dir, trigger_count=5, keep_count=3)

    content = devlog.read_text()
    assert content.startswith("# Feedback Devlog")
```

- [ ] **Step 1.2: Run tests — verify they fail**

```bash
python -m pytest lab/archive/tests/test_archive.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'archive'`

- [ ] **Step 1.3: Write `archive.py`**

Write `lab/archive/archive.py`:

```python
#!/usr/bin/env python3
"""archive.py — roll up old _feedback/devlog.md entries into quarterly archive files.

Parses devlog entries (## YYYY-MM-DD · blocks), keeps the most recent KEEP_COUNT
in devlog.md, and moves older entries verbatim into
_feedback/devlog.archive/<YYYY>-QN.md files grouped by calendar quarter.

Trigger: run when devlog.md entry count >= TRIGGER_COUNT.

Run from repo root:
  python lab/archive/archive.py

Exit codes:
  0  Completed (entries archived, or under threshold — no action needed)
  1  Internal error
"""
from __future__ import annotations

import re
import sys
from datetime import date, datetime
from pathlib import Path

DEVLOG_PATH = Path("_feedback/devlog.md")
ARCHIVE_DIR = Path("_feedback/devlog.archive")
TRIGGER_COUNT = 500
KEEP_COUNT = 200

# Matches the start of an entry: ## YYYY-MM-DD · (with surrounding blank lines)
_ENTRY_SPLIT_RE = re.compile(r"\n\n(?=## \d{4}-\d{2}-\d{2} ·)")
_ENTRY_DATE_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2}) ·")


def parse_entries(text: str) -> tuple[str, list[tuple[date, str]]]:
    """Parse devlog text into (header, [(entry_date, entry_text), ...]).

    Returns entries sorted newest-first.
    header is everything before the first ## YYYY-MM-DD · entry.
    """
    parts = _ENTRY_SPLIT_RE.split(text)
    header = parts[0]

    entries: list[tuple[date, str]] = []
    for part in parts[1:]:
        m = _ENTRY_DATE_RE.match(part)
        if m:
            entry_date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
            entries.append((entry_date, part))

    entries.sort(key=lambda x: x[0], reverse=True)
    return header, entries


def quarter_key(d: date) -> str:
    """Return the quarter string for a date, e.g. '2026-Q2'."""
    q = (d.month - 1) // 3 + 1
    return f"{d.year}-Q{q}"


def main(
    devlog_path: Path = DEVLOG_PATH,
    archive_dir: Path = ARCHIVE_DIR,
    trigger_count: int = TRIGGER_COUNT,
    keep_count: int = KEEP_COUNT,
) -> None:
    if not devlog_path.exists():
        print(f"No devlog at {devlog_path} — nothing to archive.")
        return

    text = devlog_path.read_text(encoding="utf-8")
    header, entries = parse_entries(text)

    total = len(entries)
    if total < trigger_count:
        print(f"Devlog has {total} entries (< {trigger_count}) — no archival needed.")
        return

    to_keep = entries[:keep_count]
    to_archive = entries[keep_count:]  # older entries (sorted newest-first within group)

    # Group entries to archive by quarter
    by_quarter: dict[str, list[str]] = {}
    for entry_date, entry_text in to_archive:
        key = quarter_key(entry_date)
        by_quarter.setdefault(key, []).append(entry_text)

    # Write (append) to quarterly archive files
    archive_dir.mkdir(parents=True, exist_ok=True)
    for key in sorted(by_quarter):
        entry_texts = by_quarter[key]
        archive_path = archive_dir / f"{key}.md"
        if archive_path.exists():
            existing = archive_path.read_text(encoding="utf-8").rstrip()
            new_content = existing + "\n\n" + "\n\n".join(entry_texts) + "\n"
        else:
            new_content = f"# Devlog Archive — {key}\n\n" + "\n\n".join(entry_texts) + "\n"
        archive_path.write_text(new_content, encoding="utf-8")
        print(f"Archived {len(entry_texts)} entries → {archive_path}")

    # Rewrite devlog.md with kept entries only
    kept_text = header.rstrip() + "\n\n" + "\n\n".join(t for _, t in to_keep) + "\n"
    devlog_path.write_text(kept_text, encoding="utf-8")
    print(
        f"Kept {len(to_keep)} recent entries in {devlog_path} "
        f"(archived {len(to_archive)} across {len(by_quarter)} quarter file(s))."
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 1.4: Run tests — verify all pass**

```bash
python -m pytest lab/archive/tests/test_archive.py -v
```

Expected: all green, 0 failures.

- [ ] **Step 1.5: Commit**

```bash
git add lab/archive/archive.py lab/archive/tests/test_archive.py
git commit -m "feat: add archive.py (devlog quarterly rollup)"
```

---

## Task 2: Write `SKILL.md` and update `lab/DOMAIN.md`

**Files:**
- Create: `lab/archive/SKILL.md`
- Modify: `lab/DOMAIN.md`

- [ ] **Step 2.1: Write `lab/archive/SKILL.md`**

Write `lab/archive/SKILL.md`:

```markdown
---
name: lab-archive
description: "Rolls up old _feedback/devlog.md entries into quarterly archive files when entry count reaches 500. Keeps the 200 most recent entries in the live devlog; moves older ones verbatim to _feedback/devlog.archive/<YYYY>-QN.md."
metadata:
  version: "0.1.0"
  tags:
    - lab
    - devlog
    - archive
    - maintenance
  stage: alpha
  prerequisites:
    reads:
      - path: "_feedback/devlog.md"
        description: "Live devlog — source of entries to roll up"
    produces:
      - path: "_feedback/devlog.md"
        description: "Truncated devlog (most recent 200 entries)"
      - path: "_feedback/devlog.archive"
        description: "Quarterly archive files (<YYYY>-QN.md)"
---

# Archive Devlog

## Overview

When `_feedback/devlog.md` accumulates 500 or more entries, run this skill
to move older entries into quarterly archive files. The live devlog keeps
the 200 most recent entries — enough context for ongoing regeneration work.

**When to run:**
- When `wc -l _feedback/devlog.md` suggests the file has grown very large
- Before a major catalog regeneration pass (to keep agent context lean)
- As routine quarterly maintenance

**Not needed when:**
- The devlog is under 500 entries

## Invariants

- **Lossless.** Every entry is either kept in `devlog.md` or written verbatim to an archive file — nothing is deleted or summarized.
- **Idempotent.** Running twice does not duplicate entries; the second run sees fewer than 500 entries and exits early.
- **Append-safe.** Archive files accumulate across runs; existing archive content is preserved.
- **Header preserved.** The `# Feedback Devlog` title and any intro text are kept in `devlog.md`.

---

ROLE  Devlog archiver — rolls up old feedback entries into quarterly files.

READS
  _feedback/devlog.md     — live devlog; entries with ## YYYY-MM-DD · headers

WRITES
  _feedback/devlog.md                    — rewritten with 200 most recent entries
  _feedback/devlog.archive/<YYYY>-QN.md  — older entries grouped by quarter

REFERENCES
  lab/archive/archive.py — the script this skill runs

## STEPS

STEP 1: Check entry count

```bash
grep -c "^## [0-9]" _feedback/devlog.md 2>/dev/null || echo "0"
```

If count is < 500: report "Devlog is under 500 entries — no archival needed" and stop.

STEP 2: Run the archiver from repo root

```bash
python lab/archive/archive.py
```

Expected output: lines like:
```
Archived N entries → _feedback/devlog.archive/2025-Q4.md
Kept 200 recent entries in _feedback/devlog.md (archived M across K quarter file(s)).
```

STEP 3: Show what changed

```bash
git diff --stat _feedback/devlog.md _feedback/devlog.archive/
```

Show the diff summary to the user.

STEP 4: Commit

```bash
git add _feedback/devlog.md _feedback/devlog.archive/
git commit -m "chore: archive devlog entries (quarterly rollup)"
```

## MUST

- Verify entry count is >= 500 before running (Step 1)
- Show the diff summary (Step 3) before committing
- Commit both devlog.md and the archive directory together

## NEVER

- Delete entries without archiving them first
- Summarize or transform entry content (verbatim move only)
- Run from a directory other than the repo root

## CHECKLIST

- [ ] Entry count checked (>= 500)
- [ ] `archive.py` ran without error (exit 0)
- [ ] Diff summary shown to user
- [ ] Committed with `chore: archive devlog entries (quarterly rollup)`
```

- [ ] **Step 2.2: Update `lab/DOMAIN.md`**

Read `lab/DOMAIN.md` first. Add the `lab-archive` entry after the `lab-compile-bundle` entry in the Skills list:

```markdown
- **lab-archive** (`archive/`) — Rolls up old `_feedback/devlog.md` entries into quarterly archive files when entry count reaches 500. Keeps the 200 most recent in the live devlog.
```

- [ ] **Step 2.3: Verify SKILL.md frontmatter parses correctly**

```bash
python -c "
import yaml
with open('lab/archive/SKILL.md') as f:
    content = f.read()
front = content.split('---')[1]
m = yaml.safe_load(front)
assert m['name'] == 'lab-archive', f'wrong name: {m[\"name\"]}'
assert 'produces' in m['metadata']['prerequisites']
print('SKILL.md frontmatter OK')
"
```

Expected: `SKILL.md frontmatter OK`

- [ ] **Step 2.4: Commit**

```bash
git add lab/archive/SKILL.md lab/DOMAIN.md
git commit -m "feat: add lab-archive SKILL.md and register in DOMAIN.md"
```

---

## Acceptance Criteria

- [ ] `python -m pytest lab/archive/tests/test_archive.py -v` — all tests pass
- [ ] `python lab/archive/archive.py` on a devlog with < 500 entries prints "no archival needed" and exits 0
- [ ] On a devlog with >= 500 entries: older entries appear in `_feedback/devlog.archive/<YYYY>-QN.md`, devlog.md has ≤ 200 entries
- [ ] Running twice on the same devlog (after first pass brings it under 500) is a no-op
- [ ] `lab/archive/SKILL.md` has `name: lab-archive` and correct frontmatter
- [ ] `lab/DOMAIN.md` lists `lab-archive`
