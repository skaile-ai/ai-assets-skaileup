# `lab/compile-bundle` Design Spec

**Date:** 2026-05-10
**Task:** 3D of `docs/devlog/2026-05-07-skill-graph-migration.md`

---

## Goal

Build the `lab/compile-bundle` skill — a dev-tool that keeps `bundles/*.bundle.yaml` in sync with `flows/*.flow.yaml` by ensuring every skill a flow references is present in its corresponding bundle's `requires:` list.

---

## Concept

The skill catalog has two parallel representations of tier membership:

- **Flows** (`flows/*.flow.yaml`) — define how a tier runs (skill sequence, edges, conditionals). Source of truth for which skills a tier uses.
- **Bundles** (`bundles/*.bundle.yaml`) — dependency manifests for the skill installer. Declare which skills must be installed to run a tier.

These can drift: if a skill node is added to a flow, it must also appear in the bundle or the installer will not provision it. `lab/compile-bundle` closes this gap automatically.

---

## Files

```
lab/compile-bundle/
├── SKILL.md           ← agent prompt: run script, review diff, commit
├── compile_bundle.py  ← Python script (stdlib + PyYAML); does all computation
└── validator.py       ← read-only check: every flow skill is covered in its bundle
```

---

## `compile_bundle.py` — Algorithm

**Inputs:** `flows/*.flow.yaml`, `bundles/*.bundle.yaml`  
**Outputs:** patched `bundles/*.bundle.yaml` (additive only — never removes entries)

### Step 1 — Load flows

For each `flows/<stem>.flow.yaml`, extract `node["data"]["skill"]` from every node where `node["type"] == "skill"`, in document order. Include nodes with `optional: true` — optional nodes are still required skills for the bundle. Result: `flow_skills: dict[str, list[str]]` mapping stem → ordered skill names (bare names, no prefix).

**Pairing rule:** a flow `flows/<stem>.flow.yaml` is paired with bundle `bundles/<stem>.bundle.yaml` by matching stem (filename without extension). Example: `flows/standard-app.flow.yaml` → `bundles/standard-app.bundle.yaml`.

### Step 2 — Load bundles

For each `bundles/<stem>.bundle.yaml`, parse the `requires:` list. If the `requires:` key is absent, treat it as an empty list. Split entries into:
- `bundle_refs`: entries starting with `bundle:` (bare name after prefix: `bundle:mvp` → `"mvp"`)
- `skill_refs`: entries starting with `skill:` (bare name after prefix: `skill:concept-brief` → `"concept-brief"`)
- `other_refs`: anything else (preserved verbatim)

### Step 3 — Resolve ancestry

For each bundle, resolve `bundle_refs` recursively (union, any traversal order) to collect `ancestor_skills: set[str]` — the set of **bare skill names** (prefix already stripped) from all `skill:` entries in every ancestor bundle.

**Lookup rule:** a `bundle:foo` ref resolves to `bundles/foo.bundle.yaml` (strip `bundle:` prefix, append `.bundle.yaml`).

**Cycle detection:** track visited bundle stems during traversal; if a stem is visited twice, exit 1 with message: `"Circular bundle inheritance detected: <stem> → ... → <stem>"`.

### Step 4 — Compute missing skills

```python
# All sets contain bare names (no skill:/bundle: prefix)
covered = set(own_skill_refs) | ancestor_skills
missing = [s for s in flow_skills[stem] if s not in covered]
```

If `missing` is empty, skip this bundle (no write).

### Step 5 — Insert missing skills

Find the insertion point in the bundle YAML **text** (line-by-line, not re-serialised):

1. Scan for the last line matching `^  - skill:` — insert **after** this line.
2. If no `skill:` lines exist, scan for the first line matching `^  - bundle:` — insert **before** that line.
3. If neither exists, insert after the `requires:` key line.

Append one `  - skill:<name>` line (no space after colon, matching existing format) per missing skill, in flow-node order.

### Step 6 — Write and report

Write back only bundles that changed. Print:
```
Added 2 skill(s) to standard-app.bundle.yaml: [impl-slice-refactor, impl-quality-audit]
All bundles up to date.
```

---

## `validator.py` — Read-only Coverage Check

Validates that every skill in a flow is covered by its bundle (own `skill:*` entries + full ancestor chain). Does not write anything.

Exit codes:
- `0` — all bundles cover their flows
- `2` — at least one gap found (prints which bundle and which skills are missing)
- `1` — internal error (missing file, parse error)

Used by the agent after `compile_bundle.py` runs, and usable in CI.

---

## `SKILL.md` — Agent Steps

```
ROLE  Bundle compiler — ensures every skill in a flow is listed in its bundle's
      requires: list. Additive only: never removes entries a user has added.

WHEN TO USE
  - After adding a skill node to any flow YAML
  - Before releasing a new tier to verify the bundle is complete
  - As part of the skill catalog maintenance routine

STEPS
  1. Run: python lab/compile-bundle/compile_bundle.py
     Expected: prints summary of changes or "All bundles up to date"
  2. Run: python lab/compile-bundle/validator.py
     Expected: exits 0
  3. Run: git diff bundles/
     Show the diff to the user.
  4. If changes present: commit with message "chore: sync bundles from flows"
  5. If no changes: report "All bundles are already up to date — no commit needed"

MUST
  - Never remove existing requires: entries (additive only)
  - Insert new skill: entries after the last existing skill: line; if none exist, before the first bundle: line; format as `  - skill:<name>` (no space after colon)
  - Preserve all formatting, comments, and non-requires: fields verbatim
  - Run validator.py after compile_bundle.py and surface any failures before committing

NEVER
  - Delete or reorder existing requires: entries
  - Modify any field outside requires: (name, description, metadata, etc.)
  - Create new bundle files (only patches existing ones)
  - Commit if validator.py exits non-zero
```

---

## Invariants

- **Additive only.** The script never removes `requires:` entries. A user who adds `skill:my-custom-tool` to a bundle will keep it across re-runs.
- **Inheritance-aware.** Skills already provided by an ancestor bundle (`bundle:mvp` etc.) are not added again to the child bundle.
- **Flow-node order.** New skills are inserted in the same order they appear in the flow's `nodes` array.
- **No-op on up-to-date bundles.** If all flow skills are already covered, the file is not touched (no spurious mtime changes).
- **Idempotent.** Running the script twice produces the same result.

---

## Acceptance Test

Run from the **repo root** (`/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`):

```bash
python lab/compile-bundle/compile_bundle.py
git diff bundles/
```

Expected: zero diff. The hand-authored bundles already contain all flow skills; the script finds nothing to add and writes nothing.

Then run the validator:

```bash
python lab/compile-bundle/validator.py
```

Expected: exit 0.

---

## Error Handling

| Situation | Behaviour |
|---|---|
| Flow file exists but no matching bundle | Print warning, skip |
| Bundle file exists but no matching flow | Skip silently (user-only bundle) |
| Malformed YAML in flow or bundle | Exit 1 with filename and parse error |
| Circular bundle inheritance | Exit 1 with full cycle path: `"a → b → a"` |
| `requires:` key absent from bundle | Treat as empty list (safe default) |
| Flow references a skill name not found in catalog | Print warning, still add to bundle (skill may be a planned stub) |

---

## Out of Scope

- Creating new bundle files
- Removing skills from bundles
- Modifying flow files
- Validating flow YAML against `contracts/flow.schema.json` (that is `lab/validate`'s job)
