---
path: [_concept/02_grounding/findings/]
summary: graded evidence and raw material from outside the room
writers: [concept-reverse, concept-research, design-brand]
---

# _concept/02_grounding/findings/

Graded evidence and raw material from outside the room. `concept-reverse` writes the seven
evidence files from an existing repository; `concept-research` and `design-brand` file
screenshots and page saves here, and nowhere else. The skills that own the artifacts seed their
drafts from the evidence and show each graded value to the user as a proposal: `concept-brief`
from `brief-seeds.md`, `design-brand` from `brand.md`, `architecture-techstack` from `stack.md`;
`experience-journeys`, `spec-featuresets`, `experience-shell`, the `spec-feature` loop,
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
package subpath export such as `./store/react` is not a path). Every findings file carries
`last_updated`; the user's acceptance is recorded as `approved: <date>` in the frontmatter of
every findings file the run wrote (`tree/README.md § Frontmatter every markdown artifact carries`), and a run the user has not accepted leaves the key out.

## Writing it

### Extracting (concept-reverse)

1. **Confirm the repository and find the app inside it.** The path must be readable and hold a
   source tree, a README or a package manifest. A monorepo has more than one candidate: name
   them and ask which is the app, since every later step scopes to that answer. Note which
   findings files already exist — add only what is missing and show a diff before touching any.
2. **Map before reading deeply.** List the top two levels and identify manifests, the README and
   `docs/`, the source root, framework config files, schema or migration directories, tests and
   CI configuration. Read selectively from that map; `dist/`, `build/`, `.next/`,
   `node_modules/` and lockfiles are generated and buy nothing but context.
3. **Write the seven evidence files**, grading each value as it is written, each following its own
   node: `tree/02_grounding/findings/brief-seeds.md`, `tree/02_grounding/findings/stack.md`, `tree/02_grounding/findings/brand.md`, `tree/02_grounding/findings/routes.md`, `tree/02_grounding/findings/screens.md`, `tree/02_grounding/findings/datamodel.md`, `tree/02_grounding/findings/interaction.md`. Add a row per file to the catalogue with `step: concept-reverse`.
4. **Verify the citations, then report.** Check every file path written into a finding exists; in `interaction.md` the check is the one in `tree/02_grounding/findings/interaction.md § Verifying citations`: the full path from the repository root, with a line that exists.
   Present the counts per file of `extracted`, `inferred` and `needs_review`, list every
   `needs_review` value with what is missing, and note the ambiguities: two ORMs, no README,
   routes recovered from components because there is no router. A report claiming nothing needs
   review while the brief seeds came from a package description is the failure this step exists
   to prevent.
5. **Hand off**, naming what each skill now has to work from — the brief from `brief-seeds.md`,
   the brand from `brand.md`, the stack from `stack.md`, the journeys and featuresets from
   `routes.md`, the screens from `screens.md`, the model from `datamodel.md`, the interaction decisions from `interaction.md` — and what the user
   should correct first, which is always the `needs_review` list. Once the user has accepted the
   report — corrections made, the `needs_review` list acknowledged — write `approved: <date>`
   into every findings file this run wrote.

### Filing raw material (concept-research, design-brand)

Screenshots, page saves and excerpts go in this folder — the only place screenshots live — each
with a row in `tree/02_grounding/findings/index.md`: file, source, date and `step:` set to the
skill that took it. `design-brand` does this for each reference URL it opens; `concept-research`
for everything its agents collect.

## Checks

- Every evidence file `concept-reverse` was asked for exists and is in the catalogue.
- Every value carries a grade; every cited path resolves on disk.
- Every screenshot has a catalogue row whose `step` names the skill that took it.
