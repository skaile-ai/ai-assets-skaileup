---
path: _concept/11_build/interaction.sarif
summary: SARIF 2.1.0 verdict of the code against APP-DESIGN.md
owner: [quality-interaction]
may_propose: []
---

# _concept/11_build/interaction.sarif

The verdict of `quality-interaction`: how the app's source conforms to the rules `APP-DESIGN.md` decides — the applicable rule set of `## The applicable set` below, with its violations, one exemplar per rule, a score, ordered changes and the questions the run could not settle. `experience-interaction` folds its proposed exceptions, `(change)` candidates and questions into `APP-DESIGN.md` (`tree/APP-DESIGN.md § Writing it`), and `build-plan` reads the `open` entries of `runs[0].properties.changes`; a finding without a measured `file:line` misleads both.

The file is a SARIF 2.1.0 log (OASIS, errata 01) with exactly one run. SARIF gives the verdict a place for each thing a code scanner already records — rule, result, location, suppression — so a SARIF viewer or code-scanning upload reads it unchanged; what SARIF has no field for goes in `properties` bags, which the spec reserves for tool data. The stance is `tree/11_build/README.md § Stance`: a finding is measured at a `file:line`, or it is not one.

## Format

`$schema` is `https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json` and `version` is `"2.1.0"`. The file is written whole each run and is valid JSON: no comments, no trailing commas.

| What | SARIF field | Notes |
|---|---|---|
| the skill | `runs[0].tool.driver.name` = `quality-interaction` | `driver.properties.contract` = `rulebook/rules.md` |
| the rules checked | `driver.rules[]`: `id`, `name`, `shortDescription.text` | one per rule of the applicable set, whether or not a result cites it; ids are rulebook ids (`P<n>`, `H<n>`, `DF<n>`) or the app's own entry ids for a decision no rulebook rule covers |
| a violation | `results[]` with `kind: "fail"`, `ruleId`, `level`, `message.text`, `locations[]` | `level` from `tree/11_build/README.md § SARIF levels`; `message.text` is "expected … / actual …" |
| a violation's own data | `result.properties`: `id` (`V-1`), `entry`, `also[]`, `type`, `severity`, `class`, `tag` | `severity` keeps the four-level value; `class` is `consistency` or `completeness`; `tag` is `Qn` or empty |
| an exemplar | `results[]` with `kind: "pass"`, `level: "none"`, `ruleId`, `locations[]` | one per rule where one exists |
| a location | `locations[0].physicalLocation.artifactLocation.uri` + `region.startLine` (`endLine` for a span) | `uri` is repo-relative; an absence cites the nearest line and says `absence: …` in `message.text` |
| a proposed exception | on the violation's result: `suppressions: [{ kind: "external", status: "underReview", justification, properties: { id: "E-1", entry } }]` | `underReview` is the state SARIF defines for "not yet accepted"; the user's answer reaches `APP-DESIGN.md`, never this file |
| run-level data | `runs[0].properties`: `app_design_updated`, `checked_at`, `score`, `changes[]`, `coverage`, `questions[]`, `unchecked[]`, `unread[]` | shapes below |

`runs[0].properties` shapes:

- `score`: `{ "P5": { "violations": 3, "exemplars": 1, "status": "violated", "also": 1 } }`. `status` is `violated`, `conformant`, `by-decision` or `unchecked`; `also` appears only when other rules file a finding here.
- `changes[]`: `{ "id": "C-1", "kind": "systemic" | "per-type", "title", "covers": ["V-1"], "files": ["app/a.vue"], "status": "open" | "done" }`. `build-plan` reads the `open` ones.
- `coverage`: `{ "V-1": "C-1", "V-2": "proposed: E-1" }` — a change id or a proposed exception id.
- `questions[]`: `{ "id": "Q-1", "entry": "OBJ-3", "question", "evidence": "app/c.vue:9" }`.
- `unchecked[]`: rule ids with no violation, no `also` and no exemplar. `unread[]`: region strings such as `"app/legacy/**: 40 files, sampled by grep"`.

Example:

```json
{
  "$schema": "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [{
    "tool": { "driver": {
      "name": "quality-interaction",
      "properties": { "contract": "rulebook/rules.md" },
      "rules": [
        { "id": "P5", "name": "edit-surface-ladder", "shortDescription": { "text": "…" } },
        { "id": "H1", "name": "dialog-field-limit", "shortDescription": { "text": "adopted: 12" } },
        { "id": "P14", "name": "…", "shortDescription": { "text": "…" } }
      ]
    } },
    "results": [
      { "ruleId": "P5", "kind": "fail", "level": "error",
        "message": { "text": "expected: one editor per Room (MOD-2); actual: Room edited in a modal and a page" },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "app/a.vue" }, "region": { "startLine": 12 } } }],
        "properties": { "id": "V-1", "entry": "MOD-2", "also": ["P14"], "type": "Room",
                        "severity": "high", "class": "consistency", "tag": "" } },
      { "ruleId": "P7", "kind": "fail", "level": "note",
        "message": { "text": "expected: …; actual: …" },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "app/d.vue" }, "region": { "startLine": 40 } } }],
        "suppressions": [{ "kind": "external", "status": "underReview",
                           "justification": "…",
                           "properties": { "id": "E-1", "entry": "BTN-4" } }],
        "properties": { "id": "V-2", "entry": "BTN-4", "type": "Room",
                        "severity": "low", "class": "consistency", "tag": "" } },
      { "ruleId": "P5", "kind": "pass", "level": "none",
        "message": { "text": "conformant exemplar: single editor component" },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "app/b.vue" }, "region": { "startLine": 30, "endLine": 52 } } }] }
    ],
    "properties": {
      "app_design_updated": "YYYY-MM-DD",
      "checked_at": "YYYY-MM-DD",
      "score": { "P5": { "violations": 1, "exemplars": 1, "status": "violated", "also": 0 } },
      "changes": [
        { "id": "C-1", "kind": "systemic", "title": "…", "covers": ["V-1"],
          "files": ["app/a.vue"], "status": "open" }
      ],
      "coverage": { "V-1": "C-1", "V-2": "proposed: E-1" },
      "questions": [{ "id": "Q-1", "entry": "OBJ-3", "question": "…", "evidence": "app/c.vue:9" }],
      "unchecked": ["P12"],
      "unread": ["app/legacy/**: 40 files, sampled by grep"]
    }
  }]
}
```

## The applicable set

What the verdict measures is the rulebook as the app decided it, not the whole rulebook:

- **Invariants (`P`).** Every rule of `rulebook/rules.md` the app has not excepted. A rule the app has not decided is checked at its rulebook statement, because an invariant holds until an exception removes it.
- **Heuristics (`H`).** Only those the app lists in `## Adopted heuristics`, measured against the adopted value. An un-adopted heuristic is not checked, files no finding and is not counted `unchecked` — a value nobody chose cannot be violated.
- **Defaults (`DF`).** The bundle the app adopted, rule by rule; a default the app declined is an `## Exceptions` row.
- **Decided entries.** An entry replaces the default of the rule it cites (`adapt` included), and is itself checked; one that covers no rulebook rule is a rule of its own, filed under its entry id.
- **Exceptions.** A deviation in `## Exceptions` is not reported; the rule shows `by-decision`. `[open Qn]` entries are judged by their recommendation and tagged `Qn`.

## Counting

The score is computed, never typed: per `ruleId`, count results with `kind: "fail"` and `kind: "pass"`, add `also` counts from each fail result's `properties.also`, then write the object into `runs[0].properties.score`. A short Python `json` script or a `jq` filter does it; write the results first and let it run last.

## Writing it

`quality-interaction` checks the app's source (the roots `_concept/10_blueprint/techstack.md` and `_concept/02_grounding/findings/stack.md` name; otherwise `src/`, or the stack's own roots such as `app/` + `server/`) and writes this file. It judges conformance and nothing else: it changes no application code and does not edit `APP-DESIGN.md`, whose one writer is `experience-interaction`. A deviation worth keeping becomes a proposed exception here, and the user's answer reaches the file through that skill. Where things sit per stack, and how citations are checked, is `tree/02_grounding/findings/interaction.md § Where UI sits per stack`.

**Subagents.** Evidence passes that only collect — the surface census, the button scan, one grep pass per area — run in parallel on a small, fast model. Brief each with the detection rows it needs and the citation rule (paths from the repository root). They return `file:line` lists and write nothing; classifying and judging stay in this session, which checks their citations before using them.

1. **Read the intent.** Open `APP-DESIGN.md` per `tree/APP-DESIGN.md § Reading it`, then `rulebook/rules.md` and `rulebook/defaults.md` for the rules it cites, `_concept/glossary.md` for the nouns and the object axes, `docs/adr/` and the UI concept files named in `tree/02_grounding/findings/interaction.md § Intent and vocabulary`. Build the applicable set of `## The applicable set`. Confirm the app root, the code roots and the stack — a monorepo with several apps is a question for the user, not a guess.
2. **Take the surface census.** Every modal, drawer, popover and palette with purpose, host and trigger (`tree/02_grounding/findings/interaction.md § Editors and surfaces`), plus screens, object types and finders from their own sections of that node. When `_concept/02_grounding/findings/interaction.md` exists, start from it and re-verify each line at its cited `file:line`; a line the code no longer backs is dropped, because code that changed since the census is the usual cause of a finding nobody can reproduce. Skip generated and vendored code (`tree/02_grounding/findings/interaction.md § Generated and vendored code`).
3. **Walk the entries.** Go entry by entry through `APP-DESIGN.md`, then type by type through the object map of `## Objects`: index, home, editor, create flow, delete confirmation, representations, search. Per object also walk `## Information hierarchy`: a tier-1 attribute missing from the primary region of the screen that shows the object is a finding under `P21` (`absence:`); a tier-3 attribute rendered in a row, or anywhere outside a peek, popover or named disclosure, with no `## Exceptions` row for it is a finding under `P21`. Duplicated editing is judged on behaviour: two editor implementations of one object type, or divergent validation, labels or save path for one attribute, are findings under `P4`/`P3`; an attribute edited in several approved hosts through one shared editor is conformant, and a host the object map does not list is a `P4` finding of its own. Sample large files by pattern grep and keep a list of the regions left unread — a verdict that does not name them reads as complete when it is not. On a large app walk the core types and the entries of every area, and record each type or area not reached as `unread`.
4. **Record violations and exemplars.** One finding per distinct cause, filed under the most specific rule, listing the other rules it also breaks in `also` and counted once. Each violation carries the entry and rule id (`MOD-2 / P5`), the type, expected (quoted from the entry, or from the rule where the app decided nothing), actual, `file:line`, severity and class. Severity is one of the four levels of `tree/11_build/README.md § Flag shape`, placed by what users meet: `critical` — an edit or data is lost; `high` — users can see two values disagree or act on stale data; `medium` — an inconsistency users have to learn; `low` — clutter or hygiene. Class is `completeness` for what is absent (the palette lacks actions, a tier-1 attribute is not shown, a flow has no completion state) and `consistency` for what exists in two forms, so a count does not weigh a missing feature like a broken one. An absence cites `absence: <what is missing>` with the nearest `file:line`. A deviation the repo's ADRs or `_concept/glossary.md` already decided is an accepted exception or an *unimplemented decision* — say which; it is not a design flaw. Record one conformant exemplar per rule where one exists — it is what a fix copies. An entry whose *Why* or *Ref* the code contradicts, or that drops a rule's obligation without an exception, is not a violation: it becomes a question with its evidence, and the entry stands as written.
5. **Count.** Per rule of the applicable set: violations, exemplars, and a status — `violated` (a violation is filed under the rule or lists it in `also`), `conformant`, `by-decision` (satisfied only because an entry or exception loosened it; name the obligation that remains) or `unchecked` (no violation, no `also` and no exemplar: nobody looked or nothing was found, which is not a pass). Counts come from § Counting, never from typing. A finding filed under another rule shows there as `(+n)` from its `properties.also`.
6. **Order the changes.** Systemic first — a shared editor, the action registry, one confirm component — because each closes violations across many types; then per-type changes. Each change lists the violations it covers and the files it touches. End with a coverage table: every violation maps to a change, or to a proposed exception awaiting the user's answer. A violation in neither is an unfinished plan.
7. **Check the citations.** Run `tree/02_grounding/findings/interaction.md § Verifying citations` over the draft verdict, including the `: <line>` shorthand grep it ends with, and read a sample of the cited lines for meaning. A failing citation is fixed or the finding dropped before anything is written.
8. **Write the verdict** to `_concept/11_build/interaction.sarif` in the shape of § Format, replacing the previous run's file whole, so the file always describes the code as it is now. `level` follows `tree/11_build/README.md § SARIF levels` from the finding's severity, and `properties.severity` keeps the four-level value. Check that the file parses as JSON and has `version`, one run and `tool.driver.name` before reporting. Hand the results with an `underReview` suppression and `runs[0].properties.questions` back to the user and name `experience-interaction` as the skill that folds them into `APP-DESIGN.md`; the exception enters § Exceptions only on the user's answer.
9. **Report.** The score table first, then the changes in order with what each closes, then the unchecked rules, the unread regions and the questions.

## Checks

- The file parses as JSON and has `version` `"2.1.0"`, exactly one run and `tool.driver.name`.
- Every `fail` result cites a `file:line` that passes the citation check.
- Every rule of the applicable set is counted in `runs[0].properties.score` or listed in `unchecked`; no un-adopted heuristic and no excepted deviation is reported as a violation.
- Every tier-1 and tier-3 finding cites the object's row in `## Information hierarchy` as its expected value.
- Every violation is covered by a change or carries an `underReview` suppression.
- The unread regions are named in `unread`.
