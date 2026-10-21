---
path: [_concept/11_build/slices/<slice_id>/index.md, _concept/11_build/slices/<slice_id>/progress.yaml]
summary: the frozen slice record and its transient progress file
owner: [build-implement]
may_propose: []
---

# _concept/11_build/slices/<slice_id>/index.md

`index.md` is the record of how one slice got built: written once every commit has landed, it
is what `build-branch` checks before closing a branch and what `quality-review`, `ops-review`
and the next reader take instead of the build session. `progress.yaml` is the transient
working list of the plan's rows with the finished ones marked; it exists from the first
finished row until the freeze removes it, and a build that stops midway resumes from it.

## Format

`index.md` frontmatter: `status: frozen`, `slice` (the `slice_id`), `feature` (the feature spec path), `commits` (the landed shas), `last_updated`.

Body:

- **Recap**: one to three sentences of what a user can now do, in their words and not the code's; the files touched; and where the outcome differed from the plan, with the reason.
- **Accepted debt**: what the simplification pass deliberately left in place. `quality-review` reads it as context and does not re-flag it.
- Links forward to the canonical artifacts: the commit shas and the feature spec. The spec carries no pointer back to its commits; `tree/11_build/trace.md` is the one join.

## Writing it

Written by `build-implement`, which calls `tdd` and `code-review` (named in its route) for the build and the review.

1. **Load the slice.** Read `plan.md` (the slice's machine-read plan: its `feature`, `blocked_by`, rows and criterion ids), the feature spec it names and the screens its `screens:` list names (`_concept/07_screens/<screen>.md`). A spec or screen file the plan names that is missing is a fact to resolve (`tree/README.md § How a skill runs`, rule 1): ask the user what the criteria or screen say, in the batch with the seams of step 2, and build from the plan's rows meanwhile. Where the project type grows no screens the spec alone is the source of truth and the plan's UI rows name the endpoint, command or public function to build. While any `blocked_by` slice has no `index.md`, name it and offer to build that one first: the thing this slice builds on does not exist yet. Resume from `progress.yaml` when one is there.
2. **Build the rows, one at a time.** Where `_concept/02_grounding/standards/index.yml` exists, match its entries on `applies_to: build-implement` and the slice's keywords and load the hits before the first test, so the code follows the conventions the codebase already has. Run `tdd` for each row, and confirm the seams with the user before the first test, as `tdd` requires; the plan's test tags say which level, not where. A row is done when its UI renders real data, its handler is callable from that UI, its data layer round-trips and its tests are green; then the next row starts. Mark each finished row in `progress.yaml`. Where `_concept/10_blueprint/openapi.yaml` or `asyncapi.yaml` exists (`tree/10_blueprint/openapi.md`, `tree/10_blueprint/asyncapi.md`), an endpoint or message a row implements matches the operation it documents (path, method, parameters, payload and status codes) and the row's tests assert that shape. A mismatch the contract has wrong is not fixed in the file: name the change for `architecture-system`, which owns the contract, and carry on with the rows it does not touch, because one writer keeps the contract and the code from drifting apart quietly.
3. **Review the code** with `code-review`. Whether the finished feature conforms to its spec is `quality-review`'s verdict and only its; what guards the slice meanwhile is the ledger in step 7, where a criterion with no check behind it stays untested.
4. **Run the gate in `plan.md`.** Its manual checks are questions for the user, one at a time; its automated tests are commands. Add what using it felt like (awkward flow, hidden state, a screen doing too much) and close on **Done**, **Needs more work** or **Blocked**, the last two naming what has to change and who owns it. Only Done continues. Note which criterion ids each check exercised and whether it passed; step 7 writes them to the ledger once there is a commit to stamp.
5. **Recap** in the dossier, per `## Format`: what the next reader gets instead of this session.
6. **Propose one simplification pass.** One to three of the smallest behaviour-preserving improvements (a deletion, a simplification, a clarification), each with what verifies the behaviour survived; the user picks. Additions are proposals for the next slice, and what the user leaves in place goes into **Accepted debt**.
7. **Commit atomically, then record the slice.** Propose the decomposition (migration, logic, UI, tests) and stage an explicit file list per commit after the user approves it, never `.` or `-A`. Each commit body names the slice and its feature spec, which is how a commit is traced back to the artifact that asked for it. Once the last commit has landed, write the slice's entry into `_concept/11_build/trace.yaml` (format and schema: `tree/11_build/trace.md`, validated against `tree/11_build/trace.schema.json` before writing) and then flip the ledger rows step 4 exercised per `tree/11_build/acceptance-criteria/README.md § Flipping rows`, stamping the last commit's short sha.
8. **Freeze the dossier.** Once every commit has landed, write `index.md` per `## Format` and remove `progress.yaml`. Everything else under `_concept/` was read and not rewritten: the ledger rows, the trace entry and this dossier are the only things the build writes there, and a spec edited to match the code stops being what the code is checked against.

## Checks

- The slice's commits are on the branch.
- `index.md` exists beside `plan.md` with `status: frozen`, and `progress.yaml` is gone.
- `trace.yaml` carries the slice's entry.
