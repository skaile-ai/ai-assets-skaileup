---
path: _concept/09_mockup/feedback/
summary: stakeholder annotations, their triage, reviewed patches and the audit trail
owner: [mockup-annotate, mockup-feedback]
may_propose: []
---

# _concept/09_mockup/feedback/

The one place a stakeholder's comment on the walkthrough becomes an edit to a spec. `mockup-annotate` instruments the built site and prepares `sessions/`; `mockup-feedback` adopts a returned session, triages it, authors one reviewable patch per annotation and, after a human approves the review file, applies the approved patches in one commit. A wrong route here edits the specs every downstream artifact is generated from.

## Contents

- `sessions/` — raw session files from the overlay (`tree/09_mockup/feedback/sessions/README.md`), gitignored.
- `triage/` — deterministic routing of each annotation to a file (`tree/09_mockup/feedback/triage/README.md`).
- `patches/` — proposed patches and the review file (`tree/09_mockup/feedback/patches/README.md`), gitignored.
- `applied/` — the lasting per-session record (`tree/09_mockup/feedback/applied/README.md`), committed.
- `devlog.md` — appended per apply (`tree/09_mockup/feedback/devlog.md`), committed.

## Format

### Lifecycle

`sessions/<sid>.json` → `triage/<sid>.json` → `patches/<sid>.json` + `patches/<sid>.review.md` → human approval → `applied/<sid>.json` + a `devlog.md` block + one git commit. A session counts as unapplied while `sessions/<sid>.json` has no `applied/<sid>.json` beside it. The rendered walkthrough is derived from the screens, so it is stale after an apply; `mockup-walkthrough` re-renders it, reading the devlog so the applied edits survive.

### Patch scope

1. A session annotation routes by its `specRef` to one file, `07_screens/<screen>.md`, which `mockup-feedback` co-owns for human-approved patches only (`tree/07_screens/[screen].md § Patching (mockup-feedback)`). The patch edits that file alone, anchored to a heading, and nothing else under `07_screens/` or `05_features/`.
2. A feature spec is `spec-feature`'s artifact and takes no patch. An annotation that asks for a different rule, scope line or permission becomes a `needs_manual` entry naming the screen's `implements:` feature file; the change itself is `spec-feature`'s to make for that feature.
3. `04_journeys/stories.yaml` takes no patch either: every diff anchors on a literal markdown heading, and the no-removes path of `apply.py` appends to the end of the file, which corrupts YAML silently. A journey annotation becomes a `needs_manual` entry quoting what was asked, so the comment reaches a human (`experience-journeys` owns the journey).
4. The feedback loop registers no new cross-reference: no screen is created, deleted or renamed, so the `implements:` / `screens:` links stay as they are.

### Id promotion

1. An element id the renderer auto-slugged is `provisional: true` in the screen's `elements:` frontmatter. The first time a human annotates it the id is worth keeping, so the promotion patch flips it to `provisional: false`; the id never changes, only its standing. Later renders use the promoted id and regeneration of the screen preserves it.
2. A navigation annotation on an element with no `target:` is promoted to a `target:` only when the destination resolves to exactly one `screen_id` in the walkthrough manifest.
3. A session annotation id is unique within its session only. It becomes a tracked id as the `annotationId` of the patches derived from it (`p-<annotationId>-<kind>`) and again in `applied/<sid>.json`, the lasting record once `sessions/` rotates.

## Writing it

### Annotating (mockup-annotate)

Turns a rendered walkthrough into a surface people can comment on and stops there. It edits only the built site, never a screen spec, and it is idempotent: a second run over an instrumented site changes nothing. The overlay resolves a click to the nearest `[data-spec-element]` and reads `data-spec-screen` / `data-spec-journey` off `<body>`, so it works against any renderer that honours `tree/09_mockup/walkthrough/README.md`.

1. **Locate the site.** `_concept/09_mockup/walkthrough/<renderer>/`, where `<renderer>` is the single subdirectory containing a `manifest.json`. Neither present means no walkthrough was built: say which is missing and name `mockup-walkthrough` as the skill that renders it. Read the manifest and note how many screens it lists and how many elements carry `"provisional": true`; the report tells the user, because a provisional id is one a reader's comment will promote.
2. **Copy the overlay** from `skills/mockup-annotate/overlay/annotation-overlay.js` to the **site root**, one copy for the whole site. An identical file already there: skip it and say so.
3. **Inject the script tag into every `.html` under the site root**, as the last line before `</body>`:

   ```html
   <script src="<relative-prefix>annotation-overlay.js"></script>
   ```

   The `src` is relative to the page: a page one directory down (`screen/<screen>.html`, `journey/<id>.html`) gets `../annotation-overlay.js` and each level deeper adds one `../`, because a bare filename on a nested page resolves against that page's own directory and silently loads nothing. Find the insertion point with a right-hand search for `</body>` (it appears once in a well-formed page and matching from the right survives any whitespace layout). A file that already references the overlay in a `<script>` tag is skipped whole. The tag has no `type="module"`: a module script is fetched with CORS against an origin `file://` does not have, so the plain tag is the only one a stakeholder opening `index.html` from a shared folder can load, and the validator rejects a module tag.
4. **Prepare the return path** under the project's `_concept/09_mockup/feedback/`: create `sessions/`. Append `_concept/09_mockup/feedback/sessions/` and `_concept/09_mockup/feedback/patches/` to the project `.gitignore` if absent. `applied/` and `devlog.md` stay committed: they are the audit trail of what feedback changed.
5. **Validate**: `python skills/mockup-annotate/validator.py _concept/09_mockup/walkthrough/<renderer>`. Exit 0 means every page carries the overlay as its last script and nothing external crept in; exit 2 lists the pages that do not.
6. **Report.** Name the site root, the injected/skipped counts, the session directory and the provisional-id count. Then tell the user the two things only they can do: open `index.html` and check that clicking an element in Annotate mode opens the popover, and share the site with the readers together with the instruction under *Getting the notes back*.

**Getting the notes back.** The reader opens the site in a browser, ticks **Annotate**, comments across as many pages as they like and clicks **Download**. The overlay carries the round in `sessionStorage`, so it survives moving between screens and ends when the tab closes: the reader downloads before finishing. The download is named `<session-id>.json` and is **sent back unrenamed**, because the id inside the file keys triage, patching and the audit trail and a disagreeing filename produces a round that reads as never applied. The reader's last act is to send the file (attachment, shared folder, whatever the team does); `mockup-feedback` takes it from any path and files it itself, so nobody places it in `_concept/` by hand. Say this in the report: a downloaded file nobody sends on is a round that silently never happened. Inside an embedding host the overlay posts each annotation to the parent frame instead; no host implements that listener today, so the browser path is the one that works. The session schema is `tree/09_mockup/feedback/sessions/README.md`.

### Filing feedback (mockup-feedback)

One pass over one session file: adopt, triage, patch, apply. It ends with edited screen specs, an audit trail and exactly one commit. It never edits the walkthrough. The pass stops in the middle: step 5 hands a human the review file and waits, everything before it is proposal and everything after is execution, and nothing is written into `_concept/` spec files until that approval. Patch and review-file formats: `tree/09_mockup/feedback/patches/README.md`.

1. **Adopt, if the file has not landed yet.** A reader's download sits wherever they sent it (downloads folder, attachment, shared drive) and filing it is this skill's job. Given a path, check it against the session schema in `tree/09_mockup/feedback/sessions/README.md`, then copy it to `_concept/09_mockup/feedback/sessions/<sessionId>.json`, taking the name from the file's own `sessionId` and never from the path you were handed. Then ask the user what to call this round (*"the Sept 5 stakeholder review"*) and write it into the file as `label`, the only human-readable handle a session gets. A `sessions/<sessionId>.json` that already exists is the same round re-downloaded later with more in it: replace it, keeping the existing `label`.
2. **Pick the session.** An unapplied session is one with no `applied/<sid>.json` beside it. Several unapplied: name them **by their `label`** and let the user choose; merging two rounds into one commit loses which round asked for what.
3. **Triage, deterministic, no judgement.**

   ```
   python skills/mockup-feedback/scripts/triage.py \
       _concept/09_mockup/feedback/sessions/<sid>.json _concept/ _concept/09_mockup/feedback/triage/
   ```

   Report the unresolved count and each reason: an unresolved annotation is a comment nobody will see again, and the script still exits 0. Format and routing rules: `tree/09_mockup/feedback/triage/README.md`.
4. **Author a patch per annotation** under § Patch scope and § Id promotion. Work one triage group (one target file) at a time. Read the file first and write the diff in that file's own voice, anchored to the section it changes. `change` is the one category that needs judgement: read the section the annotated element appears in and rewrite it to carry the annotation's intent, scoped to the lines that actually move. Every other category follows its template in `tree/09_mockup/feedback/patches/README.md`; an LLM rewrite of a one-line append invents variation where the reader asked for none. Copy each annotation's `body` verbatim into its patch, because the session file is gitignored and rotates and this copy is the only lasting record of what was asked. The two derived patches (id promotion, `target:` promotion) follow § Id promotion; an annotation you cannot patch becomes a `needs_manual` entry naming why. Write `patches/<sid>.json` and `patches/<sid>.review.md` together.
5. **Present the review file and wait.** Every proposed patch is listed pre-checked in `patches/<sid>.review.md`; the user unchecks what to skip and may edit a diff in place. Say plainly that nothing is applied until they come back, and name any `needs_manual` bullets so they are not mistaken for silently dropped comments. Then stop: applying an unreviewed patch set is the one failure this skill cannot walk back.
6. **Pre-flight, then apply.** First check that the git working tree is clean (`git status --porcelain` empty; apply commits, and a dirty tree puts unrelated work in that commit), that `patches/<sid>.json` validates against the patches schema in `tree/09_mockup/feedback/patches/README.md`, and that every checked patch id in the review file exists in the patch file. Then:

   ```
   python skills/mockup-feedback/scripts/apply.py \
       _concept/09_mockup/feedback/patches/<sid>.json _concept/09_mockup/feedback/patches/<sid>.review.md \
       _concept/ _concept/09_mockup/feedback/
   ```

   The script applies each checked patch best-effort, writes `applied/<sid>.json`, appends to `devlog.md` and makes one commit (`tree/09_mockup/feedback/applied/README.md`). Exit 2 means every patch failed: nothing was written or committed; fix the diffs and re-run, no `--force` needed. Exit 1 is a pre-flight refusal it caught itself. Exit 0 may still carry failures, recorded per patch with their error.
7. **Report** the applied and failed counts, the commit message, and the paths of `applied/<sid>.json` and the devlog. Print each failure with its reason and the retry: edit the review file, uncheck what already landed, re-run with `--force`. When the review file carried a `## Test impact` section, say that the changed specs affect test coverage and name the skill that regenerates it.

## Checks

- Annotating is done when the validator exits 0, `sessions/` exists, and the user has the site root and the reader instruction in front of them.
- Filing is done when one commit exists carrying the edited specs, `applied/<sid>.json` and the devlog append, and every annotation in the session appears in `applied/<sid>.json`, in `needs_manual`, or in the triage file's unresolved list.
