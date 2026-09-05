# 32: `check.py` passes flows that break every rule ticket 10 fixed

**Type:** task
**Blocked by:** None — 28 resolved 2026-09-05 and supplied the list

**Status:** resolved

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

**All seven gaps closed plus the three `### Also in scope` items, `check.py` 471 → 728 lines,
`test_check.py` 372 → 639 with 31 → 59 cases. `check.py` green on the first run (29 skills ·
4 flows · 0 errors) — every new rule passed all four landed flows without a single edit to
`flows/`, which is the ticket's own prediction holding.** Each rule was then smoke-tested by
mutating a real flow (`appbuilder-mvp`) one way at a time, not only against the tmpdir
fixtures, so no rule is a no-op against the shape the collection actually ships.

### The seven gaps

1. **Deleted keys.** `meta.category` and `globals.{approval_mode,subagent_mode,verbosity,
   concept_depth}` are rejected by name in `_check_presentation`; `data.parameters` and
   `data.writes` by name in `_check_nodes`. `${...}` is caught by scanning the flow file's
   **raw text**, not the parsed tree — an interpolation can sit in any string anywhere, and a
   structural walk would have to know every field to find it. Each message names why the key
   is dead, and the two with live readers say so: `data.parameters` cites
   `flow-extended.ts:47` (`parameters.flow`), `data.writes` cites `flow-manager.ts:361,508`.
2. **Node kinds.** `NODE_KINDS = {"skill", "group"}`; the `sub-flow` and `router` branches are
   deleted rather than narrowed, along with the router adjacency in `_check_reachability`.
   `type` is now required (it was optional, inferred from `data.skill`). A `flow:` ref in
   `requires:` is rejected on the matching argument — with no `sub-flow` node it can only
   install a flow nothing delegates to.
3. **Three group nodes per flow.** Exactly three, phases exactly `{conceptualization,
   implementation, review}`, one each — so a duplicate phase fails as well as a missing lane.
   This is what keeps the two concept flows' empty `implementation` group honest.
4. **Group phase vs node phase — the relational one.** Every skill node's `data.phase` must
   equal its parent group's. Only enum-valid values are compared, so a `phase: banana` is
   reported once as a bad enum rather than twice. **It needed one rule the ticket did not
   list to be airtight: a skill node must declare `parentNode`.** Without a parent there is no
   group phase to agree with, so an unparented node is un-checkable by construction and gap 4
   would have had a hole exactly the size of "author forgot the container". All four flows
   parent every skill node already. The inverse is checked too — a non-skill node may not
   declare `parentNode`.
5. **`requires:` `contract:` exactness.** `check_skills` now returns
   `(names, contracts_cited_per_skill_directory)`, and a flow's declared contract set must
   equal the union of what its own node skills cite — the same "no inheritance, no extras"
   rule the `skill:` refs already obeyed, and the same union ticket 28 computed by hand. Both
   directions are reported. A contract whose file does not exist is reported once (existence)
   and excluded from the extras comparison, so one defect is one error. The comparison is
   skipped when any node skill is unresolvable, since the union would be a guess.
6. **Edges.** `type` must be exactly `flow`, checked per edge. Reachability stays and is still
   worth its keep — a disconnected subgraph is possible with every edge correctly typed — but
   the direct check is what catches the parallel non-flow edge, where reachability stays green.
7. **Presentation keys.** `version` and `description` must be non-empty strings (a bare
   `version: 1.0` parses as a float and is rejected, which is the point). `meta.icon` must be
   an `i-` prefixed Iconify name. `meta.onboarding.input_style` must be in
   `{freeform, structured, repo}`; `fields` must be a non-empty list of strings when the style
   is `structured` or `repo`. `globals.research_depth` must be in
   `{skip, light, moderate, deep}` (`profiles.get.ts:47`). Every message names the reader,
   because none of these raise on the far side — `profiles.get.ts` *casts* `input_style` to
   its union and publishes `description` verbatim.

**One extra rule, from ticket 28's finding rather than this ticket's list: a skill node may
not carry `position`.** `flow-layout.ts:53-65` removes positioned nodes from the lane
computation and returns early with `lanes: []` once none remain, so authoring geometry on
skill nodes disables the swimlanes *and* the group-phase override at `:87-93` — i.e. it
silently deletes the mechanism gap 4 exists to protect. It is the same class as everything
else here and the flow still renders, so it belongs at this gate. Group geometry is
deliberately **not** required: the register already records that it has no live reader on
either path.

**One extra catch, free from an existing rule:** `meta.onboarding.placeholder` alongside a
non-`freeform` `input_style` is rejected — `OnboardingWizard.vue:82-99` binds it to the
freeform textarea only, so it is decoration in exactly the sense ticket 10 deleted.

### Also in scope

- **The citation check now scans `flows/`** — every `.md`, `.yaml` and `.yml` under the tree,
  through a shared `_check_citations` helper that skills and contracts also use. The
  `flows/README.md` dangling `contracts/flow.schema.json` link ticket 28 deleted by hand would
  now be caught; a fixture reintroduces it.
- **`test_check.py` has a failing fixture per rule** — 59 cases, up from 31. `good_flow()` was
  rebuilt into the shape the landed flows have (three groups, every skill node parented and
  repeating its group's phase, full presentation block) and nodes are addressed by id through
  a `node(flow, nid)` helper rather than by index, so the fixture can grow. The three
  edge-type tests moved from `only()` to a new `among()` that asserts a defect reports its
  full error set and nothing more.

### The `_concept/` restriction: it stays, narrowed from a ban to a named list

`check.py` now accepts a prerequisite path if it starts with `_concept/` **and** its first
segment is a real entry of the artifact tree, **or** if it is named in
`PROJECT_ROOT_PREREQUISITES` (today: `package.json`). The reasoning is at the constant, in
full, so the next author is not left guessing.

**Why not keep the ban.** It is stricter than the reader it protects: `validator.ts:81` joins
to the *project* root, so `package.json` resolves correctly, and a check whose stated bar is
"the failure mode is quiet" was blocking a declaration with no failure mode behind it at all.
Ticket 23 paid for that directly — `quality-test`'s source-exists gate lives at its step
because the frontmatter could not hold it.

**Why not drop it.** The obvious relaxation — allow anything outside `_concept/` — reopens the
defect class this repo has actually been bleeding: a *concept* path written against a
superseded tree. `experience/screens/foo.md` is a pre-0007 path, not a project-root file, and
under a blanket relaxation it would pass as one. Ticket 30 swept 32 files of exactly that
shape. The carve-out "first segment must not be a tree entry" would catch today's names and
miss tomorrow's.

**Why the list.** It converts a blanket ban into a reviewed exception list: the unknown stays
banned, the known becomes declarable, and extending it is a deliberate edit with the reason
beside it. It also states the limit honestly — a project-root path cannot be verified from
inside this collection, because whether it exists is a fact about the scaffolded project.

**Nothing in the landed collection changes.** No skill declares a non-`_concept/` path today,
so the relaxation is green by construction; it removes a trap rather than unblocking a
pending edit. `docs/adr/0011` carries a dated amendment recording the narrowing (its Decision
text said "every declared prerequisite path starts with `_concept/`" and "check.py enforces
both halves"), and `docs/skill-template.md`'s corresponding bullet is updated to match.
Leaving either stale would have been the documented-vs-enforced drift this ticket exists to
close, one level up.

### What ticket 29 can now rely on the gate to catch

Everything ticket 28 verified by hand, plus the shape rules nobody had checked at all. In
acceptance terms: a flow reaching the host with a `data.parameters` block, a `sub-flow` or
`router` node, a `contract:` manifest that does not match what its skills read, an edge that
draws but orders nothing, an `input_style` the wizard cannot render, or a node whose declared
phase is silently overridden by its group — none of these can now pass CI. That matters
precisely because the host is a weak signal by construction: `validateFlow` has zero call
sites, `run.post.ts:78-80` falls back to a generic prompt, and `requirements.get.ts:37-48`
fabricates `satisfied: true`. A green acceptance run against a broken flow was possible
before this ticket and is not after it.

The gate cannot see two things, and 29 should not read it as covering them: whether a
project-root prerequisite exists (a fact about the scaffolded project, stated at the
constant), and whether a `skill:` ref installs over the network — the acceptance suite
installs over SSH and self-skips when the repo is unreachable, which ticket 28 already flagged.

### For the forge-concept register (Out of scope)

One new entry, found while grounding the `data.writes` ban:

- **Banning `data.writes` leaves `resolveNodeFolders` with nothing to resolve.**
  `flow-manager.ts:361` takes `data.writes` when present and otherwise falls through to
  `getArtifactsProducibleBySkill` (`:368`), which reads the artifact contract —
  **`artifacts.yaml`, which ticket 01 found unreachable as deployed** (`artifact-contract.ts:138`
  reads it only under `--link`). With `data.writes` deleted by ticket 10 and the fallback
  unreachable on a copy install, every `-mp` node resolves to zero folders, so the node-folder
  surface is empty for the whole collection. Neither half is wrong on its own; the two
  decisions compose into a dead feature. It is inert for ticket 29 (nothing gates on it), and
  the fix is the host's — either restore a reachable artifact contract or read the folder from
  the skill's own frontmatter.

### Deliberately left undone

- Nothing committed or staged, per the ticket.
- `flows/`, `skills/`, `templates/`, `profiles/`, `contracts/` untouched. No new check fired on
  any of them at any point, so none was ever a candidate for editing.
- `docs/examples/` untouched (ticket 33 is there); `11_build/review.yaml` not renamed (31).
- **Group `position`/`style` is not required**, though ticket 28's rule mentions geometry. The
  register records it has no live reader on either path, and this gate does not enforce
  decoration — that is the same argument that deleted `meta.category`.
- **`meta.onboarding.placeholder` is not required for a `freeform` flow.** `-mp` ships none;
  the rule would have no subject.
