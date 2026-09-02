# 13: A triage on-ramp and a durable record of rejected scope

**Type:** grilling
**Blocked by:** None (04 resolved)
**Status:** ready

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

_(pending)_
