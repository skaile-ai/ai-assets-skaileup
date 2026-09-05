# 29: The acceptance run — install `-mp` and get the flows loading green

**Type:** task
**Blocked by:** None — 28 resolved 2026-09-05
**Status:** resolved

## Question

Graduated from the map's "Opt-in mechanics and the acceptance test" fog patch, which ticket 10
made specifiable by fixing the flow list.

This is the map's destination: **one real project installs `-mp` and its flows load green.**

Decide and do:

- **Which project plays the role.** `forge-concept` is the natural candidate — it owns the
  integration test — but the map's parallel/opt-in premise says nothing cuts over, so the
  install must be additive.
- **Opt-in mechanics**: how a project points at `-mp` in `skaile.yaml` (`sources:` +
  `dependencies:`), and what lockfile state that produces.
- **Run it.** `WorkspaceService.install()` → deploy under `.skaile/flows` + `.claude/skills`
  → `loadFlowsFromDir` parses all four. Green means: four flows discovered and parsed, every
  `data.skill` resolving to a deployed skill directory.

Note the host cannot help here: **`validateFlow` / `FlowManifestSchema` have zero call sites**
in forge-concept, a `data.skill` resolving to nothing does **not** raise
(`run.post.ts:78-80` falls back to a generic prompt; `requirements.get.ts:37-48` returns a
fabricated `satisfied: true`). So "loads green" in the host is a weak signal by construction —
`scripts/check.py` (ticket 16) is the real gate, and this ticket should say so rather than
trusting a silent pass.

## Answer

**Green. `forge-concept` installs `-mp` from GitHub and loads all four flows, with every
node skill deployed** — `tests/integration/skaileup-flows.test.ts` 4/4, no skip, and the
loader reporting `[flows] Loaded 4 flows`. `check.py` is green over the collection
(29 skills · 4 flows · 0 errors) and `test_check.py` is 61/61 after this ticket added a rule.

### The project, and the opt-in mechanics

`forge-concept` plays the role — additively, as the map's parallel premise requires: the
suite builds a throwaway workspace, and `templates/dev/skaile.yaml` (the local dev
workspace) is the only standing pointer changed. Nothing in the old collection moved.

A workspace opts in with one `sources:` URL and an explicit dependency line per asset:

```yaml
sources:
  - url: git@github.com:skaile-ai/ai-assets-skaileup-mp.git
dependencies:
  - flow:@skaile-ai/appbuilder-mvp        # ×4 — a flow is the tier
  - skill:@skaile-ai/concept-brief        # ×29 — see "a flow is not self-contained"
```

That produces `skaile.lock.yaml` with one entry per ref at `#0.0.0-sha.<7>` (the synthetic
version for an untagged source), flows deployed under `.skaile/flows/<id>/` and skills under
`.claude/skills/<name>/`. **`skill:*` is not accepted here** — the wildcard is CLI sugar and
`parseAssetRef` throws on it inside `skaile.yaml`, so the 29 lines are written out.

### What blocked it: a flow's asset name is its `name:`, not its `id:`

The first run resolved **two of four** flows. `@skaile/workspaces` takes a flow's asset
identity from the manifest's **`name:`**, slugified — `core/manifest.ts`
`fromFlowYamlContent` (`name: String(meta.name ?? meta.id ?? stem)`) then `scanDirectory`'s
`add()` through `slugifyAssetName`. `id:` is never consulted. So:

| `id:` | `name:` | asset name the installer indexed | ref resolved? |
|---|---|---|---|
| `appbuilder-mvp` | `Appbuilder MVP` | `appbuilder-mvp` | yes — by accident of title case |
| `appbuilder-standard` | `Appbuilder Standard` | `appbuilder-standard` | yes |
| `skaileup-concept-only` | `Concept Only` | `concept-only` | **no** |
| `skaileup-concept-reverse` | `Reverse Engineer a Codebase` | `reverse-engineer-a-codebase` | **no** |

The old collection satisfied this by convention it never wrote down — every flow was titled
the Title Case of its id (`'SkaileUp Concept Only'`), so nobody had cause to learn the rule.
Ticket 28 wrote descriptive titles instead and the two flows silently vanished: `missing`
named them, but a project reading `deployed` sees a shorter list and no error.

**Fixed and gated** (`-mp` `dc8dfea`): both flows retitled — `Skaileup Concept Only`,
`Skaileup Concept Reverse` — and `check.py` now mirrors `slugifyAssetName` and fails any
flow whose `name:` does not slugify to its `id:`, with two tests (the negative case, and
`Appbuilder MVP`/`appbuilder-mvp` as the legal title-cased form). The rule is three-way, not
cosmetic: the install ref, the deployed directory, and the loader's `flow.id !== entry.name`
check (`flow-manager.ts:220`) all key on that one string.

The alternative — rename the ids to match the nicer titles — was rejected: `id` is the flow's
identity everywhere else (ticket 10 fixed the list, `profiles.get.ts` keys onboarding on it),
and a title is the cheaper thing to bend.

### A flow is not self-contained on install

The map has said since charting that a flow's top-level `requires:` provisions its skills and
contracts. **It does not, in the version the acceptance target runs.** In
`@skaile/workspaces` 0.48.1, `bundleDeps` (core walker) opens with
`if (kind !== "bundle") return undefined` — so a flow candidate carries `deps: 0` and
installing `flow:@skaile-ai/appbuilder-mvp` alone deploys the `.flow.yaml` and **nothing
else**, silently, with `missing: []`. Measured on both collections, so it is a version fact,
not something `-mp` did. The monorepo's `main` has already widened it (`manifestDeps`, flow
`requires` included) — unreleased into forge-concept.

Consequence, and the reason the acceptance bar is written the way ticket 29 wrote it: a node
whose skill never installed **still runs**, on a generic `Run skill <id>` prompt
(`run.post.ts:78-80`). So the suite now asserts the cover itself — for each of the four
flows the app parsed, every `node.data.skill` must be a directory under `.claude/skills/` —
and both the test workspace and `templates/dev/skaile.yaml` list all 29 skills explicitly.
Before this ticket the dev workspace declared four flows and no skills, i.e. a full picker
over an empty-bodied pipeline.

### The harness, as landed (working tree, uncommitted)

Both files in `forge/forge-concept`, on top of ticket 28's edits:

- `tests/integration/skaileup-flows.test.ts` — `SKILLS` widened from two spot-checks to all
  29 node skills (asserted deployed, one `existsSync` each), plus a third test walking the
  parsed flows for unresolved `data.skill`. Repo URL and `FLOWS` are ticket 28's.
- `templates/dev/skaile.yaml` — the same 29 skills added under the four flows.

### Also found (recorded, not fixed here)

- **A cached source clone is not refetched on install.** After `dc8dfea` was pushed, a
  *fresh* workspace still resolved the two flows as missing: `~/.skaile/cache/sources/
  github.com/skaile-ai/ai-assets-skaileup-mp` stayed at the old commit and the install
  reused it. A manual `git fetch && git reset --hard origin/main` in the cache fixed it.
  Anyone re-running this suite after pushing `-mp` needs to know.
- **The contracts layer is not installable at all** — `-mp` ships `contracts/*.md` as flat
  files with no manifest, so discovery finds **0 contract assets** and every flow's
  `contract:` refs name nothing. Inert only because of the `bundleDeps` gap above. Opened as
  [34: The contracts layer is not installable — 13 refs per flow name nothing](34-contracts-are-not-assets.md).
