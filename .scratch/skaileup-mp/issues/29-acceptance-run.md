# 29: The acceptance run — install `-mp` and get the flows loading green

**Type:** task
**Blocked by:** None — 28 resolved 2026-09-05
**Status:** ready (needs `-mp` `main` pushed first — see 28)

## Question

Graduated from the map's "Opt-in mechanics and the acceptance test" fog patch, which ticket 10
made specifiable by fixing the flow list.

This is the map's destination: **one real project installs `-mp` and its flows load green.**

Decide and do:

- **Which project plays the role.** `forge-concept` is the natural candidate — it owns the
  integration test — but the map's parallel/opt-in premise says nothing cuts over, so the
  install must be additive.
- **Opt-in mechanics**: how a project points at `-mp` in `skaile.yaml` (`sources:` +
  `dependencies:`), and what lockfile state that produces.
- **Run it.** `WorkspaceService.install()` → deploy under `.skaile/flows` + `.claude/skills`
  → `loadFlowsFromDir` parses all four. Green means: four flows discovered and parsed, every
  `data.skill` resolving to a deployed skill directory.

Note the host cannot help here: **`validateFlow` / `FlowManifestSchema` have zero call sites**
in forge-concept, a `data.skill` resolving to nothing does **not** raise
(`run.post.ts:78-80` falls back to a generic prompt; `requirements.get.ts:37-48` returns a
fabricated `satisfied: true`). So "loads green" in the host is a weak signal by construction —
`scripts/check.py` (ticket 16) is the real gate, and this ticket should say so rather than
trusting a silent pass.

## Answer

_(pending)_
