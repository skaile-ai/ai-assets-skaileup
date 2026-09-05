# Recon 22 — What the iron laws still gate

Evidence only. `S/` = `ai-assets-skaileup` (old, quoted from `main`), `MP/` = `ai-assets-skaileup-mp`,
`FC/` = `forge/forge-concept`, `WS/` = `workspaces`.

## A. The contract, verbatim

`MP/contracts/iron_laws.md` is **119 lines and byte-identical to `S/skaileup/contracts/iron_laws.md`**
(`diff` clean). It was copied, not ported. Its own header states the premise ticket 09 kept it on:
*"Skills enforce these via their `requires` field (flow node or SKILL.md frontmatter). This document
explains the WHY behind each gate."* (`:4-5`).

| law | line | text | machine counterpart in `MP/skills/` today |
|---|---|---|---|
| 1 NO CONCEPT WORK WITHOUT A BRIEF | `:11-13` | "Every conceptualization skill requires `discovery/brief.md`" | **live** — `spec-feature:15` + `build-branch:10` hard-gate `brief.md` (0007's root file). Path text stale, substance holds. |
| 2 NO DATA MODEL WITHOUT FEATURES | `:19-21` | "`blueprint/datamodel/` requires `experience/features/` with at least one feature file" | **none** — no `MP` skill writes a datamodel (architecture domain unported, ticket 18). |
| 3 NO SCREENS WITHOUT BRAND TOKENS | `:27-30` | "`experience/screens/` requires `discovery/brand/tokens.json` … unless the brand step was explicitly skipped by the user" | **contradicted** for the screen writer (§B); still hard in `mockup-walkthrough:15` and `mockup-storybook:15`, both on pre-0007 paths. |
| 4 NO SCREENS WITHOUT DATA MODEL | `:36-38` | "`experience/screens/` requires `blueprint/datamodel/model.json`" | **contradicted** — `spec-feature:17` gates `10_blueprint/datamodel` **soft**. |
| 5 NO MOCKUPS WITHOUT SCREEN SPECS | `:44-46` | "The `mock` skill requires `experience/screens/` with at least one screen file" | **live under another name** — `mockup-walkthrough:13` hard + `min_entries: 1`; `mockup-storybook:14` same. Skill name is phantom (§F). |
| 6 NO IMPLEMENTATION WITHOUT READINESS CHECK | `:52-55` | "…either via the `ready` skill gate or by checking these paths directly" | **none** — `ready` does not exist in `MP` (§G). `build-plan`/`build-implement` do "check these paths directly". |
| 7 NO ARTIFACT WITHOUT PREREQUISITES | `:61-63` | "A skill must verify its `requires` paths … before producing any output" | **already duplicated** in `MP/contracts/agent_patterns.md:8-20` (§ Read-Context-First). |
| 8 NO OVERWRITING WITHOUT APPROVAL | `:69-71` | "Never overwrite user-modified files without showing the diff…" | stated at its step: `spec-feature:74-75`, `build-implement:51-52`, `mockup-feedback:21`. `agent_patterns:135` has an input-values-only variant. |
| 9 QUESTIONS ARE STANDALONE MESSAGES | `:77-80` | "…send it as its own dedicated message… See `agent_patterns.md` Communication Style for examples." | **already duplicated** in `MP/contracts/agent_patterns.md:48-68`, with the worked wrong/right example. Law 9 itself points there. |

**The ticket's "six of nine are stale" is correct as a count** (1-6), and its path table is correct
row for row against `MP/contracts/concept_structure.md` (`brief.md` `:17`, `05_features/` `:55`,
`07_screens/` `:61`, `03_brand/tokens.json` `:48`, `10_blueprint/datamodel/` `:78`).

Two corrections to the ticket's own citations:

- **`spec-feature` line numbers are off by one.** The ticket cites `:9-10,17`. `brand-tokens: soft`
  is `:10` and `datamodel: soft` is `:11`; `:9` is `journeys: soft`. The `prerequisites.files`
  datamodel entry is `:17` as cited.
- **`iron_laws.md` has more than two mentions in `MP`.** Besides `contracts/README.md:14,47` it is
  named at `docs/adr/0004-contracts-earn-their-place.md:18,37` — where ADR 0004 records the exact
  premise now under review: *"`iron_laws` and `golden_principles` are **not** in tension with ADR
  0003 — that ADR removed…"*.

**Not in the ticket:** `model.json` (law 4's object) is not named in ADR 0007's tree.
`concept_structure.md:78` says only `datamodel/   schema, seed data, feature cross-reference`; the
filename survives in `golden_principles.md:80,83-84`, `semantic_types.md:6,124`, `seed_data.md:9,103`
and `concept_structure.md:185`. So law 4 gates on a filename no `MP` skill writes and no `MP` skill
declares.

## B. What a demoted gate actually costs — **nothing, for either value**

This is the crux, and it does not come out where the ticket expects.

**The declared gates.** `MP/skills/spec-feature/SKILL.md:5-17`:

```yaml
artifacts:
  requires:
    - { id: scope, gate: hard }        # :7
    - { id: brief, gate: hard }        # :8
    - { id: journeys, gate: soft }     # :9
    - { id: brand-tokens, gate: soft } # :10
    - { id: datamodel, gate: soft }    # :11
prerequisites:
  files:
    - { path: "01_meta/scope.yaml", gate: hard }        # :14
    - { path: "brief.md", gate: hard }                  # :15
    - { path: "04_journeys/stories.yaml", gate: soft }  # :16
    - { path: "10_blueprint/datamodel", gate: soft }    # :17
```

Confirmed: **`tokens.json` appears in neither block.** Law 3's object has no file-level declaration
at all in `spec-feature`; only the artifact-id `brand-tokens`, which is a different mechanism.

**Every reader of `gate`, traced.**

1. **`prerequisites.files[].gate`** — `WS/packages/workspaces/resolver/src/parser.ts:69-74`
   (default `"hard"` when absent) → `validator.ts:79-104` (existence probe per file) →
   `validator.ts:149`:
   ```ts
   const hardFilesSatisfied = files.filter((f) => f.gate === "hard").every((f) => f.exists);
   ```
   A **soft** entry is probed and reported (`files[]` carries `exists`) but is excluded from
   `satisfied`. It never blocks and it never warns — **soft is report-only; the caller decides
   whether a missing soft file means anything.**
2. **Preamble prose** — `resolver/src/preamble.ts:50-57` renders `REQUIRES` with a literal
   `hard:` / `soft:` prefix per line. Reached only from
   `workspace-plugin/src/tools/skills.ts:277` (`skillGetPreamble`), exposed as the MCP tool
   `skill_get_preamble` (`adapters/mcp.ts:185-186`) — an agent must call it. Not automatic.
3. **`artifacts.requires[].gate`** — **read by nothing.**
   `WS/discovery/src/requires-graph.ts:236-249` (`extractSkillRequires`) reads `r.id` only and emits
   a dependency edge; `gate` is never touched. Zod declares it
   (`types/src/manifests/_shared.ts:36`) and stops there. `FC/server/utils/artifact-contract.ts`
   reads `contracts/artifacts.yaml`, not this field — and ticket 01 already ruled that file
   unreachable as deployed.
4. **`FC` surface** — `FC/server/api/flows/nodes/[nodeId]/requirements.get.ts:50,54` is the only
   place `FC` calls the resolver. **It has zero callers.** Grep for `requirements` across
   `FC` `app/ server/ shared/` (excluding `node_modules`, `.nuxt`, vendored `forge-common`)
   returns four hits, all inside that route file. The route also calls the `async`
   `validateRequirements` without `await` (`:54`).
5. **The UI's "Hard gates" panel is not this.** `FC/app/components/GateInfo.vue:37-43` renders
   `focusedNode.blockers` (`FC/app/pages/concepts/index.vue:22`), and `blockers` is computed from
   **flow edges**, not file gates: `FC/server/utils/flow-extended-state.ts:47-50`
   (`flow.edges.filter(e => e.target === n.id && e.type === "flow" && !satisfied(e.source))`).

**And then the frontmatter never reaches reader 1 or 3.** `parser.ts:45-46`:

```ts
const meta = fm.metadata ?? {};
const prerequisites = meta.prerequisites ?? {};
```

There is **no root-level fallback** — the whole file has two `fm.` reads (`:45` and the frontmatter
match). Same for the artifact edges: `requires-graph.ts:236-238` returns early on
`if (!metadata) return;`. **No skill in `MP/skills/` has a `metadata:` key at all**
(`grep -rn "^metadata:" MP/skills/` → 0 hits); all eight put `artifacts:` and `prerequisites:` at
the root. The old collection nests them (`S/skaileup/03_experience/03_screens/SKILL.md:20,38`), and
so does the resolver's own fixture (`WS/resolver/tests/parser.test.ts:6-11`).

Verified against **the deployed artifact, not just source**:
`FC/node_modules/@skaile/workspaces@0.48.1/dist/chunk-GXC3TYMQ.js`, `parseSkillRequirements` —
identical `fm.metadata ?? {}` line.

Second, independent break: **the paths carry no `_concept/` prefix.** `validator.ts:81` does
`path.join(projectDir, req.path)` and `projectDir` is `getProjectRoot()`
(`requirements.get.ts:51`) — the *project* root, not `_concept/`. Every old-repo declaration
carries the prefix (`_concept/experience/features`, `WS/resolver/tests/validator.test.ts:34`);
no `MP` declaration does.

**So for every `MP` skill, `parseSkillRequirements` returns `empty` and `satisfied` is vacuously
`true`.** Ticket 19's demotion of two gates from hard to soft changed nothing observable, because
`spec-feature`'s two *hard* gates are equally unenforced. The ticket's framing —
"what carries the gates today is `prerequisites.files[].gate` … So the file explains gates it does
not enforce" — is **half right**: the file does not enforce them, and neither does the frontmatter,
as `-mp` currently writes it.

`MP/docs/skill-template.md:13-17` is where the convention was fixed, and it states the opposite
of both findings: *"`artifacts.requires[].id + gate` — **hard gates the flow engine enforces**"*
and *"`prerequisites.files[]` — path gates"*, shown at the root of the fence. Ticket 01's own
research had it right and the template did not carry it over:
`S/.scratch/skaileup-mp/research/01-machine-layer-public-api.md:357` (branch
`research/machine-layer-api`) — *"`metadata.prerequisites.files[]` … **READ — hard/soft gates**"*.

## C. Where the gates live now — all eight `MP` skills

Paths verbatim from frontmatter; `_concept/`-relative, prefix absent in every row.

| skill | `prerequisites.files[]` (line) | gate | 0007? |
|---|---|---|---|
| `spec-feature` | `01_meta/scope.yaml` `:14` · `brief.md` `:15` | hard · hard | ✅ ✅ |
| | `04_journeys/stories.yaml` `:16` · `10_blueprint/datamodel` `:17` | soft · soft | ✅ ✅ |
| `build-plan` | `05_features` `:13` · `07_screens` `:14` (both `min_entries: 1`) | hard · hard | ✅ ✅ |
| | `10_blueprint/techstack.md` `:15` · `10_blueprint/datamodel` `:16` | soft · soft | ✅ ✅ |
| `build-implement` | `11_build/slices` `:13` · `05_features` `:14` · `07_screens` `:15` (all `min_entries: 1`) | hard ×3 | ✅ |
| `build-branch` | `brief.md` `:10` | hard | ✅ |
| `mockup-walkthrough` | `experience/screens` `:13` · `experience/journeys/stories.yaml` `:14` · `discovery/brand/tokens.json` `:15` | hard ×3 | ❌ pre-0007 |
| | `experience/features` `:16` | soft | ❌ |
| `mockup-storybook` | `experience/screens` `:14` · `discovery/brand/tokens.json` `:15` · `blueprint/techstack.md` `:16` | hard ×3 | ❌ |
| | `experience/journeys/stories.yaml` `:17` | soft | ❌ |
| `mockup-annotate` | `mockup-walkthrough` `:10` (`min_entries: 1`) | hard | ❌ |
| `mockup-feedback` | `_feedback/sessions` `:10` (`min_entries: 1`) | hard | ❌ |

**Law by law, does a frontmatter counterpart exist:** 1 ✅ · 2 ❌ · 3 ✅ but only in the mockup pair,
and **absent from the screen writer** · 4 ✅ demoted to soft · 5 ✅ · 6 ❌ · 7-9 not path-shaped.

`min_entries` (`parser.ts:73`, `validator.ts:97-100`) is the machine form of the laws' "at least one
… file" clause, and it is present in exactly the two places laws 2 and 5 name it.

Law 3's escape hatch — *"unless the brand step was explicitly skipped by the user"* — does have a
machine form: `validator.ts:74,76-79` treats any path in `overrides.skip_checks` as present, fed
from flow-node `data.overrides` (`requirements.get.ts:52`, engine type
`factory-assets/connectors/flow/engine/types.ts:126`). **`MP/contracts/flow.schema.json` declares
neither `overrides` nor `skip_checks`** (`grep -c` → 0), and `MP/flows/` holds only a `README.md`.

## D. Readers — the ticket's premise verified, and one number imported from the wrong repo

**`iron_laws.md` in `MP` — zero in-body readers, confirmed.** Full grep
(`grep -rn "iron_laws\|Iron Law\|iron law" .` minus `.git/`) returns 5 hits, and no skill is among
them: `contracts/README.md:14` (tree drawing), `:47` (table row — in a README that is stale
wholesale: it still lists `frontmatter.md`, `skill_grammar.md`, `flows.md`, `cf/`, `saxe/` and
`scripts/`, all deleted), `contracts/iron_laws.md:1` (itself), and
`docs/adr/0004:18,37`. **No `MP/skills/**/SKILL.md` mentions it.** For calibration, the eight `MP`
skills cite eight other contracts by name, 28 times: `walkthrough_renderer` ×12, `slice_loop` ×5,
`elements_block` ×4, `feedback_loop` ×2, `concept_structure` ×2, `domain_model` /
`artifact_frontmatter` / `acceptance_criteria` ×1.

**`iron_laws.md` in `S` — 84 hits across 41 of 88 `SKILL.md` files**
(`git grep -n "iron_laws" main -- '*SKILL.md'`). Split by ticket 09's bar:

- **39 are `REFERENCES` / `REQUIRED BACKGROUND` citations** — lines matching
  `^\s*[-|]?\s*\`?contracts/iron_laws\.md`, e.g. `03_experience/02_behaviors/SKILL.md:90`.
- **24 are `MUST`/`NEVER` block lines** (`^(MUST|NEVER)`) — the block ADR 0003 deletes, e.g.
  `08_concept-slice/03_scope-feature/SKILL.md:89`.
- **~12 are genuine in-body step reads**, across 8 skills:
  `00_.../scope-project/SKILL.md:122,204`, `08_concept-slice/02_align:175`,
  `11_impl-plan/02_align:213`, `12_impl-slice/04_test:149`, `12_impl-slice/06_refactor:223,229`,
  `12_impl-slice/07_commit:219,220`, `13_impl-quality/13_review-feature:134`, `14_ops/12_trace:123`.
- Remainder are `| Must read |` table rows and "Required background" prose.

**Every one of those citations names law 7, 8 or 9 and nothing else.** Counting `§` tokens across
all `S` `SKILL.md`: **§ 7 ×24, § 8 ×10, § 9 ×29, and § 1-6 zero.** Cross-checked by name:
`git grep -n "NO CONCEPT WORK\|NO DATA MODEL WITHOUT\|NO SCREENS WITHOUT\|NO MOCKUPS WITHOUT\|NO IMPLEMENTATION WITHOUT" main -- '*SKILL.md'` → **0 hits.** In 95 skills over the file's whole life,
**the six path laws were never once cited by a skill.** The three that were cited are the three the
ticket proposes to move out.

**`agent_patterns.md` in `MP` — also zero in-body readers.** Same grep shape: `contracts/README.md:15,48`,
`contracts/iron_laws.md:80` (law 9 pointing at it), `docs/adr/0005:59`, `docs/adr/0006:47`. **No skill.**
The ticket's parenthetical *"`agent_patterns.md` (9 in-body readers)"* is **ticket 09's count against
the old repo** carried across without relabelling — in `S`, `agent_patterns` appears in 15 `SKILL.md`
files. As a destination inside `MP` today, it is exactly as unread as `iron_laws.md`.

`agent_patterns.md` has its own staleness, if laws are moved into it: `:11` gates on "flow node
`requires`"; `:27` reads `user_inputs.dialog`; `:28` names
`_concept/_grounding/{folder}/user_input.json` while the resolver reads
`_concept/_grounding/<skillId>/input.json` (`validator.ts:110`, `preamble.ts:66`); `:179` is the
Implementer Status Report — the 4-status protocol ticket 07 deleted with `impl-plan-supervised`;
`:95` Standards Injection and `:214` Expert Discovery both point at skills ticket 17 has not ruled on;
`:217` reads `_concept/blueprint/techstack.md`, pre-0007.

## E. Laws 7-9 and the two tables (`:87-119`, 33 of 119 lines)

**Rationalization Defense** (`:89-100`, 10 rows) and **Red Flags** (`:104-117`, 7 rows). Contrary to
the ticket's *"three of their rows name deleted skills or the pre-0007 tree"* — **no row contains a
pre-0007 path.** The only path-shaped token in either table is `` `_concept/` `` at `:99`, which
ADR 0007 keeps (`concept_structure.md:7-11`, fixed by four `FC` source sites). What is stale is
*named machinery*:

- **`:94`** — *"Use a lighter flow (e.g. `prototype`)"*. **No flow named `prototype` exists.**
  `S` ships 17 (`git ls-tree -r main | grep flow.yaml`): `appbuilder-{cli,mvp,simple,standard,complex}`,
  `architecture`, `concept-discovery`, `impl-build-setup`, `mockup-feedback`, `quality-gate`,
  `skaileup-{concept-only,concept-reverse,implementation,slice,slice-concept,slice-impl,stepwise}`.
  `MP/flows/` is empty. `prototype` is a **global mp skill**, not a flow — the row points a reader
  at an affordance that never existed in this collection.
- **`:96`** — *"Write the test plan alongside features."* `impl-quality-test-plan` is one of the 13
  skills ticket 17 owns, and one of the four ticket 17 records as referenced by **zero flows**.
- **`:98`** and **`:115`** — the same rule twice: spec compliance before quality review. Its two
  sources in `S` are `11_impl-plan/04_supervised/SKILL.md` (**deleted by ticket 07**) and
  `12_impl-slice/02_implement/SKILL.md` (**survives**). It is now stated at its step:
  `MP/skills/build-implement/SKILL.md:35-39` — *"Review against the spec before reviewing the code…
  a quality review of the wrong feature is wasted work."* So the table row duplicates a rule that
  already lives where ADR 0003 puts it.
- **`:93`** — *"Structure them with component inventory, states, and seed data references"* describes
  the pre-`elements:` screen-spec shape; `spec-feature:66-70` writes an `elements:` block per
  `contracts/elements_block.md` instead.
- Live and unproblematic: `:91`, `:92`, `:95`, `:97`, `:99`, `:100`, `:111`-`:114`, `:116`, `:117`.
- Closing line `:119` — *"Violating the letter is violating the spirit. No rationalization overrides
  these laws."*

Row `:97` (*"I'll just ask at the end of this update"*) and Red Flag `:116` are law 9 restated a third
and fourth time, after `iron_laws:77-83` and `agent_patterns:48-68`.

## F. Law 5's phantom skill

**No `mock` skill exists in either repo.** `S`: `git grep -n "^name: mock$" main -- '*SKILL.md'` → 0;
no directory `mock/` in `git ls-tree -r main`. `MP/skills/` holds eight directories, none named
`mock`. The domain ported (tickets 06, 14) as **`mockup-walkthrough` · `mockup-storybook` ·
`mockup-annotate` · `mockup-feedback`**. Law 5's *substance* is the only one of the six path laws
whose gate is stated twice, hard, with `min_entries: 1` — `mockup-walkthrough:13` and
`mockup-storybook:14` — so the law is right and only its subject's name is dead.

## G. Law 6 / `ready` — flagged, not ruled (ticket 17 owns it)

Law 6 (`:52-57`): *"Implementation skills should verify that features, screens, data model, and tech
stack all exist — either via the `ready` skill gate or by checking these paths directly."*

- In `MP`, **`ready` exists only inside law 6 itself** — grep for `ready` across `MP/skills/` and
  `MP/contracts/` returns `iron_laws.md:55` plus three unrelated prose uses of the English word.
- In `S`, the skill is `impl-quality-ready` (`skaileup/13_impl-quality/07_ready/SKILL.md:2`), and its
  own description is *"verify all features are complete enough to test. Checks each feature for
  concept doc, screen spec, data model entry, brand tokens, and tech stack"* — law 6 restated.
- **Overlap with ticket 17, exact:** `issues/17-quality-domain.md:23-25` already puts `ready` on the
  wrong side of ticket 04's `quality`/`ops` line — *"`quality` checks `src/`, `ops` checks
  `_concept/`. Some of these 13 are on the wrong side of that line — `ready` inspects `_concept/`
  completeness."* Law 6's second clause ("or by checking these paths directly") is **already
  satisfied** by `build-plan:13-16` and `build-implement:13-15`, which hard-gate features + screens
  and soft-gate techstack + datamodel — i.e. the law's four items, three of them by direct check.

## H. Things a decider would not think to ask

1. **The file was copied, not ported.** Byte-identical to the old repo. Every other surviving
   contract was at least touched; ticket 11's skeleton took `iron_laws.md` across at ticket 09's
   verdict without a rewrite pass, which is why it is the only contract still describing the
   pre-08 pipeline in *prose* rather than just in stray paths.
2. **`iron_laws.md` is not the worst path offender, or even close.** Contracts in `MP` carrying
   pre-0007 tokens (`experience/`, `discovery/`, `blueprint/{datamodel,techstack,architecture}`,
   `_implementation/`, `mockup-walkthrough/`, `_concept/_feedback`, `_concept/_meta`):
   `walkthrough_renderer.md` 26 · `feedback_loop.md` 19 · `artifact_frontmatter.md` 16 ·
   `acceptance_criteria.md` 12 · `elements_block.md` 9 · **`iron_laws.md` 5** ·
   `concept_structure.md` 4 (all legitimate) · `domain_model.md` 2 · `seed_data.md` 1 ·
   `agent_patterns.md` 1. Killing this one file does not close the class ticket 19 handed to 16.
3. **Ticket 09's kept-because-machine-enforced argument fails on a wider front than the ticket
   states.** It is not that the prose lags the frontmatter; it is that **no `MP` skill's frontmatter
   gates are visible to the only reader** (§B). Fixing the nesting and the `_concept/` prefix would
   make all eight skills' gates live at once — including `mockup-storybook`'s hard gate on
   `discovery/brand/tokens.json`, a path ADR 0007 abolished, which would then **block that skill on
   a file nothing writes**. Ticket 14 fixed exactly this class of bug once already (a hard gate on
   `design/tokens.json` that could never pass); the repair moved the path but the tree moved again.
4. **`gate` on `artifacts.requires[]` is decoration in both repos.** `requires-graph.ts:236-249`
   reads `id` only. Five of `spec-feature`'s ten gate declarations (`:7-11`) are in a block whose
   `gate` key no code has ever read.
5. **The `FC` surface that would show a soft gate to a human is dead.** `requirements.get.ts` has
   no callers; the panel labelled "Hard gates" (`GateInfo.vue:37-43`) is fed by flow edges. So even
   with correct frontmatter, a soft gate today has **no rendering anywhere** — `soft` means
   "recorded in a report object nobody fetches".
6. **Laws 7 and 9 are not candidates for a move — they are already in `agent_patterns.md`**
   (`:8-20` and `:48-68`), and `iron_laws.md:80` already forwards law 9 there for its examples. The
   two files carry the same rule at two levels of detail; the question a move settles is which copy
   dies, not where the rule goes. Law 8 is the only one of the three with no `agent_patterns` home
   (`:135` covers input values, not files).
7. **The three laws with readers are the three with no `prerequisites` counterpart, and the six with
   no readers are the six the frontmatter can express.** Ticket 09 kept the file because its gates
   are machine-enforced; §D shows the machine-shaped half is precisely the half nobody ever cited,
   and the cited half is the half no `gate:` field can hold.
8. **`_shared.ts:36,43` means the zod schema will validate a `gate` value it never enforces** —
   `ArtifactRefSchema` and `FilePrerequisiteSchema` both declare `gate: z.enum(["hard","soft"]).optional()`.
   A wrong gate value fails validation; a correct one changes nothing at reader 3.

## Open questions for the human

1. **Is the crux the laws, or the nesting?** Ticket 19 demoted two gates and the contract disagreed —
   but the demotion was unobservable, because `MP` writes `prerequisites:` where the resolver does
   not look and without the `_concept/` prefix the validator joins. Does 22 rule on the laws against
   gates that do not run, or does the nesting fix land first and change what "demoted to soft" costs?
2. **Ticket 09's bar, applied to the destination.** `agent_patterns.md` has 0 in-body readers in `MP`,
   same as `iron_laws.md`; the "9 readers" is the old repo's number. Moving laws 7-9 there moves them
   into a file that fails the same test, and that already contains 7 and 9.
3. **Who owns the nesting/prefix repair?** It affects all eight shipped skills and the template
   (`docs/skill-template.md:13-17`) that told them to do it. Ticket 16 owns paths-resolve-to-real-entries
   and the validators; this is a *frontmatter shape* bug in the same class but on a different axis.
4. **If laws 3 and 4 go, what states the rule they encoded?** `spec-feature:66-70` already says a screen
   carries `elements:` and traces to its feature — but nothing in `MP` says a screen spec written before
   the data model exists has to be revisited when it does. The per-feature loop has no return edge to
   `07_screens/`.
5. **Law 5 is the one that clearly survives** (two hard gates, `min_entries: 1`, right subject, wrong
   skill name). Is a nine-law document worth keeping for one law that a two-word edit fixes, plus law 1,
   which `spec-feature:15` already enforces on the correct 0007 path?
6. **Both tables restate rules that now live at their steps** (`:98`/`:115` vs `build-implement:35-39`;
   `:97`/`:116` vs `agent_patterns:48-68`). ADR 0003's rule is one rule at one reader. Does the
   Rationalization Defense survive as a genre, or is it the pre-ADR-0003 form of the same content?
