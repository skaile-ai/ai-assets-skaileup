# The machine-layer public API of `ai-assets-skaileup`

Research for ticket `.scratch/skaileup-mp/issues/01-machine-layer-public-api.md`.
Question: **what can `-mp` rename/restructure freely, and what is a contract with a live consumer?**

Every claim below is cited `path:line` against the consuming code (or against a live run of it).
Absolute paths are abbreviated:

| alias | path |
|---|---|
| `FC/` | `/Users/matthias/devBench/SKAILEdev/forge/forge-concept/` |
| `WS/` | `/Users/matthias/devBench/SKAILEdev/workspaces/packages/workspaces/` |
| `SK/` | `/Users/matthias/devBench/SKAILEdev/ai-assets/ai-assets-skaileup/` |

Runtime under test: `@skaile/workspaces@0.48.1`, the version forge-concept actually resolves
(`FC/node_modules/@skaile/workspaces/package.json:3`). Where the workspaces **dev tree** has
moved on, that is flagged explicitly.

---

## 0. Executive summary

The public API is **much smaller than the repo suggests**. Three things are load-bearing:

1. **Skill identity = the `name:` field in SKILL.md frontmatter.** Nothing else. Directory
   paths are free — verified: **95 of 95** skills already have `name:` ≠ parent directory name.
2. **Flow identity = the `<id>.flow.yaml` filename stem**, and the flow YAML's node graph
   (`id`, `type`, `data.skill`, `data.flow`, `data.routes`, `parentNode`, `edges`) plus its
   top-level `requires:` install manifest.
3. **The `_concept/` / `_implementation/` on-disk tree**, which forge-concept partly hardcodes
   (`experience/features/`, `_implementation/trace.yaml`, `_concept/_grounding/<skill>/input.json`).

Two things widely assumed to be contracts are **not**:

- **`SK/skaile.yaml`'s `assets:` block is dead.** Discovery falls back to glob mode; the block is
  never read (§3.1). Live proof: it declares `impl-slice-finish` while the SKILL.md says
  `impl-slice-git-finish` — and discovery yields the latter.
- **`contracts/artifacts.yaml` is read only in `--link` (dev) installs.** In the default copy
  install it is unreachable from `.skaile/flows/`, so forge-concept silently falls back to
  session-driven node completion (§1.3).

---

## 1. `contracts/artifacts.yaml` — fields actually READ

### 1.1 The parser

`FC/server/utils/artifact-contract.ts:38-43` declares the entire shape it will look at:

```ts
interface RawArtifact {
  path?: string;
  kind?: string;
  side?: string;
  produced_by?: string | string[];
}
```

and `FC/server/utils/artifact-contract.ts:151-175` is the only place the YAML is walked:
`doc.artifacts` (`:151`) → for each `[id, raw]` (`:152`) it **requires** `raw.path` and
`raw.produced_by` (`:153`, entries missing either are skipped), normalises `produced_by` to an
array (`:154`), takes `producedBy[0]` as *the canonical producer* (`:155`), and stores
`{id, path, kind, side, producedBy}` (`:158-164`).

| field | read? | where / how |
|---|---|---|
| the map key (`<id>`) | **read** — carried as `ArtifactEntry.id` (`artifact-contract.ts:152`, `:159`) but never compared to anything | — |
| `path` | **READ — required** | `:153` (gate), `:160`, resolved at `:183-191` |
| `produced_by` | **READ — required**; first entry is canonical | `:153-155`, `:165-174` |
| `kind` | **READ** — only the literal `durable` matters | `:162`, `:269` (`e.kind == null \|\| e.kind === "durable"`) |
| `side` | **parsed, never read** — stored at `:161`, no consumer | dead |
| `description` | **not parsed at all** — absent from `RawArtifact` | dead |
| top-level `version: 1` | **not parsed** | dead |

### 1.2 Path semantics that ARE a contract

`FC/server/utils/artifact-contract.ts:183-191` and `:205-212`:

- a trailing `/` means "directory artifact" (`:194-196`) → completion counts files instead of
  `existsSync` (`:215-220`);
- a `{` anywhere (e.g. `{slice_id}`) makes the path **unresolvable** and it is dropped (`:184`, `:206`);
- the literal prefix `_concept/` is stripped and re-rooted at `getConceptDir()` (`:187-189`);
  anything else resolves against the project root (`:190`);
- `conceptRelativeFolder()` additionally strips a trailing `.md` (`:210`) so the value matches the
  extension-less entries of the `/api/concepts` listing.

`isNodeFileComplete()` (`:266-274`) is the whole point: a node is complete when **every** concrete,
non-templated, `durable`-or-untyped artifact of its canonical producer exists.
`kind: scratch` and `kind: code` are deliberately excluded from the mandatory set (`:269`).

`resolveNodeFolders()` (`FC/server/utils/flow-manager.ts:353-395`) adds one more implicit rule:
for a **directory artifact with several `produced_by` entries**, the subfolder whose name the
skill name *ends with* is attributed to that skill (`:378-390`, matcher at `:416-422`,
dash/underscore-insensitive). That is how `mockup-walkthrough-static-html` claims
`mockup-walkthrough/static-html/`. **Renaming a renderer skill without renaming its output
subfolder (or vice-versa) breaks this silently.**

### 1.3 …but it usually isn't loaded at all

`buildArtifactIndexes()` only searches `getInstalledFlowsDirs()`
(`artifact-contract.ts:138`), i.e. `{root}/.skaile/flows` (`FC/server/utils/project.ts:133-140`),
for a file named `artifacts.yaml` whose **parent directory is named exactly `contracts`**
(`artifact-contract.ts:66`), max depth 8 (`:58`), following symlinks (`:74-80`).

The default install **copies**, it does not symlink: `AssetManager.install()` defaults
`link` to false (`WS/asset-manager/src/index.ts:1310`, `:851-853`) and
`WS/asset-manager/src/installer.ts:183-190` only symlinks on `opts.link === true`.

Observed on disk (a real deploy, `/Users/matthias/devBench/SKAILEdev/.skaile/flows/`):

```
.skaile/flows/appbuilder-standard/appbuilder-standard.flow.yaml
.skaile/flows/appbuilder-standard/appbuilder-standard.md
```

— plain files, no symlink, no `contracts/` anywhere. Meanwhile the contract *is* deployed, but to
`.claude/contracts/shared-contracts/artifacts.yaml`
(`WS/core/src/driver-targets.ts:53-67`, `contract: ".claude/contracts"`), a directory
`artifact-contract.ts` never searches.

**Consequence:** in a normal `skaile install`, `getCanonicalArtifactsBySkill()` returns an empty
map (`artifact-contract.ts:142`), `isNodeFileComplete()` is always `false` (`:268`), and
forge-concept falls back to session-tracked completion (`flow-manager.ts:456-467`). The artifact
contract is a **dev-mode (`--link`) enhancement**, not a hard runtime dependency.

### 1.4 Second consumer

The only other reader is the collection's own validator,
`SK/skaileup/contracts/scripts/verify_artifacts.py:42`
(`REGISTRY = REPO / "skaileup" / "contracts" / "artifacts.yaml"`) — internal, and the map already
plans to retire it. Nothing in `platform/` reads it (grep across the super-repo returns only
forge-concept + this script).

---

## 2. The flow-YAML schema that is actually parsed

### 2.1 Load + acceptance

`WS/factory-assets/connectors/flow/engine/loader.ts`:

- `loadFlow()` (`:19-26`): `.yaml`/`.yml` → `yaml.parse`, else `JSON.parse`. No validation.
- `loadFlowsFromDir()` (`:41-63`): files ending `.flow.yaml` / `.flow.json` / `.json` (`:46`);
  **files starting with `_` are skipped** (`:45`); a flow is kept **only if `def.id && def.nodes
  && def.edges` are all truthy** (`:54`). Anything else is dropped silently.

So the *minimum viable flow* is `{ id, nodes, edges }`. `name`, `version`, `description`, `meta`
are optional to the loader (though `FlowManifestSchema` marks `id` and `name` required for the
asset validator — `WS/factory-assets/connectors/flow/engine/flow-manifest.ts:57-60`).

forge-concept adds a **directory/filename contract** on top:
`findFlowFile()` looks for `${flowId}.flow.yaml` under `.skaile/flows/${flowId}/`
(`FC/server/utils/flow-manager.ts:173`, `:213`) and then only adopts the parsed flow whose
`flow.id === entry.name` (`:220`). **The deploy dir name, the file stem, and `id:` must all be the
same string.**

The installer reinforces it: `copyFromManifest()` copies the *whole parent directory* when
`basename(parentDir) === basename(dest)` (`WS/asset-manager/src/installer.ts:61-62`) — which is
why `appbuilder-standard.md` rides along. Move a flow out of a same-named folder and its sibling
docs stop shipping.

### 2.2 Node kinds

Canonical type union — `WS/factory-assets/connectors/flow/engine/types.ts:81`:
`"skill" | "group" | "sub-flow" | "router"`. The doc block at `:44-71` states plainly that
**the engine tracks only `skill` nodes**; `group`, `sub-flow` and `router` are excluded from
`computeFlowState` / `computeSkippable` / `NodeState` (`:60-66`, and `FlowState.nodes` at `:372`).

forge-concept therefore re-implements the missing two:
`FC/shared/flow-extended.ts:17` widens the union locally, and
`FC/server/utils/flow-extended-state.ts:34-74` synthesises their state.

| kind | fields the code reads |
|---|---|
| `skill` | `id`, `type`, `parentNode`, `data.skill`, `data.label`, `data.optional`, `data.approval.mandatory`, `data.phase`, `data.parallel_group`, `data.writes`, `data.overrides.skip_checks` |
| `group` | `id`, `type`, `data.label`, `data.phase`; children found via other nodes' `parentNode` |
| `sub-flow` | `id`, `type`, `parentNode`, `data.flow` (fallback `data.parameters.flow`), `data.label`, `data.optional`, `data.phase` |
| `router` | `id`, `type`, `parentNode`, `data.routes[].condition`, `data.routes[].target` (nullable), `data.label`, `data.phase` |

Citations:

- `data.skill` → `FC/server/utils/flow-manager.ts:367`, `:465`; `FC/server/api/flows/nodes/[nodeId]/run.post.ts:53`; `FC/server/api/flows/nodes/[nodeId]/requirements.get.ts:36`; `WS/factory-assets/connectors/flow/engine/types.ts:91` (`data.skill ?? node.id` fallback — documented at `:68-69`, implemented as the `skillId` fallback in both endpoints).
- `data.label` → `FC/server/utils/flow-extended-state.ts:64`; `FC/server/utils/flow-manager.ts:489`; orchestrator prompt `WS/factory-assets/connectors/flow/prompt-fragments.ts:122`.
- `data.optional` → `FC/server/utils/flow-extended-state.ts:66`, `:87`; `prompt-fragments.ts:118`, `:137`.
- `data.approval.mandatory` → `prompt-fragments.ts:122` (gate column); schema-enforced mutual exclusion with `optional` at `flow-manifest.ts:42-46`.
- `data.phase` → `FC/server/utils/flow-manager.ts:490`, `:537`, `:555`; **value enum is hardcoded** at `FC/shared/flow-phases.ts:8-10`: `conceptualization | implementation | review`. An unrecognised value falls back to a name-prefix heuristic (`:20-29`).
- `data.parallel_group` → `FC/server/utils/flow-manager.ts:533` (surfaced to UI only; the engine ignores it — `types.ts:114-119`).
- `data.writes` → `FC/server/utils/flow-manager.ts:361`, `:508`. **Legacy**: skaileup flows omit it and rely on the artifact contract instead (`:511-516`).
- `data.overrides.skip_checks` → `FC/server/api/flows/nodes/[nodeId]/requirements.get.ts:52` → `WS/resolver/src/validator.ts:74`, `:81-84`.
- `parentNode` → `FC/server/utils/flow-manager.ts:494`, `:534`, `:554`.
- `position` / `style` → **never read by any engine or server code** (`types.ts:84-87`: "not used by the engine"); only the canvas renderer.

### 2.3 `data.skill` resolution — the chain

```
flow node .data.skill  (else node.id)
   → resolveSkillContent(skillId)         FC/server/api/flows/nodes/[nodeId]/run.post.ts:53-54
   → {root}/.claude/skills/{skillId}/SKILL.md   FC/server/utils/skill-content.ts:17-27
   → prompt: `Run skill ${skillId}\n\n<full SKILL.md text>`   run.post.ts:78-80
```

In parallel, `data.skill` is the key into the artifact contract:
`isNodeFileComplete(n.data?.skill)` (`FC/server/utils/flow-manager.ts:465`) →
`getArtifactsForSkill()` (`artifact-contract.ts:232-235`) → `produced_by[0]` match.

And it is the key into the dependency graph:
`WS/factory-assets/connectors/flow/engine/flow-kind-provider.ts:63-66` emits a `requires` edge
`nodes[].data.skill`; ditto `data.flow` at `:68-71`. Mirrored in
`WS/discovery/src/requires-graph.ts:180-201`.

**So `data.skill` is simultaneously (a) a directory name under `.claude/skills/`, (b) a
`produced_by` value in `artifacts.yaml`, and (c) a dependency-graph node id. All three must agree.**

### 2.4 Router semantics

`FC/shared/flow-extended.ts:57-64` keeps a route only when `typeof r.condition === "string"`;
`target` defaults to `null`. `null` means "skip this branch"
(`FC/server/utils/flow-route-choice.ts:39-51`). The `condition` string is **never evaluated by any
code** — `types.ts:132-138` says explicitly the package "does not itself parse or evaluate
`condition`". In forge-concept a human picks the route and the unchosen branches are marked
skipped (`flow-route-choice.ts:27-62`). So route condition strings (`stack.astro_available`,
`default`) are **prose for the operator/LLM, not an expression language**.

### 2.5 `parameters`, `globals`, `modes`, top-level `requires`

- `data.parameters` — read in exactly **one** place: the sub-flow child-id fallback
  `n.data?.parameters?.flow` (`FC/server/utils/flow-manager.ts:475`;
  `FC/shared/flow-extended.ts:52-53`). Every skaileup flow writes `parameters: {}`. Otherwise it
  is forwarded verbatim to the runner and never inspected (`types.ts:110-111`).
- `globals` — surfaced to the agent as a whole object by the `get_globals` tool
  (`WS/factory-assets/connectors/flow/adapter.ts:675-676`). No individual key is branched on.
- `modes`, `tier_presets`, `artifact_handoff`, `next_flows` — `next_flows` is plumbed into the
  catalog (`FC/server/utils/flow-manager.ts:53`, `:308`) but **no shipped flow declares any of the
  four** (grep over `SK/skaileup/flows/**/*.yaml` returns zero hits). Documentation-only today.
- **Top-level `requires:` — a REAL contract.** `WS/core/src/walker.ts:511-529` (`manifestDeps`)
  reads a flow's `requires:` and feeds it into `ProvenanceCandidate.deps` (`:257`, `:449`), which
  `resolveAll()` expands transitively (`WS/core/src/repo-manager.ts:865-871`). The comment at
  `walker.ts:513-514` is unambiguous: *"Without this, installing a flow deploys only the
  `.flow.yaml` and never the contracts/skills/sub-flows it declares."* The refs are parsed by
  `bundleDepRefs` (`WS/core/src/manifest.ts:427-448`) in the form `kind:@publisher/name`, so
  **the publisher `@skaile-ai` is baked into every flow YAML.** This is what makes the
  forge-concept test's `expect(result.missing).toEqual([])` pass while declaring only 6 flows.

### 2.6 The collection's own `flow.schema.json` overshoots the parsers

`SK/skaileup/contracts/flow.schema.json` defines much that nothing reads:
`gate-node` (`:105`, in the `oneOf` but absent from the runtime union at `types.ts:81`),
edge `type: "review-loop"` + `max_iterations` + `exit_condition` (`:280-292` — `EdgeType` is only
`flow|parallel|optional`, `types.ts:42`), `data.subagent`, `data.requires`, `data.grounding_folder`,
`data.user_inputs`, `data.feedback`, `sourceHandle`/`targetHandle`/`animated`/`label` on edges,
and the `next_flows[].domain` enum. All safe to drop.

---

## 3. How a skill is addressed, end to end

### 3.1 Discovery: `name:` frontmatter wins; directory path is irrelevant

`WS/discovery/src/discover.ts:725-764` (`deriveName`):

```ts
if (typeof manifest.name === "string" && manifest.name.length > 0 && isValidAssetName(manifest.name))
  return manifest.name;                       // :732-738
...
if (kind === "flow") return filename.replace(/\.flow\.(yaml|json)$/, "");   // :743-746
...
if (parts.length >= 2) return parts[parts.length - 2]!;   // parent dir  :757-759
```

`isValidAssetName` = `/^[a-z0-9]+(?:-[a-z0-9]+)*$/` (`WS/core/src/models.ts:288`, `:307-309`).

**Verified by running the real discovery** (`@skaile/workspaces@0.48.1`,
`discoverAssetsInTree("<SK>")`):

- 105 assets found, 0 errors — 95 `skill`, 6 `contract`, 3 `agent`.
- **95 / 95 skills have `name:` ≠ parent directory name** (`concept-brief` lives in `01_brief/`,
  `impl-quality-test-e2e` in `13_impl-quality/06_test-e2e/`, …). The numbered directory scheme is
  pure authoring convenience and carries **zero** identity.
- `readManifestSourceConfig(SK)` → `undefined` (no `skaile.manifest.yaml`), so discovery runs in
  **glob mode** (`WS/discovery/src/source-config.ts:314-316`: manifest mode requires
  `version === 2 && Array.isArray(assets)`, produced only by `manifestToSourceConfig` at `:453-475`
  from a `skaile.manifest.yaml`).
- **`SK/skaile.yaml`'s `assets:` block is therefore never read.** Independent proof from the same
  run: `skaile.yaml` declares `skill: impl-slice-finish` (root `skaileup/12_impl-slice/08_finish`)
  but discovery yields `impl-slice-git-finish` from `08_git-finish/SKILL.md` — the frontmatter
  wins and the declared name does not exist. Six assets exist on disk that `skaile.yaml` never
  declares (`ops-trace`, `impl-quality-review-feature`, `impl-slice-git-finish`, and three
  `agent.yaml`s) and are discovered anyway.
- The collection's own convention (`SK/CLAUDE.md` § Naming Convention) *derives* `name:` from the
  path by stripping `NN_` / `NN_<letter>_` prefixes — but **no consumer enforces or re-derives
  it**. The one place that compares them, `WS/core/src/conformance.ts:55-61`, emits a
  `warn` ("name does not match parent directory") — which today fires for all 95 skills and is
  never escalated. The mapping is a repo-internal discipline, not an external contract.
- Publisher: derived from the git remote org via `resolveSourcePublisher`
  (`WS/library/src/local/local-catalog-source.ts:296-314`) → `skaile-ai`, matching the
  `@skaile-ai/...` refs in the flow `requires:` blocks. In a bare `discoverAssetsInTree` with no
  source config it degrades to the first path segment (`@skaileup`, `source-config.ts:377-381`).

> **Migration hazard for `-mp`.** The workspaces **dev tree** hard-rejects `publisher:`/`version:`/
> `assets:` in `skaile.yaml` (`WS/core/src/workspace-config.ts:1596-1605`) and expects the
> publication half in `skaile.manifest.yaml` (`WS/core/src/publish-manifest.ts:8-15`, `:148`).
> `-mp` should ship `skaile.manifest.yaml` (or nothing) and rely on glob mode + frontmatter names.

### 3.2 Deploy

`WS/asset-manager/src/installer.ts:173`:

```ts
const dest = deployedDir(entry.kind, entry.name, driverTarget, globalInstall, cwd);
```

`deployedDir` = `<base>/<name>` (`WS/core/src/store.ts:57-65`), base from
`DRIVER_TARGETS` (`WS/core/src/driver-targets.ts:53-67`): for `claude-code`
`skill → .claude/skills`, `flow → .skaile/flows`, `contract → .claude/contracts`,
`agent → .claude/agents`, `prompt → .claude/commands`.

`WS/asset-manager/src/index.ts:1921` builds the `deployed` list as `` `${kind}:${name}` `` —
exactly the strings the forge-concept test asserts.

So: **`.claude/skills/<frontmatter name>/SKILL.md`**.

### 3.3 Read back

- `FC/server/utils/skill-content.ts:17-31` — `join(dir, skillId, "SKILL.md")`, project root then
  app root then `.omp/skills/`.
- `FC/server/utils/skill-docs.ts:35`, `:47` — walks `.claude/skills/`, and comments
  `name: entry, // directory name is the canonical skill ID`.
- `WS/core/src/workspace-config.ts:2363-2436` (`stageMaterializedSkills`) — stages
  `.skaile/assets/skill/<name>/` into `<skillsDir>/<name>/`, gated on a declared-name set with
  publisher-scope tolerance (`:2388-2397`).

### 3.4 The name is also a path segment in `_concept/`

`WS/resolver/src/validator.ts:107`:

```ts
const inputFile = path.join(projectDir, "_concept", "_grounding", skillId, "input.json");
```

Renaming a skill renames its grounding folder. Same in
`FC/server/utils/concept-agent.ts:379-400` (`enrichSkillPrompt` → `getStepGroundingFolder`).

---

## 4. SKILL.md `metadata:` — read vs. documentation-only

Schema (permissive, `z.looseObject`): `WS/types/src/manifests/skill.ts:11-72`. Passing validation
proves nothing about being *read*. Actual readers:

| frontmatter field | READ by | verdict |
|---|---|---|
| `name` (top level) | `WS/discovery/src/discover.ts:732-738`; conformance dir-name check `WS/core/src/conformance.ts:55-61` | **CONTRACT** — the identity |
| `description` (top level) | `WS/core/src/walker.ts:338`, `:343` (store listing); `FC/server/utils/skill-docs.ts:48`; Claude Code's own skill loader | **CONTRACT** — max 1024 chars enforced as an *error* (`conformance.ts:64-71`) |
| `metadata.version` | `WS/discovery/src/discover.ts:712-723` (`coerceVersion`, falls back to `"0.1.0"`); `WS/core/src/manifest.ts:83-88` (`extractVersion`); version pinning `WS/resolver/src/version.ts:53` via `run-flow.ts:563` | **READ** |
| `metadata.artifacts.requires[].id` | `WS/discovery/src/requires-graph.ts:231-250` — emits graph edges | **READ** (edges only; ids are *not* resolved against `artifacts.yaml` by any TS code) |
| `metadata.artifacts.produces[]` / `consumes[]` | validated by Zod (`skill.ts:16-17`) — **no reader** | doc-only (+ `verify_artifacts.py`) |
| `metadata.prerequisites.files[]` (`path`, `gate`, `min_entries`, `description`) | `WS/resolver/src/parser.ts:69-74` → `WS/resolver/src/validator.ts:80-104`; surfaced at `FC/server/api/flows/nodes/[nodeId]/requirements.get.ts:50-54` | **READ — hard/soft gates** |
| `metadata.prerequisites.inputs_required` / `inputs_optional` | `parser.ts:75-76`, `:144-156`; checked against `input.json` at `validator.ts:117-127` | **READ** |
| `metadata.prerequisites.reads[]` | `parser.ts:77-80`; `validator.ts:130-137` (informational) | **READ (advisory)** |
| `metadata.prerequisites.produces[]` / `resources[]` / `connectors[]` | `parser.ts:81-91`, `:158-168` | **READ** (resources/connectors only matter with a ResourceManager) |
| `metadata.user_inputs.dialog[]` | legacy path `parser.ts:96-106` | **READ (legacy)** |
| `metadata.requires` | `WS/core/src/manifest.ts:101-111` (`parseRequires`, root **or** `metadata.`) | **READ** — not used by skaileup skills today |
| `keywords`, `category`, `license`, `homepage` (top level) | `WS/core/src/walker.ts:332-347` — store listing | READ (cosmetic) |
| `allowed-tools` | conformance WARN only if not a string (`conformance.ts:97-104`) | advisory |
| `metadata.tags` | **no reader** (only `keywords` at top level is read, `walker.ts:339`) | **doc-only** — and it triggers the non-string portability WARN at `conformance.ts:84-95` |
| `metadata.stage` | **no reader** | doc-only |
| `metadata.source` (`'MERGED'` etc.) | **no reader** | doc-only |
| `metadata.parameters` | validated (`skill.ts:12`), **no reader** | doc-only |
| `## Compaction Directives` body section | `WS/resolver/src/parser.ts:124-142` | READ (if a host calls it) |

Note `conformance.ts:82-95`: the agentskills.io standard wants `metadata` to be a flat
string→string map; skaile's nested objects are reported as **warnings, never errors, never
rewritten**. So nesting is tolerated but each nested key costs a warning.

---

## 5. Literal hardcoded compatibility surface

### 5.1 Flow and skill names in tests

`FC/tests/integration/skaileup-flows.test.ts`:

- `:22` — repo URL `git@github.com:skaile-ai/ai-assets-skaileup.git` (override: `SKAILEUP_ASSETS_REPO`).
- `:23` — publisher `skaile-ai`.
- `:29-36` — **flow names**: `appbuilder-mvp`, `appbuilder-simple`, `appbuilder-standard`,
  `appbuilder-complex`, `skaileup-slice-concept`, `skaileup-slice-impl`.
- `:38` — **skill names**: `concept-brief`, `concept-goals`.
- `:68-69` — dependency ref grammar `flow:@skaile-ai/<name>` / `skill:@skaile-ai/<name>`.
- `:92-93` — deployed-ref strings `flow:<name>` / `skill:<name>`.
- `:96-99` — deploy paths `.skaile/flows/<flow>` and `.claude/skills/`.
- `:114-117` — parsed flow must have `id === <name>`, non-empty `nodes`, array `edges`.

`FC/tests/integration/framework-contract.test.ts` is **not** a skaileup contract — it pins the
`@skaile/workspaces/sdk/flow` export surface (`:14-19`) and forge-concept's own event shapes.
Nothing in it references the collection.

### 5.2 Hardcoded strings in production code

| literal | location | note |
|---|---|---|
| `"conceptualization" \| "implementation" \| "review"` | `FC/shared/flow-phases.ts:8-10` | the `data.phase` enum |
| skill-name prefixes `concept- design- experience- product-spec- mockup-` | `FC/shared/flow-phases.ts:18` | phase inference fallback |
| `quality`, `ops-eval`, `ops-review`, `ops-sync`, `impl-` | `FC/shared/flow-phases.ts:23-26` | phase inference fallback — **couples the domain-prefix naming scheme to the UI** |
| domain ids `skaileup-conceptualization` / `skaileup-implementation` / `skaileup-evaluate` | `FC/server/utils/flow-manager.ts:147-150`; `FC/server/api/settings.get.ts:30-31`; `FC/server/api/domains.get.ts:10` | synthetic, derived from `meta.category` |
| `meta.category === "implementation" \| "evaluation" \| "quality"` | `FC/server/utils/flow-manager.ts:147-148` | **dead branches**: shipped categories are only `cli, concept, full-stack, incremental, maintenance, prototype`, so every flow falls through to `skaileup-conceptualization` (`:150`) |
| `_concept/` prefix | `FC/server/utils/artifact-contract.ts:187`, `:208`; `FC/server/utils/project.ts:112` | |
| `_concept/experience/features/` | `FC/server/utils/review-coverage.ts:100` | matches `SK/skaileup/contracts/artifacts.yaml:158` — **duplicated, not derived** |
| `_implementation/trace.yaml`, `_implementation/acceptance_criteria/**/*.ac.md`, `_implementation/review/<feature>.yaml` | `FC/server/utils/review-coverage.ts:109`, `:122-123`, `:131` | review dashboard; frontmatter keys `feature`, `verdict`, `specced/sliced/committed/evaluated/documented/code_refs` (`:167-174`) |
| `_concept/_grounding/<skillId>/input.json` | `WS/resolver/src/validator.ts:107` | |
| `_grounding`, `_research`, `_standards` (hidden dirs) | `FC/server/utils/grounding.ts:15` | |
| `impl_status: implemented \| tested` | `FC/server/utils/concept-status.ts:138-139` | markdown frontmatter in `_concept/` outputs |
| `artifacts.yaml` under a dir named `contracts` | `FC/server/utils/artifact-contract.ts:66` | |
| `${flowId}.flow.yaml` inside `.skaile/flows/${flowId}/` | `FC/server/utils/flow-manager.ts:173`, `:213`, `:220` | |
| `SKILL.md` filename | `WS/discovery/src/builtin-providers.ts:205-212`; `WS/core/src/workspace-config.ts:2400-2407` | |
| `CONTRACT.md` filename for `kind: contract` | `WS/discovery/src/discover-manifest.ts:256-265` | |
| companion dirs (`references/`, `scripts/`, …) + same-dir `validator.py`, `CLI.md` | `WS/discovery/src/builtin-providers.ts:86-115` | defines what ships inside a skill tarball |

---

## 6. Verdict

### FREE TO RENAME / RESTRUCTURE

| thing | why it's free |
|---|---|
| **Every directory path inside the repo** (`skaileup/NN_domain/NN_step/`) | Identity comes from `name:`, not the path (`discover.ts:732-738`). Live proof: all 95 skills already diverge. Only *relative* structure inside one skill dir matters (companion dirs, `builtin-providers.ts:86-115`). |
| **The number of domains, the `NN_` prefixes, domain grouping** | Nothing reads them. `_domain` in forge-concept is synthesised from flow `meta.category`, not from paths (`flow-manager.ts:145-151`). |
| **`SK/skaile.yaml`'s `assets:` block** | Never read (§3.1); already drifted from reality. `-mp` should not reproduce it. |
| **`artifacts.yaml` `side:` and `description:`** | Parsed-and-ignored / not parsed (`artifact-contract.ts:38-43`, `:161`). |
| **`metadata.tags`, `metadata.stage`, `metadata.source`, `metadata.parameters`, `metadata.artifacts.produces/consumes`** | No reader anywhere (§4). |
| **Flow `meta.category` values** | All fall through the same default (`flow-manager.ts:150`). |
| **`modes:`, `tier_presets:`, `artifact_handoff:`, `next_flows:` in flow YAMLs** | No shipped flow uses them. |
| **`data.parameters`, `data.writes`, node `position`/`style`** | `parameters` only for the sub-flow `flow` fallback (`flow-manager.ts:475`); `writes` is legacy; geometry is canvas-only (`types.ts:84-87`). |
| **Router `condition` strings** | Never evaluated (`types.ts:132-138`). |
| **`flow.schema.json` extras** — gate nodes, `review-loop` edges, `data.user_inputs`/`feedback`/`grounding_folder`/`requires`/`subagent` | Not in any parser (§2.6). |
| **The DSL grammar, `skill_grammar.md`, most of `contracts/`** | No TS consumer; only the repo's own Python validators. |
| **`docs/` Starlight site** | Nothing outside the repo reads it. |

### CONTRACT — and who owns it

| contract | owner / consumer | evidence |
|---|---|---|
| **SKILL.md `name:`** is the skill's only identity — kebab-case `/^[a-z0-9]+(?:-[a-z0-9]+)*$/` | `@skaile/workspaces` discovery → deploy dir `.claude/skills/<name>/`; forge-concept skill resolution; Claude Code's native skill loader | `discover.ts:732-738`; `models.ts:288`; `installer.ts:173`; `store.ts:57-65`; `skill-content.ts:22` |
| **SKILL.md `description:`** ≤ 1024 chars, present | store listing + agent skill selection | `conformance.ts:64-71`; `walker.ts:338` |
| **`<id>.flow.yaml` in a directory named `<id>`, with `id: <id>`** | forge-concept flow loading + the installer's whole-dir copy | `flow-manager.ts:173`, `:213`, `:220`; `installer.ts:61-62` |
| **A flow must have truthy `id`, `nodes`, `edges`** | flow engine loader | `loader.ts:54` |
| **Node kinds limited to `skill`/`group`/`sub-flow`/`router`** | flow engine + forge-concept | `types.ts:81`; `flow-extended.ts:17` |
| **`nodes[].data.skill` = an installed skill name** | forge-concept node run; artifact contract; requires graph | `run.post.ts:53-54`; `flow-manager.ts:465`; `flow-kind-provider.ts:63-66` |
| **`nodes[].data.flow` = another flow id** | sub-flow completion + transitive install | `flow-extended.ts:48-54`; `flow-manager.ts:475-478`; `flow-kind-provider.ts:68-71` |
| **`nodes[].data.routes[]` = `{condition: string, target: string\|null}`** | forge-concept router UI + branch pruning | `flow-extended.ts:57-64`; `flow-route-choice.ts:35-38` |
| **`data.phase` ∈ {conceptualization, implementation, review}** | forge-concept sidebar lanes | `flow-phases.ts:8-10`, `:31-33` |
| **Edge `type` ∈ {flow, parallel, optional}**; `flow` = hard dependency | flow engine + forge-concept synthesis | `types.ts:42`; `flow-extended-state.ts:47-49` |
| **Flow top-level `requires: [kind:@skaile-ai/name]`** — every node skill listed, publisher included | install resolution (`missing` would be non-empty otherwise) | `walker.ts:511-529`; `manifest.ts:427-448`; `repo-manager.ts:865-871`; `skaileup-flows.test.ts:91` |
| **`contracts/artifacts.yaml` entry shape: `<id>: {path, produced_by, kind}`**, `produced_by[0]` canonical, `_concept/` prefix, trailing `/` = dir, `{}` = templated | forge-concept file-derived node completion — **but only under `--link`** | `artifact-contract.ts:151-175`, `:183-196`, `:266-274`; link default `index.ts:1310` |
| **Renderer skill name must end with its output subfolder name** | forge-concept multi-producer folder attribution | `flow-manager.ts:378-390`, `:416-422` |
| **`_concept/experience/features/`, `_concept/experience/screens/`, …** the concept tree | forge-concept explorer + review dashboard (duplicated, not derived) | `review-coverage.ts:100`; `artifacts.yaml:152-190` |
| **`_implementation/{trace.yaml, acceptance_criteria/*.ac.md, review/*.yaml}`** and their keys | forge-concept `/review` page | `review-coverage.ts:109-141`, `:167-174` |
| **`_concept/_grounding/<skill-name>/input.json`** | resolver input gating | `validator.ts:107` |
| **`impl_status: pending\|implemented\|tested` frontmatter** | forge-concept node badges | `concept-status.ts:138-140` |
| **`metadata.prerequisites.*`** (files/inputs/reads/resources/connectors) | resolver gating, surfaced in forge-concept | `parser.ts:59-92`; `validator.ts:80-137`; `requirements.get.ts:50-54` |
| **`metadata.version`** | discovery version + flow node version pinning | `discover.ts:712-723`; `version.ts:53` |
| **The six flow ids + two skill names in the test** | `forge-concept` CI | `skaileup-flows.test.ts:29-38` |

### Ownership summary

- **`@skaile/workspaces`** owns: asset-name grammar, `name:`-over-path resolution, `.claude/skills/<name>` and `.skaile/flows/<id>` layout, flow-node type union, `requires:` transitive install, `metadata.prerequisites` parsing, `metadata.version`.
- **`forge-concept`** owns: `data.phase` enum, the phase/domain name-prefix heuristics, the artifacts.yaml reader and its `path`/`kind`/`produced_by` subset, the renderer-subfolder matching rule, `_implementation/` review artifacts, `impl_status`, and the hardcoded test names.
- **`ai-assets-skaileup` itself** owns everything else — and can move all of it.

### Two recommendations for `-mp`

1. **Ship `skaile.manifest.yaml`, not `assets:` in `skaile.yaml`.** The dev-tree workspaces throws
   on the latter (`workspace-config.ts:1596-1605`). Or ship neither and let glob mode work.
2. **Decide whether `artifacts.yaml` is worth keeping.** As deployed today it is unreachable
   (§1.3). Either move the reader to `.claude/contracts/` (a one-line change in
   `artifact-contract.ts:138`) or accept that node completion is session-driven and drop the file.

---

## Appendix: how the evidence was produced

Static reads of the files cited, plus one live run of the *installed* discovery against the
collection (`@skaile/workspaces@0.48.1`, `discoverAssetsInTree("<SK>")`, executed from
`FC/`, script deleted afterwards). Results quoted in §3.1: 105 assets / 0 errors;
`readManifestSourceConfig` → `undefined`; 95/95 name-vs-directory divergences; the
`impl-slice-finish` vs `impl-slice-git-finish` discrepancy; six undeclared-but-discovered assets.
Deployed-layout claims (§1.3, §3.2) were checked against the real
`/Users/matthias/devBench/SKAILEdev/.skaile/flows/`, `.claude/skills/` and `.claude/contracts/`
trees on this machine.
