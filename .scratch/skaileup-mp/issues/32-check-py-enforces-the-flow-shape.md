# 32: `check.py` passes flows that break every rule ticket 10 fixed

**Type:** task
**Blocked by:** None — 28 resolved 2026-09-05 and supplied the list

**Status:** ready

## Question

Nothing to decide. Ticket 16 made the collection self-validating and closed with a residue note
asking ticket 10 to expect an adjustment once real flows landed. They landed in ticket 28 —
which then had to verify **every** flow shape rule **by hand**, with an ad-hoc script, because
`scripts/check.py` enforces almost none of them. That hand-verification is the input this
ticket exists to make permanent.

Ticket 29 is the acceptance run, and the map already records that the host is a **weak signal
by construction**: `validateFlow` / `FlowManifestSchema` have zero call sites in forge-concept,
and a `data.skill` resolving to nothing does not raise. `check.py` is the real gate. A gate that
passes a flow carrying `data.parameters` — which still has a live host read — is not one.

Each gap below was measured against the four landed flows, all of which are clean today. The
risk is entirely forward: the next flow anyone writes.

1. **No deleted-key check at all.** `meta.category`, `globals.{approval_mode, subagent_mode,
   verbosity, concept_depth}`, every `${...}` interpolation, `data.parameters` and `data.writes`
   all pass untouched. Ticket 10 deleted all of them as decoration with zero readers — except
   `data.parameters`, which has **one live read host-wide** (`parameters.flow`), so a stray
   block is not inert.
2. **Node kinds unenforced.** `check.py` still has working `sub-flow` and `router` branches;
   ticket 10 ruled `-mp` ships neither.
3. **Three group nodes per flow unenforced.** Only `parentNode` → group resolution is checked.
4. **Group phase vs node phase unenforced — the important one.** Ticket 28's rule is that the
   two are *written from one table so they cannot disagree*, and that is exactly the property
   nothing checks: both validate against the enum independently, a node whose `data.phase`
   contradicts its group's passes, and the group silently wins at render time.
5. **`requires:` `contract:` refs are checked for existence, not exactness.** Skill refs are
   exact in both directions already. A contract the flow's skills never cite, or a cited
   contract left out, passes.
6. **Edges: `type: flow` only, caught only indirectly.** A wrongly-typed edge surfaces as an
   unreachable node; a non-flow edge *parallel* to a flow edge passes silently.
7. **`version`, `description`, `meta.icon`, `meta.onboarding.*`, `globals.research_depth`, and
   `input_style` values are never checked** — and all of them have live readers in
   `profiles.get.ts`.

### Also in scope

- **`check.py`'s citation check does not scan `flows/`.** Ticket 28 found a dangling link to
  `contracts/flow.schema.json`, deleted by ticket 16, sitting in `flows/README.md` with nothing
  to catch it.
- **`check.py` is stricter than the reader it protects** (found by ticket 23): it rejects any
  prerequisite path outside `_concept/`, so no skill can declare a `package.json` gate even
  though `validator.ts:81` resolves one correctly. Every source-exists gate currently lives at
  its step to work around this. Decide whether the restriction earns its keep; if it does, say
  so at the check so the next author is not left guessing.
- Extend `scripts/test_check.py` with a failing fixture per rule added. A gate with no test for
  its negative case is the same silent pass this ticket is closing.

## Not in scope

Changing any of the four landed flows — they are clean against every rule above. If a new check
fires on one, that is a defect in the check.

## Answer

_(pending)_
