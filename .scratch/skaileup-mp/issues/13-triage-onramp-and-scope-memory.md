# 13: A triage on-ramp and a durable record of rejected scope

**Type:** grilling
**Blocked by:** None (04 resolved)
**Status:** resolved

## Question

Graduated from the map's fog once ticket 04 fixed the domain set. Ticket 02 found skaileup
has **two structural gaps**, both of which mp fills and neither of which is a port:

1. **No on-ramp for work the collection didn't create.** Every flow starts from a project
   brief. A bug report, an incoming request, a "this screen is wrong" — none has an entry
   point. mp's `triage` is the general skill; skaileup has only the narrow special case,
   `mockup-feedback-triage`, which routes stakeholder annotations back to `_concept/` files.

2. **No memory of rejected scope.** mp keeps an `.out-of-scope/` record so a rejected idea
   stays rejected; skaileup re-litigates. The `_concept/` tree records what was decided,
   never what was refused and why.

Both are **scope additions**, not ports — decide whether `-mp` takes them at all.

Decide:

- Does `-mp` gain a general triage on-ramp? If so, does `mockup-feedback-triage` collapse
  into it (one skill, feedback as one input kind) or stay a sibling?
- Does `-mp` gain a durable rejected-scope record? Where does it live — a file in `_concept/`
  (making it a project artifact that forge-concept can render), or repo-local like mp's
  `.out-of-scope/`?
- Which skill writes it, and at which moments. Scope refusal happens in at least three
  places today: `concept-slice-scope-feature`'s IN/OUT/DEFER pass, the brief, and ad-hoc
  in conversation. Is the record a by-product of the scoping skill, or its own thing?
- **Domain placement.** Ticket 04 draws the `quality`/`ops` line at the artifact under
  inspection: `ops` operates on the concept repo itself. Both of these do — so both are
  `ops-*` unless there's an argument otherwise. Names under the 2-segment rule:
  `ops-triage` and (something like) `ops-scope-memory`.
- If either is refused, say so on the map's **Out of scope** section rather than leaving
  it as fog — this ticket exists to close the question either way.

## Answer

**Both halves resolve as "no new skill" — but for opposite reasons, and the second half gains
a writer it did not have.**

### 1. The triage on-ramp is refused — the inbox is upstream

`-mp` gains **no general triage skill**, and no `ops-triage` name is taken. The gap the
ticket names is real; the demand for filling it is not, and the one channel where a
skaileup-specific triage could have beaten mp's is inert:

- `ai-assets-skaileup` has **1 issue (closed)**; `-mp` has **0**. The 500-issue /
  43-`user-feedback` queue is on `platform` and `workspaces` — repos that have `_concept/`
  but are not driven by the skaileup pipeline, and whose triage **already runs on mp's
  globally-installed `/triage`** with mp's own five labels. Re-implementing it under an
  `ops-` prefix duplicates a skill the human already has, pointed at an empty inbox.
- The one skaileup-shaped channel — forge-concept's per-document comment API
  (`server/api/comments/[...document].{get,post}.ts` over `concept-comment-store.ts`, 137
  lines, threads anchored to a `documentId` on a `_concept/` file) — **is read by nothing in
  the collection**. That is a host-capability finding, not a missing skill, and it goes to the
  **forge-concept register** so the successor effort starts from it.

**The intake rule `-mp` holds instead**, stated positively rather than left implied: *for work
the collection did not create, use the global `/triage`; an accepted item enters at
`spec-feature` (a new or changed feature) or `build-plan` (a defect against built code).* This
is `ask-matt/SKILL.md:40`'s separation rule aimed at `-mp`'s two lanes. It has **no home
today** — `-mp` has no router skill, and inventing one here would port ahead of the shape — so
it is recorded as a **requirement on the router**, in the fog patch that already owns it.

**`mockup-feedback-triage` does not collapse into anything**, because there is nothing to
collapse into. Ticket 06's fold into `mockup-feedback` stands unchanged, and the naming
collision the ticket feared never arises: `-mp` ships one thing called triage, not two.

**Two of the ticket's premises were wrong, and the corrections are the reason the refusal is
narrow rather than sweeping.** "Every flow starts from a project brief" is false: **no** flow
starts at a brief — 7 of 9 addressable flows enter at `skaileup-scope-scope-project`, and
`skaileup-concept-reverse` enters at `ops-reverse-engineer` (`.flow.yaml:43`), a genuine
non-brief entry at whole-repo granularity. And `ops-add-feature` is a real partial on-ramp for
the enhancement half — trigger list, `feature_mode ∈ {new, modification}`, a cascade through
journeys/architecture/datamodel/screens — that is unreachable (**zero flows**) and gated the
wrong way (**hard-gates on `discovery/brief.md`**, `SKILL.md:53-55`). Ticket 21 already
re-points it at `spec-feature`; nothing here re-opens that.

### 2. The rejected-scope half: ticket 05 settled the noun, this ticket supplies the writer

Ticket 05's ruling stands — a rejected scope decision **is** a decision record marked
rejected, not a second store, and no `.out-of-scope/` is created. But calling that half
"closed" overstated it in a way worth separating into two mechanisms:

- **The reader.** mp's `.out-of-scope/` earns its keep at *read* time: triage step 1 matches a
  new request against it **by concept similarity** (`OUT-OF-SCOPE.md:74-76`) and surfaces the
  hit. `-mp` has **no such reader, deliberately** — with the on-ramp refused there is no step
  at which a request is checked against past refusals. **`-mp` ships no re-litigation guard.**
  The refusal record is documentation a human consults, not a check that fires. Stating that is
  this ticket's job; hiding it behind ticket 05's ruling was the error.
- **The writer, which did not exist.** No `-mp` skill wrote a decision record at all, and in
  the old collection 12 skills write the two logs and **none writes a refusal**. So ticket 05's
  ruling described an artifact nothing produced. Fixed here, at one step's cost:
  **`spec-feature` step 4 now appends an OUT that clears the three-test gate to
  `10_blueprint/decisions.md` with Status `rejected`** (`skills/spec-feature/SKILL.md:61-64`).
  The argument is scope, not tidiness: `## Out of Scope` is one feature's and **freezes with
  its dossier**, while the re-litigation the ticket complains about is **cross-feature**.

Two contract defects blocked that writer and are fixed here, because a path sweep cannot
invent a status or choose which log a refusal binds to:

- **`rejected` added to the Status enum** (`contracts/domain_model.md:87-91`), with the
  collision spelled out: it means *the choice was refused*, and is **not** the "rejected
  alternatives" of *Options considered* — the roads not taken inside a decision that was
  accepted. One word was carrying two concepts in one file.
- **The decision-log paths corrected to ADR 0007's tree** — `10_blueprint/decisions.md`
  (design-time) and `11_build/decisions.md` (build-time), at both `:9` and `:75-76`, which
  also disagreed with each other (`_concept/decisions.md` vs `_concept/blueprint/decisions.md`).

**Accepted residue, recorded rather than fixed:** the three-test gate is deliberately narrow,
so **most** scope refusals fail it and stay in `## Out of Scope` inside one frozen dossier,
findable only by someone already reading that feature. That is the known limit of the
documentation-only answer, not an oversight.

**Flagged, not fixed:** `CONTEXT.md:100-101` says decision records exist at **three** levels
(collection · design · build); `domain_model.md` gives paths for **two**. The collection level
is `-mp`'s own ADRs under `docs/adr/`, and reconciling the glossary against the contract
belongs to `CONTEXT.md`'s owner, not here.

### 3. Handed to ticket 16

- **`mockup-feedback`'s journey branch has no target of that shape.** `scripts/triage.py:29-31`
  resolves `screen > feature > journey` to `<subdir>/<value>.md`. Two are stale paths that a
  path check catches (`07_screens/`, `05_features/`) — but `04_journeys/` holds **one
  `stories.yaml`** (`concept_structure.md:53`), so the third branch has **no target at all**.
  It must arrive as *this branch is dead*, or 16 repairs the string and leaves it dead.
- **`domain_model.md` is left half-swept, by design.** Its glossary paths
  (`_concept/blueprint/glossary.md`, `:8,24,63,67`) are still pre-0007, and `:133` names a
  **`skaileup-domain-model` skill that does not exist** and carries an old-scheme name. Both
  are mechanical; neither blocked the writer.

## Note from ticket 05

**Half this ticket is already answered.** A rejected scope decision **is** a decision
record marked rejected — append-only, records a refusal and why, exists so nobody
re-litigates. That is the ADR machine exactly, so `-mp` does **not** gain a second
`.out-of-scope/` store beside it. `scope-feature.md`'s IN/OUT/DEFER stays the working
record for one feature; anything clearing the 3-test gate graduates to the decision
record at the level it binds.

What is left for this ticket is the **triage on-ramp** question alone: does `-mp` gain a
general entry point for work the collection did not create, and does
`mockup-feedback-triage` collapse into it?
