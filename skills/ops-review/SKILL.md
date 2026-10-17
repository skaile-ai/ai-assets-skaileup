---
name: ops-review
description: "Use when _concept/ needs a health check, its cross-references have drifted, or you want to know whether every feature is actually built and shipped. Produces the review verdict and a build-coverage matrix read from the trace, each finding naming the skill that fixes it. Triggers on 'audit the concept', 'check for issues', 'fix the links', 'is every feature done', 'what code belongs to no feature'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: features }
      - { id: screens }
      - { id: datamodel }
      - { id: trace }
      - { id: app-design }
    produces: []
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: hard }
      - { path: "_concept/05_features", gate: soft, min_entries: 1 }
      - { path: "_concept/11_build/slices", gate: soft }
      - { path: "_concept/11_build/trace.yaml", gate: soft }
      - { path: "_concept/10_blueprint/datamodel", gate: soft }
      - { path: "APP-DESIGN.md", gate: soft }
---

# ops-review

Inspects `_concept/` and reports what is wrong with it, in two halves. **Review** is the tree's integrity: structure,
frontmatter, cross-references, naming, coverage and decay. **Coverage** is build coverage: per feature, the slices,
commits and code behind it from `11_build/trace.yaml`, plus the tracked files that belong to no feature. Both are
recomputed every run, delivered as the report and never written to disk; the only writes are the cross-reference
repairs the user approved.

Read `tree/README.md` once per session. Stance, flag shape and severities are `tree/11_build/README.md § Verdicts`; the
legal paths and what each skill may read are `tree/README.md § Read direction`; every `_concept/` file's frontmatter
and naming is the node at its own path. This file sequences the checks and does not restate them.

## Steps

1. **Run the mechanical check.** `python3 <skill-dir>/scripts/check_concept.py <project>` prints one `path: message`
   line per problem. Report each line unedited, the message as the finding's `note`; rereading the files to
   second-guess it spends the run on what the script already settled. `not valid JSON` or `not valid YAML` on
   `model.json` or `stories.yaml` is `critical`: the script then skips the data-entity and criterion checks, and the
   model or journeys cannot be read. Every other line is `high`: `unowned` entries (retired paths included), missing or
   non-ISO frontmatter fields, broken `screens:` and `implements:` links, `data_entities[]` absent from the model, bad
   criterion ids, and malformed ledger rows. A project with no `_concept/` is the missing step, not a finding.
2. **Inventory what the script does not read**, once and before scoring anything: every featureset, feature and
   screen, the data model, the `11_build/slices/` dossiers and `git ls-files`. Then **check the naming rules** per
   `tree/10_blueprint/datamodel/README.md § Naming` (entity, field, enum, relation) and the body a feature spec must
   have per `tree/05_features/[featureset]/[feature].md § Format`; a generated concept fails these first.
3. **Check coverage.** Per feature: a spec, at least one screen that implements it, and an entity it reads or writes
   or an explicit statement that it needs none. Globally: `03_brand/brand.tokens.json` and `10_blueprint/techstack.md`
   exist, since the renderers and the planner hard-gate on them. A gap here is work not yet done, reported as the
   missing step.
4. **Check the screen specs against `APP-DESIGN.md`**, where the file exists (`tree/APP-DESIGN.md § Reading it`);
   without it say the interaction check did not run. Read `07_screens/` for four rules of
   `tree/APP-DESIGN.md § Patterns`: **P1**, an attribute editable on two screens; **P4**, two editors of one object type; **P8**, two index
   screens of one type; **P13**, a label that is not a term in `glossary.md`. Each is a `warning` citing the rule, the
   entry it breaks and both screen files. The fixer is `spec-feature` when the screen strays from a decision the file
   makes, and `experience-interaction` when the file has no decision for it or two entries conflict. The code is
   `quality-interaction`'s; this step reads specs only.
5. **Check for decay.** A screen no feature implements and a model no feature's `data_entities[]` lists are orphans; a
   file whose `last_updated` sits far behind its siblings is stale. Report both; deleting is the user's call, since an
   orphan is as often planned work as a leftover.
6. **Build the coverage matrix, one row per feature**, from the trace and the dossiers, never stored. A feature's
   slices are its `11_build/trace.yaml` entries (`tree/11_build/trace.md`), cross-checked against the
   `11_build/slices/` dossiers whose `plan.md` frontmatter names the feature (`tree/11_build/slices/[slice_id]/plan.md`):
   a dossier the trace lacks is a slice that committed without recording itself, reported against `build-implement`. No
   trace at all is the finding when any slice dossier exists, and the missing step on a project that has built nothing.
   Per row: whether every slice is frozen (its `index.md` exists), the commits and code the trace recorded, the ledger
   rows of the feature's criteria and their status (`tree/11_build/acceptance-criteria/README.md § Reading`), and
   whether any doc page cites its source files. **Red** when a slice is unfrozen, commits or code are empty, or a
   ledger row is `FAIL` or untested. **Amber** when the hard checks pass but the documentation does not. **Green**
   otherwise. `overall` is green exactly when no row is red; amber is surfaced, not blocking.
7. **Scan the other direction for orphan code.** Every file `git ls-files` reports under the source directories, minus
   the union of every feature's `code` in the trace, minus tests, build output, configuration, dotfiles and
   `_concept/`. What remains is code no feature claims: advisory, never deleted, a question for the user.
8. **Name the fixing skill on every finding**, the script's included. A missing screen is `spec-feature`; a missing
   shell is `experience-shell`; missing tokens are `design-brand`; a missing stack or model is `architecture-techstack`
   or `architecture-datamodel`; a retired path is the skill that now writes its replacement (`03_brand/tokens.json` →
   `design-brand`, `11_build/interaction.yaml` → `quality-interaction`, `comparable.md` → `concept-brief`); a missing
   glossary is `concept-glossary`; an unplanned feature is `build-plan`; an unfrozen slice or missing trace entry is
   `build-implement` or `build-branch`; a feature with no featureset is `spec-featuresets`. A finding without a next
   command leaves the reader to triage it.
9. **Show everything, then offer the repairs.** Rank findings by the severities of `tree/11_build/README.md § Verdicts`,
   `critical` and `high` being the blocking issues in its report format. Beyond the script's lines (step 1): a red
   coverage row is `high`; a naming violation or an amber row is `medium`; an orphan screen or model,
   a stale file and orphan code are `low`. The verdict is `pass` while no finding blocks, else `needs_iteration`.
   Present the findings and the coverage matrix as a table with its orphan list and `overall`, then offer only the
   mechanical fixes: adding a missing back-link, removing a reference to a file that no longer exists. Show the exact
   diff and get a yes before writing. Everything else is reported and left alone: repairing it means deciding what it
   should have said.

**Done when** every feature has exactly one coverage row, every finding was reported with its severity and fixing
skill, and any applied repair was shown as a diff first. A reader who wants yesterday's verdict runs the skill again.
