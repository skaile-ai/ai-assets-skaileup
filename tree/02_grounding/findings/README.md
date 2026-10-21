---
path: [_concept/02_grounding/findings/]
summary: graded evidence and raw material from outside the room
owner: [concept-reverse, concept-research, design-brand]
may_propose: []
---

# _concept/02_grounding/findings/

Graded evidence and raw material from outside the room. `concept-reverse` writes the seven
evidence files from an existing repository, one scope at a time; `concept-research` and `design-brand` file
screenshots and page saves here, and nowhere else. The skills that own the artifacts seed their
drafts from the evidence and show each graded value to the user as a proposal: `concept-brief`
from `brief-seeds.md`, `design-brand` from `brand.md`, `architecture-techstack` from `stack.md`;
`experience-journeys`, `experience-shell`, the `spec-feature` loop,
`architecture-datamodel`, `architecture-system` and `quality-standards` read the rest as
evidence; `experience-interaction` seeds `APP-DESIGN.md` from `interaction.md`, and `quality-interaction` reads it as the census to judge against. Findings are never artifacts and never decisions.

## Contents

- `tree/02_grounding/findings/index.md` — the catalogue.
- `tree/02_grounding/findings/brief-seeds.md`, `tree/02_grounding/findings/stack.md`, `tree/02_grounding/findings/brand.md` — what the docs, manifests and theme files say.
- `tree/02_grounding/findings/routes.md`, `tree/02_grounding/findings/screens.md`, `tree/02_grounding/findings/datamodel.md` — what the code says.
- `tree/02_grounding/findings/interaction.md` — how the code lets a user work: surfaces, editors, save models, messages, search.
- Screenshots and page saves sit beside these files, each with a row in the catalogue.

## Format

Every value in a findings file carries a grade, in an `extraction_confidence` field beside the
value:

| grade | means |
|---|---|
| `extracted` | read verbatim from code, config or docs |
| `inferred` | reasoned from structure, defensibly, but nobody said it |
| `needs_review` | no signal found |

The grade is the whole difference between a finding somebody can trust and one that reads like a
hand-written concept while being half guesswork, and the report in `## Writing it` is counted
from it. Each value is cited to the file that backs it, and every cited path exists on disk (a
package subpath export such as `./store/react` is not a path). The user's acceptance is recorded
as `approved: <date>` in the frontmatter of every findings file the run wrote
(`tree/README.md § Frontmatter every markdown artifact carries`); a run the user has not accepted
leaves the key out, and a re-derive that changes an entry clears it.

Every evidence file carries these frontmatter fields, so a reader can tell whether the code has
moved since the finding was written:

```yaml
scope: screens                  # the scope this file answers (table below)
paths: ["app/pages/**"]         # source globs read for it; ["**"] when the whole app was read
source_sha: 3f9c2ab             # `git rev-parse HEAD` of the code the entries were read from
last_updated: 2026-10-21
```

An entry kept from an earlier read, outside the globs of the run that wrote the file, carries
`as_of: <source_sha it was read at>` beside its grade; an entry without `as_of` is current at
`source_sha`. A repository without git leaves `source_sha` as `none`, and the file counts as
stale on every run.

## Scopes and freshness

| scope | findings file | reads |
|---|---|---|
| `brief` | `brief-seeds.md` | README, manifest description, changelog, `docs/` |
| `stack` | `stack.md` | manifests, lock files, framework config, CI, Dockerfile |
| `brand` | `brand.md` | theme config, token files, root layout |
| `routes` | `routes.md` | routers, API handlers, navigation components |
| `screens` | `screens.md` | page components behind the routes |
| `datamodel` | `datamodel.md` | schema, migrations, fixtures |
| `interaction` | `interaction.md` | overlays, editors, finders, save and message code |

**Calling it.** Any skill whose derive step finds the code holding a fact the findings lack runs
`concept-reverse` with `scope` (one or more values of the table) and optionally `paths` (globs
relative to the app root), for example: run `concept-reverse` with scope=screens
paths=app/pages/inbox*. It writes the files of the requested scopes and no others; a skill that
calls it reads only those files afterwards.

**Fresh or stale.** A findings file is fresh when its `source_sha` equals `git rev-parse HEAD`
and its `paths` cover the request; a fresh file is read as it is and rewritten by nobody. A
different `source_sha`, or a request reaching past `paths`, makes it stale. A stale file is
re-derived for the requested `paths` only (every path when none were given): the entries citing
a file inside the globs are replaced, the others stay, and `source_sha` and `last_updated` move to
the new run. `paths` becomes the requested globs, joined by the old `paths` only when the old
`source_sha` was already HEAD (a request reaching past `paths`), since only then are those
entries still current. The entries the run did not re-read keep their grade and gain `as_of`; a
neighbour's re-read does not make them current.

## Writing it

### Extracting (concept-reverse)

1. **Resolve the request and the app.** Read `scope` and `paths` from the request; none given
   means every scope and the whole app. The repository path must be readable and hold a source
   tree, a README or a package manifest. A monorepo has more than one candidate: name them and
   ask which is the app, since every later step scopes to that answer; a request that already
   names a path inside one app has answered it. For each requested scope read the file of
   `## Scopes and freshness` if it exists, compare its `source_sha` with HEAD and keep the fresh
   ones as they are; show a diff before touching a file the user has already accepted.
2. **Map before reading deeply.** List the top two levels and identify manifests, the README and
   `docs/`, the source root, framework config files, schema or migration directories, tests and
   CI configuration. Read selectively from that map; `dist/`, `build/`, `.next/`,
   `node_modules/` and lockfiles are generated and buy nothing but context.
3. **Write the files of the requested scopes**, grading each value as it is written, each
   following its own node (the table above names it), with the four frontmatter fields set and
   the stale entries merged as `## Scopes and freshness` says. Add or update a row per file in the
   catalogue with `step: concept-reverse`.
4. **Verify the citations, then report.** Check every file path written into a finding exists; in `interaction.md` the check is the one in `tree/02_grounding/findings/interaction.md § Verifying citations`: the full path from the repository root, with a line that exists.
   Present the counts per file of `extracted`, `inferred` and `needs_review`, list every
   `needs_review` value with what is missing, and note the ambiguities: two ORMs, no README,
   routes recovered from components because there is no router. A report claiming nothing needs
   review while the brief seeds came from a package description is the failure this step exists
   to prevent.
5. **Report what each written file now offers**: the brief from `brief-seeds.md`, the brand from
   `brand.md`, the stack from `stack.md`, the journeys and the feature roster from `routes.md`,
   the screens from `screens.md`, the model from `datamodel.md`, the interaction census in
   `interaction.md`. Name what the user should correct first, which is always the `needs_review`
   list. Once the user has accepted the report — corrections made, the `needs_review` list
   acknowledged — write `approved: <date>` into every findings file this run wrote; a run called
   from another skill's derive step leaves that acceptance to the calling skill's own batch.

### Filing raw material (concept-research, design-brand)

Screenshots, page saves and excerpts go in this folder — the only place screenshots live — each
with a row in `tree/02_grounding/findings/index.md`: file, source, date and `step:` set to the
skill that took it. `design-brand` does this for each reference URL it opens; `concept-research`
for everything its agents collect.

## Checks

- Every evidence file of a requested scope exists, is in the catalogue and carries `scope`, `paths`, `source_sha` and `last_updated`.
- A re-derive left the entries outside the requested `paths` in place, each with its grade and, when older than `source_sha`, its `as_of`.
- Every value carries a grade; every cited path resolves on disk.
- Every screenshot has a catalogue row whose `step` names the skill that took it.
