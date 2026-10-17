---
path: _concept/02_grounding/onboarding/answers.json
summary: the one answer record — values, confidence, seed inventory, approval
writers: [concept-onboard]
---

# _concept/02_grounding/onboarding/answers.json

The one record of what the user answered. `concept-onboard` owns it; every other skill reads it
and no skill reads the host's own files, so an answer missing here is asked again. The host
saves each step's wizard input at `_concept/_grounding/<step>/user_input.json` and shows it as
pre-collected input; `concept-onboard` merges those files into `answers.json` once.

## Format

A data file with no frontmatter, described by `tree/02_grounding/onboarding/onboarding-answers.schema.json` (open: every skill's input dialog may add field ids; `last_updated` required). Keys are the `id` values of the `inputs_optional` fields a
dialog rendered (`framework`, `database`, `ui_library`, `auth`, `has_brand`, …), holding the raw
value; six reserved keys sit beside them: `approved`, `last_updated`, `confidence`, `rationale`,
`renderer`, `seeds`.

```json
{
  "approved": "YYYY-MM-DD",
  "last_updated": "YYYY-MM-DD",
  "framework": "Nuxt 4",
  "database": "PostgreSQL",
  "has_brand": true,
  "brand_files": "assets/brand/",
  "confidence": { "framework": "locked", "database": "preferred" },
  "rationale": { "framework": "the team already ships Nuxt" },
  "renderer": "static-html | astro",
  "seeds": [{ "path": "02_grounding/seeds/pitch.pdf", "seeds": "brief", "grade": "complete | partial | reference" }]
}
```

- `confidence` is `locked` (decided, not open to a recommendation), `preferred` (open to a
  better fit) or `open` (recommend from the project's signals), one per technology answer.
  `architecture-techstack` honours `locked` and may overrule `preferred`; without the word every
  answer reads as binding.
- `renderer` is `static-html` (zero-build page set) or `astro` (built site); `mockup-walkthrough`
  reads it from here at render time and nowhere else.
- `seeds[].grade`: `complete` (a later skill adopts it and skips that ground), `partial` (a
  starting point with named gaps), `reference` (context only — code excerpts, competitor PDFs).
- `approved:` is written only once the user has confirmed the seed table and the answers as read
  back; a record whose answers are unconfirmed carries no such key.

## Writing it

1. Read `answers.json` if it exists. One that carries `approved:` means this ran before: show
   what it holds and ask whether to continue with it, change specific answers, or start over.
2. Fold the values of every `_concept/_grounding/<step>/user_input.json` into `answers.json`
   once. A value already there changes only after the user confirms the change; new answers
   merge into the file rather than replacing it. A saved value is the default, and a question
   already answered is skipped.
3. Read `_concept/01_meta/scope.yaml` (format: `tree/01_meta/scope.md`) for `project_type` and the flow; confirm that value rather than
   collecting it again.
4. Ask the technology preferences — framework or language, data access and database, UI
   component library, authentication, overall architecture pattern — one question per message,
   each answer with its `confidence`. Skip what the user has not decided rather than recording
   a null.
5. Ask whether the project has a brand (logo, palette, typography, style guide) and where its
   files are, because `design-brand` extracts from them instead of proposing. On a flow that
   renders a walkthrough, ask which `renderer` the project wants.
6. Scan `02_grounding/seeds/` and show a table of file → artifact it seeds → grade; let the user
   correct it before recording, because a misclassified seed is ignored or treated as truth.
   Read the files where they sit and leave them there.
7. Validate the record against `tree/02_grounding/onboarding/onboarding-answers.schema.json` (dates as ISO text), then write the remaining answers: technology answers with `confidence` and any `rationale`, the
   brand answer and file location, `renderer`, the `seeds` list. Set `last_updated`, carry
   `approved` forward on every write, and set a new `approved: <date>` once the user confirms.
   Report what was captured and which questions went out.

## Checks

- The file parses as JSON, validates against `tree/02_grounding/onboarding/onboarding-answers.schema.json`, and `approved` is present only after confirmation.
- Every file under `02_grounding/seeds/` appears in `seeds`.
- Every technology answer carries a `confidence` value.
