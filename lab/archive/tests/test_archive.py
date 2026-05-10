"""Tests for archive.py — devlog quarterly rollup logic."""
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

    # File unchanged (still 10 entries)
    assert len(parse_entries(devlog.read_text())[1]) == 10
    assert not archive_dir.exists()


def test_main_archives_old_entries_when_over_threshold(tmp_path):
    devlog = tmp_path / "devlog.md"
    # 300 entries over a threshold of 100, keep 50
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

    # Total archived = 300 - 50 = 250
    total_archived = 0
    for f in archive_files:
        _, archived = parse_entries(f.read_text())
        total_archived += len(archived)
    assert total_archived == 250


def test_main_keeps_newest_entries_in_devlog(tmp_path):
    devlog = tmp_path / "devlog.md"
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
