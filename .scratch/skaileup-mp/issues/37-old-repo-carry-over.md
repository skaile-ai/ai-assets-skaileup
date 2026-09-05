# 37: What carries over from the old repo besides skills

**Type:** grilling
**Blocked by:** 35 — the disposition of `docs/` decides where two of these three live
**Status:** blocked

## Question

Graduated from the last fog patch. The port moved skills, flows, contracts and templates.
Three things in the old repo moved nothing, and each is a different question:

- **`docs/devlog/` — 31 files.** A running record of how the old collection was built, dated
  and named per work item (`2A-scope-project.md`, `2026-05-07-skill-graph-migration.md`,
  `forge-concept-walkthrough.md`). `-mp` records decisions in **11 ADRs** instead, a different
  form with a different bar. Does the devlog carry, get mined for ADRs it should have
  produced, or stay in the old repo as its history?
- **The improvement backlog** — `docs/src/content/docs/improvements.mdx`, a page inside the
  Starlight site. Whether it survives at all is downstream of **ticket 35**; whether its
  *content* still applies to a collection one third the size is this ticket's.
- **Git history.** `-mp` was created fresh by ticket 11, so it has none of the old repo's.
  The old repo is not archived (ruled out of scope at charting), so the history stays
  reachable — the question is whether anything needs to be *in* `-mp`.

The map's standing bar applies to all three: this collection has deleted an artifact no one
reads **four times** (`artifacts.yaml`, `data.writes`, `review.yaml`, and the per-file
contract refs). A devlog nobody opens is the same shape of thing — but it is also the only
record of *why* the old collection is what it is, which is exactly what a migration destroys
and cannot re-derive.

Blocked by ticket 35 because two of the three physically live under `docs/`: if the site is
dropped, "carry the devlog" means something different than if it is ported.

## Answer

_(pending)_
