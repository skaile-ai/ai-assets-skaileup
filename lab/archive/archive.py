#!/usr/bin/env python3
"""archive.py — roll up old _feedback/devlog.md entries into quarterly archive files.

Parses devlog entries (## YYYY-MM-DD · blocks), keeps the most recent KEEP_COUNT
in devlog.md, and moves older entries verbatim into
_feedback/devlog.archive/<YYYY>-QN.md files grouped by calendar quarter.

Trigger: run when devlog.md entry count >= TRIGGER_COUNT.

Run from repo root:
  python3 lab/archive/archive.py

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

# Splits on blank line before ## YYYY-MM-DD · entries
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
    to_archive = entries[keep_count:]  # older entries

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
