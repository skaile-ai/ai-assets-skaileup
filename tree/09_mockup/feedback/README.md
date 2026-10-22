---
path: _concept/09_mockup/feedback/
summary: how open prototype notes become spec edits and model proposals
owner: [mockup-feedback]
may_propose: []
---

# _concept/09_mockup/feedback/

The one place a stakeholder's note on the prototype becomes an edit. The notes themselves are not stored here: they live in the project's annotation inbox, `<project>/.data/annotations/`, where the prototype's annotation toolbar writes them (`tree/09_mockup/storybook/README.md § Annotation`). `mockup-feedback` reads the open notes, routes each to the file it belongs in, authors one reviewable patch per note and, after a human approves the review file, applies the approved patches in one commit and closes the notes in the inbox. A wrong route here edits the specs, or the data model, that every downstream artifact is generated from.

## Contents

- `triage/` — deterministic routing of each open note to a file (`tree/09_mockup/feedback/triage/README.md`).
- `patches/` — proposed patches and the review file (`tree/09_mockup/feedback/patches/README.md`), gitignored.
- `applied/` — the lasting per-round record (`tree/09_mockup/feedback/applied/README.md`), committed.
- `devlog.md` — appended per apply (`tree/09_mockup/feedback/devlog.md`), committed.

## Format

### Lifecycle

Open notes in `.data/annotations/items/` → `triage/<round>.json` → `patches/<round>.json` + `patches/<round>.review.md` → human approval → `applied/<round>.json` + a `devlog.md` block + one git commit → the answered notes closed in the inbox with a resolution. A round id names one pass (`r-<UTC timestamp>` unless the user gives a name); it keys the files above and appears in the commit message. A note is open until a round resolves it: a note whose patch was unchecked, failed or went to `needs_manual` stays open and appears again in the next triage.

### Patch scope

1. A note on a screen's story routes to `07_screens/<screen>.md`, which `mockup-feedback` co-owns for human-approved patches only (`tree/07_screens/[screen].md § Patching (mockup-feedback)`). The patch edits that file alone, anchored to a heading, and nothing else under `07_screens/` or `05_features/`.
2. A note on an entity's editor or display component routes to `10_blueprint/datamodel/model.ts`. The patch is a **proposal**: it appends a field to that entity or a new entity, marked `proposed: { by: 'mockup-feedback', on, source }` with the note's `inboxId` as `source`, and removes or changes nothing else in the file (`tree/10_blueprint/datamodel/model.md § Format`). The owner promotes the proposal later by removing the marker.
3. A new or changed domain term the note introduces goes into the glossary as a proposal in the same round, marked `status: proposed` with the same `source` (`tree/glossary.md § Where the words live`). The patch step chooses the glossary file from the project's `scope.yaml` `glossary` key; the router never routes to it.
4. A feature spec is `spec-feature`'s artifact and takes no patch. A note that asks for a different rule, scope line or permission becomes a `needs_manual` entry naming the screen's `implements:` feature file.
5. `04_journeys/stories.yaml` takes no patch: every diff anchors on a literal markdown heading, and the no-removes path of `apply.py` appends to the end of the file, which corrupts YAML silently. A journey note becomes a `needs_manual` entry quoting what was asked, so the comment reaches a human (`experience-journeys` owns the journey).
6. A note on a floorplan, on the app shell, or without a source position (`target.kind` is `route`) routes nowhere: it ships with the package, not with the concept, and stays in the triage file's unresolved list.
7. The feedback loop registers no new cross-reference: no screen is created, deleted or renamed, so the `implements:` / `screens:` links stay as they are.

### Notes and resolutions

1. An inbox item's `inboxId` is unique across rounds. It becomes a tracked id as the `inboxId` of the patches derived from it (`p-<inboxId>-<kind>`) and again in `applied/<round>.json`, the lasting record.
2. Every patch carries `resolves[]`: for each note it answers, the status (`implemented` or `rejected`) and one sentence saying what was done or why not. The inbox refuses `rejected` without a reason, because the reason is what a refusal is for.
3. A note is closed only when every patch that lists it has been applied; the resolution text is the one the human approved in the review file.

## Writing it

### Filing feedback (mockup-feedback)

One pass over the open notes: triage, patch, apply, resolve. It ends with edited specs, proposals in the model, an audit trail and exactly one commit. It never edits the prototype's code; `mockup-storybook` re-derives that from the changed specs and model. The pass stops in the middle: step 4 hands a human the review file and waits, everything before it is proposal and everything after is execution, and nothing is written into `_concept/` spec files until that approval. Patch and review-file formats: `tree/09_mockup/feedback/patches/README.md`.

1. **Read the open notes.** The `annotation-inbox` skill lists them from `<project>/.data/annotations/`; skim them so the round's size is known. No open note means nothing to file: say so and stop. `patches/` and the inbox's `.data/` are local state, so append `_concept/09_mockup/feedback/patches/` and `.data/` to the project `.gitignore` when absent. Several rounds' worth of notes are one round unless the user asks to split by story; merging is cheap, because every patch is traceable to its `inboxId`.
2. **Triage, deterministic, no judgement.**

   ```
   python skills/mockup-feedback/scripts/triage.py _concept/ _concept/09_mockup/feedback/triage/ --round <round>
   ```

   `--inbox <dir>` overrides the default `.data/annotations` beside `_concept/`. Report the unresolved count and each reason: an unresolved note is a comment nobody will see again, and the script still exits 0. Format and routing rules: `tree/09_mockup/feedback/triage/README.md`.
3. **Author a patch per note** under § Patch scope. Work one triage group (one target file) at a time. Read the file first and write the diff in that file's own voice, anchored to the section it changes. A screen note needs judgement: read the section the note's element sits in and rewrite it to carry the note's intent, scoped to the lines that actually move. An entity note asks what the editor needs and the model lacks: propose the field or entity and give the glossary its term. Copy each note's `comment` verbatim into its patch `body`, because the inbox rotates and this copy is the only lasting record of what was asked. Write a note the file cannot carry as `needs_manual`, with the reason. Write `patches/<round>.json` and `patches/<round>.review.md` together, then validate them (`## Checks`).
4. **Present the review file and wait.** Every proposed patch is listed pre-checked in `patches/<round>.review.md`; the user unchecks what to skip and may edit a diff or a resolution in place. Say plainly that nothing is applied until they come back, and name any `needs_manual` bullets so they are not mistaken for silently dropped comments. Then stop: applying an unreviewed patch set is the one failure this skill cannot walk back.
5. **Pre-flight, then apply.** First check that the git working tree is clean (`git status --porcelain` empty; apply commits, and a dirty tree puts unrelated work in that commit), that `patches/<round>.json` validates, and that every checked patch id in the review file exists in the patch file. A patch on `model.ts` needs `gen.ts` and the schemas beside it in `10_blueprint/datamodel/` (`tree/10_blueprint/datamodel/skaile-model.md`); without them the patch fails and says so. Then:

   ```
   python skills/mockup-feedback/scripts/apply.py \
       _concept/09_mockup/feedback/patches/<round>.json _concept/09_mockup/feedback/patches/<round>.review.md \
       _concept/ _concept/09_mockup/feedback/
   ```

   The script applies each checked patch best-effort; after `model.ts` changed it runs `gen.ts`, and when `gen.ts` rejects the file it restores `model.ts` and fails every proposal patch with the generator's message. It then writes `applied/<round>.json`, appends to `devlog.md`, makes one commit, and only then closes the answered notes through the prototype's `scripts/resolve.ts` (`tree/09_mockup/feedback/applied/README.md`). Exit 2 means every patch failed: nothing was written or committed; fix the diffs and re-run, no `--force` needed. Exit 1 is a pre-flight refusal it caught itself, or a failed commit, after which the tree is restored and no note is closed. Exit 0 may still carry failures, recorded per patch with their error.
6. **Report** the applied and failed counts, the commit message, and the paths of `applied/<round>.json` and the devlog. Print each failure with its reason and the retry: edit the review file, uncheck what already landed, re-run with `--force`. Name every note whose resolution is `pending` with the command from `applied/<round>.json`: the prototype package is not installed, so the user runs that command once to close the notes. When the review file carried a `## Test impact` section, say that the changed specs affect test coverage and name the skill that regenerates it. When the round changed `model.ts`, name `mockup-storybook` as the skill that builds the new field into the editor.

## Checks

Filing is done when one commit exists carrying the edited files, `applied/<round>.json` and the devlog append, and every note of the round appears in `applied/<round>.json` as a resolution, in `needs_manual`, or in the triage file's unresolved list.
