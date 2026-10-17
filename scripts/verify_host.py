#!/usr/bin/env python3
"""verify_host.py — grep the host facts against real checkouts.

`scripts/host_facts.py` is what `check.py`'s host-derived rules rest on. This is the
thing that makes that coupling **tested rather than asserted**: point it at the
super-repo holding the sibling checkouts and it greps every signature, honouring
`expect`, and reports **holds** or **expired** per fact.

Manual by design, and deliberately not in push CI: the hosts are absent there, and a
scheduled job that checks out three repos is more machinery than a fact set that changed
zero times in two weeks deserves. Run it when a host moves, or before trusting a
host-derived failure from `check.py`.

Usage:
  python scripts/verify_host.py [--hosts <super-repo root>] [--update] [--fact <id>]

  --update   rewrite `verified:` and the advisory `seen_at` line numbers in
             host_facts.py, but only after a completely clean run. The dates rot the
             way the line numbers did if nothing writes them back.

Exit codes:
  0  every fact holds
  1  at least one expired, or a host checkout is missing
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from host_facts import ABSENT, FACTS, HOSTS, Fact  # noqa: E402

TABLE = Path(__file__).resolve().parent / "host_facts.py"

HOLDS = "holds"
EXPIRED = "expired"


def default_hosts_root() -> Path:
    """The super-repo this collection is a submodule of: `<root>/ai-assets/<repo>/scripts`."""
    return Path(__file__).resolve().parents[3]


def _hits(text: str, signature: str) -> list[int]:
    """1-based line numbers containing `signature` verbatim."""
    return [i for i, line in enumerate(text.splitlines(), 1) if signature in line]


def check_fact(f: Fact, hosts_root: Path) -> tuple[str, str, list[int]]:
    """`(verdict, detail, line hits)` for one fact."""
    host_dir = HOSTS.get(f.host)
    if host_dir is None:
        return EXPIRED, f"unknown host {f.host!r}", []
    path = hosts_root / host_dir / f.path
    if not path.is_file():
        return EXPIRED, f"no such file: {host_dir}/{f.path}", []

    hits = _hits(path.read_text(encoding="utf-8", errors="replace"), f.signature)
    if f.expect == ABSENT:
        if hits:
            return EXPIRED, f"expected absent, found at {_fmt(hits)} — the ban this backs is now wrong", hits
        return HOLDS, "absent, as expected", []
    if not hits:
        return EXPIRED, "signature not found — the fact moved or died", []
    return HOLDS, f"found at {_fmt(hits)}", hits


def _fmt(hits: list[int]) -> str:
    return ", ".join(f"L{n}" for n in hits)


# --------------------------------------------------------------------------
# --update: the only writer of `verified:` and `seen_at`
# --------------------------------------------------------------------------

ID_RE = re.compile(r'^\s*id="(?P<id>[^"]+)",\s*$')
VERIFIED_RE = re.compile(r'^(?P<indent>\s*)verified="[^"]*",\s*$')
SEEN_AT_RE = re.compile(r'^(?P<indent>\s*)seen_at="[^"]*",\s*$')


def rewrite_table(seen: dict[str, list[int]], today: str) -> int:
    """Refresh `verified:` and `seen_at` in place. Returns the number of rows touched."""
    lines = TABLE.read_text().splitlines(keepends=True)
    out: list[str] = []
    current: str | None = None
    touched: set[str] = set()

    for line in lines:
        m = ID_RE.match(line)
        if m:
            current = m.group("id")
        elif current in seen:
            v = VERIFIED_RE.match(line)
            if v:
                out.append(f'{v.group("indent")}verified="{today}",\n')
                touched.add(current)
                continue
            s = SEEN_AT_RE.match(line)
            if s:
                out.append(f'{s.group("indent")}seen_at="{_fmt(seen[current])}",\n')
                continue
        out.append(line)

    TABLE.write_text("".join(out))
    return len(touched)


def main() -> int:
    parser = argparse.ArgumentParser(description="Grep the host facts against local checkouts.")
    parser.add_argument(
        "--hosts",
        default=None,
        help=f"super-repo root holding {', '.join(sorted(HOSTS.values()))} (default: {default_hosts_root()})",
    )
    parser.add_argument("--fact", default=None, help="verify one fact id only")
    parser.add_argument(
        "--update",
        action="store_true",
        help="after a clean run, rewrite `verified:` and the advisory `seen_at` line numbers",
    )
    args = parser.parse_args()

    hosts_root = Path(args.hosts).resolve() if args.hosts else default_hosts_root()
    facts = [f for f in FACTS if args.fact is None or f.id == args.fact]
    if not facts:
        print(f"no fact matches {args.fact!r}")
        return 1

    # Only hosts that actually back a fact matter here. `HOSTS` also lists `platform`,
    # which no rule rests on today, and warning about its absence on every clean run is
    # noise that trains the reader to skim the warnings that do mean something.
    needed = {HOSTS[f.host] for f in facts}
    missing = sorted(d for d in needed if not (hosts_root / d).is_dir())
    print(f"hosts root: {hosts_root}")
    for d in missing:
        print(f"  WARNING no checkout at {d} — every fact of that host reads as expired")
    print()

    seen: dict[str, list[int]] = {}
    expired: list[tuple[Fact, str]] = []
    for f in sorted(facts, key=lambda f: (f.host, f.path, f.id)):
        verdict, detail, hits = check_fact(f, hosts_root)
        print(f"{verdict:8} {f.id}")
        print(f"         {f.host}/{f.path} — {detail}")
        if verdict == HOLDS:
            seen[f.id] = hits
        else:
            expired.append((f, detail))

    print(f"\n{len(facts)} fact(s) · {len(expired)} expired")

    if expired:
        print("\nEach expired fact leaves its rules unowned. Either the host moved (update the")
        print("signature and re-verify) or the fact died (delete the rules resting on it):")
        for f, detail in expired:
            print(f"  {f.id} — rules: {', '.join(f.rules)}")
        return 1

    if args.update:
        today = _dt.date.today().isoformat()
        touched = rewrite_table(seen, today)
        print(f"\nupdated {touched} row(s): verified={today}, seen_at refreshed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
