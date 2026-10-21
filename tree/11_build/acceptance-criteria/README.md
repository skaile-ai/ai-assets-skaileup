---
path: [_concept/11_build/acceptance-criteria/, _concept/11_build/acceptance-criteria/<featureset>/<feature_slug>.ac.md]
summary: the criteria status ledger, one checkbox file per feature
owner: [build-plan, build-implement, quality-e2e, quality-review]
may_propose: []
---

# _concept/11_build/acceptance-criteria/

The **ledger** tracks whether each acceptance criterion has been proved. It is a join and not
a copy: a criterion is written once, in its feature spec, and the ledger holds one row per
criterion carrying its id, its status and what proved it. A row never restates the
criterion's text, because the build half's copy is the one that quietly becomes what the code
is checked against.

## Format

One file per feature, mirroring its place under `05_features/`:
`_concept/11_build/acceptance-criteria/<featureset>/<feature_slug>.ac.md`.

```markdown
---
feature: <feature_slug>
feature_ref: _concept/05_features/<featureset>/<feature_slug>.md
last_updated: YYYY-MM-DD
---

# Criteria — <Feature Name>

- [ ] AC-checkout_flow-01
- [PASS] AC-checkout_flow-02 — tests/checkout/total.test.ts · build-implement · 4f2a9c1 · 2026-09-05
- [FAIL] AC-checkout_flow-03 — journey "checkout" step 4: total unchanged · quality-e2e · 4f2a9c1 · 2026-09-05
- [ ] AC-cart-01
```

- **Rows are checkbox lines and not a table.** The one machine that reads the file matches `- [PASS|FAIL|x|X| ] <text>` line by line, and a table parses as zero criteria, so the coverage page reports the feature as untested.
- `feature:` is what every other build artifact joins on; without it the id falls back to the directory name, which is the featureset.
- The marker is the status: empty is untested, `PASS` and `FAIL` say what they say.
- The text after the id is the **evidence**, `<pointer> · <evaluator> · <commit> · <date>`: the check that set the row (a test path, or a journey and step), the skill that set it, the short commit the evaluated tree was at, and the date. An untested row carries the id alone.
- The id is a criterion id (`AC-<story-id>-<nn>` or `AC-<feature_slug>-<nn>`, grammar in `tree/04_journeys/stories.md`).

| skill | what it does to the ledger |
|---|---|
| `build-plan` | creates the file: one row per criterion id in the spec, every one untested |
| `build-implement` | evaluates the rows its slice gate exercised, each with the check behind it |
| `quality-e2e` | evaluates the rows a journey covered, end to end in the browser |
| `quality-review` | evaluates the rows it re-checks against the running app |
| `quality-release` | reads the rows and does not re-walk journeys |
| `ops-review` | reads the rows: any `FAIL` or untested row makes the feature's coverage row red |

## Writing it

Every skill that writes a row follows these rules, so two evaluations of one criterion cannot
leave the ledger telling two stories:

1. **One row per criterion id, created once.** `build-plan` creates the rows; no other skill adds, removes or renumbers one. An evaluator that finds no ledger for its feature stops and names `build-plan` as the missing step, since a ledger built afterwards holds whatever happened to get tested.
2. **An evaluation overwrites.** The evaluator replaces the row's marker with `PASS` or `FAIL` and its evidence with its own (pointer, evaluator, commit, date); git history holds the earlier verdict.
3. **Only evaluated rows change.** A row the run did not exercise stays exactly as it was; a row set on inference costs the ledger its value, because every reader downstream trusts it instead of re-reading the code.
4. **`FAIL` beats `PASS` at the same commit.** When two evaluations of one commit disagree the row ends `FAIL` with the failing evaluation's evidence, and a later `PASS` at that commit does not overwrite it. At a newer commit rule 2 applies and the newer evaluation wins either way.

### Creating the ledger (build-plan)

Create `_concept/11_build/acceptance-criteria/<featureset>/<feature_slug>.ac.md` with one untested row per criterion id the feature spec carries, story-derived and spec-added alike, and the frontmatter above. This is the one point where rows are created and every later evaluation overwrites a row and never adds one. The slicing step already claimed every criterion into a slice, so this is the only point at which the full set is known before anything is built.

### Flipping rows (build-implement, quality-e2e)

#### build-implement

After the last commit of a slice has landed, set only the rows the slice gate's checks exercised, each carrying its check as the pointer, `build-implement` as evaluator, the last commit's short sha and today's date.

#### quality-e2e

Drives the running application through **every story in `_concept/04_journeys/stories.yaml`**, one journey per story, and reports what a user can and cannot actually do. Where `quality-test` asserts against units, this asserts against the product: a journey's pass condition is its own criterion ids, observed in the browser. The tool is `agent-browser`. Screenshots are test output and live beside the tests in the codebase, and never under `_concept/`, which holds what the project decided and not what one run looked like.

1. **Clear the platform gate.** `agent-browser` supports Linux, WSL and macOS; on anything else stop and say so. Confirm a browser-reachable frontend exists (a dev script, a pages tree, an `index.html`) and that `agent-browser --version` answers; install it if it does not. An API-only run (step 2) skips these browser checks.
2. **Build the journey list.** Read every story in `stories.yaml`, hero and vital stages first, and carry each story's criterion ids forward as that journey's pass conditions; read a criterion's text from `stories.yaml` when a step needs it and copy it into neither the report nor the ledger. Where the project type grows no journeys there is no `stories.yaml`: derive one end-to-end path per feature from the ids in the feature specs and the ledger and treat those criteria as the pass conditions. Screen specs under `_concept/07_screens/` give the routes and the per-state elements to look for; without them, discover routes from the running app's own navigation and record in the report that they were inferred. Read `_concept/10_blueprint/datamodel/` for the entities a journey writes and the queries that confirm them; a project with no data model gets journeys proved through the UI alone. A project with no UI journeys (an `api-service`) is proved through its API instead: where `_concept/10_blueprint/openapi.yaml` exists (`tree/10_blueprint/openapi.md`), each documented operation is one path to walk and the criteria of the features that implement it are its pass conditions; steps 4 and 5 then exercise the operation's responses against the running service instead of driving a browser. A project with UI journeys keeps the browser walk. Then open the ledger of every feature the journeys cover; if one does not exist, stop and name `build-plan`, because the verdicts have nowhere to land and a ledger built after the walk holds only what was walked.
3. **Start the app and pin the seed.** Install, start the dev server in the background, wait until it answers, then open it. Every input a journey types comes from a named scenario in `_concept/10_blueprint/datamodel/seed.json` (`tree/10_blueprint/datamodel/seed.md`); invented test data proves the app handles data that does not exist in it.
4. **Walk each journey, screenshotting every step.** Re-snapshot after every navigation, since element references go stale the moment the page changes and acting on one fails in a way that reads like a product defect. Read the screenshots back instead of assuming the click landed, check the console for errors after each step, and after any step that writes data query the store to confirm the record matches the data model. A journey passes only when **all** of its criterion ids hold; otherwise it fails, named by the id of the first criterion that did not.
5. **Test the key pages responsively** at 375×812, 768×1024 and 1440×900.
6. **Write the verdicts into the ledger.** For every feature a journey covered, set the rows it evaluated, found by criterion id, to `PASS` or `FAIL` per the rules above: the journey and step as the pointer, `quality-e2e` as evaluator, the commit under test and today's date. The ledger is the record of each journey's verdict and `quality-release` reads it from there. An id the journey never reached stays as it was.
7. **Stop the dev server and close the browser session**, whatever the outcome; a server left running is the next run's port conflict.
8. **Report** per journey: pass or fail, the failing criterion id, the screenshots, the console errors, and any record the database did not hold. The pass or fail cites the ledger rows it was written to and is not a second verdict. Group the failures by feature so the reader knows which spec to reopen.

### Reading (quality-review, ops-review)

`quality-review` re-checks the ledger of the feature under review: for every row marked `PASS`, exercise the criterion against the running app and not the code that claims it, because static inspection is how a `PASS` row survives with nothing behind it. Overwrite each row it re-checked with its result and its own evidence, per the rules above (`FAIL` beats an earlier `PASS` at the same commit). A row that fails is a `high` finding carrying its criterion id; rows it did not exercise stay as they were.

`ops-review` and `quality-release` only read. They take each feature's status from its ledger and do not walk journeys again: a `FAIL` or untested row makes the feature's coverage row red in `ops-review` and is what blocks the release in `quality-release`.

## Checks

- Every criterion id in the feature spec has exactly one row, and no row carries criterion text.
- Every `PASS`/`FAIL` row carries `<pointer> · <evaluator> · <commit> · <date>`; every untested row carries the id alone.
- After a `quality-e2e` run: every story (or derived path) has a pass or a fail with a criterion id behind it, the rows evaluated carry that verdict and its evidence, and no dev server or browser session is left alive.
