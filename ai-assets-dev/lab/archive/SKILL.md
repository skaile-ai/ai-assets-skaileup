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
- Before a major collection regeneration pass (to keep agent context lean)
- As routine quarterly maintenance

**Not needed when:**
- The devlog is under 500 entries

## Invariants

- **Lossless.** Every entry is either kept in `devlog.md` or written verbatim to an archive file — nothing is deleted or summarized.
- **Idempotent.** Running twice does not duplicate entries; the second run sees fewer than 500 entries and exits early.
- **Append-safe.** Archive files accumulate across runs; existing archive content is preserved and deduplication prevents double-writes.
- **Atomic writes.** Each file is written to a `.tmp` sibling then renamed, so a crash mid-run leaves no corrupt files.
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
python3 lab/archive/archive.py
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
