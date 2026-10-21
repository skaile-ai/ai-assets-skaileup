---
name: quality-test
description: "Use when built features need a test suite that traces back to their specs — learns the project's test conventions from its existing tests, then writes unit tests and, where there is a data layer, integration tests. Triggers on 'generate tests', 'add test coverage', 'write integration tests'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: scope }
      - { id: features }
      - { id: grounding-findings }
    produces: []
  prerequisites:
    files:
      - { path: "_concept/01_meta/scope.yaml", gate: soft }
      - { path: "_concept/05_features", gate: soft, min_entries: 1 }
      - { path: "_concept/02_grounding/findings", gate: soft }
---

# quality-test

Covers features that are already built: one test file per feature, every case traceable to
the criterion it proves. `tdd` owns the tests written *before* the code; this is the pass
that covers what shipped without them, and it never rewrites a test to make it green.

Read `tree/README.md` once per session. **The levels come from the depth** in
`_concept/01_meta/scope.yaml` (`tree/01_meta/scope.md`): `sketch` runs unit only, `standard` and
`exhaustive` run unit and integration. A `depth` the file lacks is asked in the batch of step 3
and recorded as `tree/01_meta/scope.md § Asking a missing key` says; the project's size is
not a question to ask twice.

## Steps

1. **Confirm there is code to test.** A manifest at the project root (`package.json`,
   `pyproject.toml`, `go.mod` or the stack's equivalent) plus source for the features you are
   about to cover. With no source there is nothing to assert against: stop and name
   `build-implement`.
2. **Read two or three existing tests before writing one.** They carry the runner, the file
   placement (colocated or a test root), the naming pattern, the assertion style and how the
   project mocks. Match them exactly: a suite in a second dialect is one the next author has
   to choose between. When no runner is configured, ask which one to use and let the user
   install it rather than picking one for them.
3. **Map each feature to its testable units.** For every feature under `_concept/05_features/`
   (`tree/05_features/[featureset]/[feature].md`), read its acceptance criteria and find the
   exported functions, handlers, stores and validators that carry them, then name which
   criterion each unit answers. A criterion that needs a browser or a database is not a gap
   here: record it as belonging to integration or to `quality-e2e` and move on. With no
   feature specs, derive the units from `_concept/02_grounding/findings/routes.md` and the
   code, and ask the user which behaviours must hold, in one batch with the open `depth`
   (`tree/README.md § How a skill runs`, rule 1); the tests then name those behaviours in
   place of criterion ids, and the report says so.
4. **Write the unit tests**, one file per feature, describe blocks named for the criterion
   they cover and each test naming its criterion id (`AC-<story-id>-<nn>`).

   | Source | What to test |
   |---|---|
   | Composables and hooks | return values, reactivity, error handling |
   | Utility functions | input/output, edge values, type handling |
   | Handlers | request parsing, response shape, error responses |
   | Stores and state | mutations, getters, actions, initial state |
   | Validators | valid input, invalid input, boundary values |

   Leave to the layers above: database queries, full request/response cycles, cross-feature
   interaction (integration), and anything visual or browser-dependent (`quality-e2e`). Mock
   every external dependency the way the existing tests do; a unit test that reaches a real
   service fails for reasons that have nothing to do with the feature.
5. **Write the integration tests** when the depth includes the level. They need a data layer:
   with no `_concept/10_blueprint/datamodel/` and no `.env.example` there is nothing to
   integrate against, so say that in the report and finish at unit rather than mocking a
   database and calling the result an integration test.

   Start from an endpoint inventory (endpoint, method, entity, feature, auth required) built
   from the route files and the data model, so coverage is measured against what the app
   exposes and not what the tests happen to hit. Then pick **one** isolation strategy and use
   it everywhere: a separate test database (state survives inspection when a test fails), a
   transaction rolled back per test (fastest, and broken by any code that opens a transaction
   of its own), or truncate-and-reseed between tests (works anywhere, slowest). Feed every
   case from a named scenario in `_concept/10_blueprint/datamodel/seed.json`
   (`tree/10_blueprint/datamodel/seed.md`); invented fixtures drift from the shape the app
   actually stores. Cover per endpoint: the happy path with a database assertion behind it,
   the field constraints the model declares, the auth rejection, and the cross-feature flows
   the entity relations imply.
6. **Run the suite.** Fix what fails because the test is wrong: a missing mock, a stale
   import, a wrong path. Report what fails because the code is wrong, with the file and the
   expectation, and leave the assertion standing, since a test edited until it passes is a bug
   with a green tick beside it.
7. **Report** per feature: the file written, how many tests, which criteria they cover, and
   which criteria no test can reach and why. The uncovered list is the point of the report; it
   is what `quality-e2e` and the next planning pass read.

**Done when** every feature under `05_features/` has a test file at the levels its depth
runs, every test names the criterion it covers, and the suite runs with every remaining
failure attributed to the code rather than to the test.
