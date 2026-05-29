# Task 2E — `impl-quality/debug-{self-verify, handoff}` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author two general-purpose debugging skills under `impl-quality/`:
1. `impl-quality/debug-self-verify/SKILL.md` — produces a self-runnable verification protocol the AI can execute autonomously to determine "is this bug fixed?"
2. `impl-quality/debug-handoff/SKILL.md` — produces a self-contained markdown summary the user (or another agent) can paste into a fresh chat after `/clear`, containing bug description, attempts so far, current hypothesis, and next steps.

**Architecture:**
- Both skills are **interview-driven**: they ask the user (or read from existing slice scratch) for the bug description, current code state, and prior attempts. Per Iron Laws § 9, every question is sent as a standalone message — never bundled with a status update.
- Both skills share the same **input shape** (a "debug context" — symptom, repro steps, attempts, hypothesis) but diverge on output form: `self-verify` emits a **machine-runnable protocol** (test commands + expected outputs + success criteria); `handoff` emits a **human-pasteable narrative** (markdown for a fresh chat).
- Outputs land in a new `_debug/<id>/` workspace zone (mirroring the slice zones from SKILL_GRAPH.md § 7). The zone choice is **flagged for confirmation** (see "Open Question 1" below) before the executing agent commits to it.
- Each skill ships a `validator.py` that schema-checks the produced markdown (required headings present, required tables have the right columns).
- Each skill ships an `examples/` folder with 1-2 worked examples so the executing agent has a concrete output target.

**Tech Stack:**
- Skill DSL per `contracts/skill_grammar.md` and frontmatter per `contracts/asset_frontmatter.md`
- Markdown outputs (UTF-8, LF line endings) — both skills' outputs are markdown so they round-trip cleanly through chat paste
- Python 3.12+ for `validator.py` (PyYAML for frontmatter — but these outputs have no frontmatter; stdlib `re` suffices)

---

## Open Questions to Resolve Before Authoring

These are **flagged for the executing agent to surface to the user at the start of the session**. Do not silently assume an answer.

### Open Question 1 — Output zone

**Proposal:** New zone `_debug/<id>/` with these contents:
- `_debug/<id>/protocol.md` — output of `debug-self-verify`
- `_debug/<id>/handoff.md` — output of `debug-handoff`
- `_debug/<id>/context.md` — shared interview state (symptom + attempts), written by the FIRST debug skill invoked, read by the second so the user doesn't repeat themselves.

`<id>` is a kebab-case slug derived from the symptom (e.g. `login-redirect-loop`), or a timestamp (`2026-05-07-1430`) if the agent can't infer one.

**Lifetime:** per-bug, not per-slice. **Deletion policy:** TBD (proposal: deleted by the user / a future `debug-resolve` skill once the bug is closed; never auto-deleted by these two skills, because protocols may need re-running).

**Why a new zone (not `_slice/`):** debug sessions are not always tied to a slice. A user might run `debug-self-verify` against trunk code with no active slice. Sharing `_slice/impl/<id>/` would conflate "in-flight feature work" with "this is broken, please help."

**Why a new zone (not committed):** these are scratch artifacts. Committing them creates noise in git history; protocols are intended to be regenerated when re-debugging.

**Action for executing agent:** confirm with the user before authoring. If user prefers `_slice/<id>/debug/`, adjust both skills' WRITES sections accordingly. If user prefers committing them, add to `.gitignore` consideration.

### Open Question 2 — Call sites

These skills aren't currently wired into any `flows/*.flow.yaml`. Their primary call sites are:
- **User invokes ad-hoc** when stuck (matches the SKILL_GRAPH.md § 5.2 hint: `─── if stuck mid-slice ──► impl-quality/debug/self-verify or impl-quality/debug/handoff`)
- **Another skill calls one of them on bug-out** (e.g. an `impl-slice/implement` that's been looping on a failing test could escalate to `debug-self-verify`)

**Action for executing agent:** do **not** try to resolve flow integration in this task. Just note the intended call sites in each SKILL.md's "When to Use" block. Flow wiring belongs to a future task (likely 2H or a follow-on).

### Open Question 3 — Naming: `debug-*` flat vs. `debug/` subdirectory

`SKILL_GRAPH.md` uses both forms in places (`debug/self-verify` in § 5.2 and § 5.3, `debug-{self-verify, handoff}` in § 9 and the parent plan). Per `CONTRIBUTING.md`, the `name:` field must match the parent directory.

**Decision (pinned):** Use **flat** layout — `impl-quality/debug-self-verify/` and `impl-quality/debug-handoff/`. Reasons:
- Mirrors the existing flat siblings (`impl-quality/test-unit/`, `impl-quality/standards-discover/`) — no other `impl-quality/*` skill uses a sub-cluster directory
- Matches the parent plan's verbatim names: `impl-quality-debug-self-verify`, `impl-quality-debug-handoff`
- Path-based naming yields the exact `name:` strings the parent plan requires

If the user pushes back wanting `impl-quality/debug/{self-verify,handoff}/`, the `name:` would shorten to `debug-self-verify` and `debug-handoff` (mirroring the `template-postxl` exception in `CONTRIBUTING.md`). Surface this as an option but default to flat.

---

## Pre-flight

Before any authoring, confirm baseline state.

- [ ] **Pre-1: Confirm cwd**

Run: `pwd`
Expected: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

- [ ] **Pre-2: Confirm branch / git state**

Run: `git status -sb`
Expected: clean tree (or only the in-progress migration branch's untracked plan docs). If dirty in unrelated files, stop and clarify with the user.

- [ ] **Pre-3: Confirm target dirs do NOT yet exist**

Run: `ls impl-quality/debug-self-verify impl-quality/debug-handoff 2>&1 | grep -i "no such"`
Expected: both paths report "No such file or directory". If either exists, STOP and read the existing files before continuing.

- [ ] **Pre-4: Confirm sibling skills exist (so the new skills can match their tone)**

Run: `ls impl-quality/`
Expected: includes `audit/`, `eval-code/`, `ready/`, `test-unit/`, `standards-discover/`. Use these as tone reference.

- [ ] **Pre-5: Confirm source documents are readable**

Run: `wc -l SKILL_GRAPH.md contracts/iron_laws.md contracts/skill_grammar.md contracts/asset_frontmatter.md CONTRIBUTING.md`
Expected: line counts non-zero for all five.

- [ ] **Pre-6: Resolve all three Open Questions above**

Send each Open Question as a **standalone message** to the user (Iron Laws § 9). Wait for answers. Update this plan in-place if any answer differs from the pinned proposal, before continuing to Task 1.

---

## Source-of-Truth Anchors (read before authoring)

The executing agent MUST read each of these once, in this order, before starting Task 1:

1. `SKILL_GRAPH.md` § 5.2 (the line `─── if stuck mid-slice ──► impl-quality/debug/...`) and § 5.3 (the `debug/` block describing both skills' purpose)
2. `contracts/iron_laws.md` § 9 — both skills are interview-driven; this rule is non-negotiable
3. `contracts/asset_frontmatter.md` § "Skill — SKILL.md" — frontmatter schema, especially `metadata.prerequisites`
4. `contracts/skill_grammar.md` — full file; both SKILL.md bodies are written in this DSL
5. `CONTRIBUTING.md` — naming, integrity checklist
6. Sibling tone references:
   - `impl-quality/audit/SKILL.md` — for the "ROLE / READS / WRITES / MUST / NEVER / STEP / CHECKLIST" structure
   - `impl-quality/test-unit/SKILL.md` — for frontmatter `prerequisites` example
   - `impl-quality/eval-code/SKILL.md` — for parallel-sub-agent pattern (relevant for `self-verify` if it dispatches verification)

---

## Pinned Schema — `_debug/<id>/context.md` (shared input scratch)

Both skills read this file if it exists; the first skill invoked writes it. This avoids re-interviewing the user when both skills are run in sequence (typical: `self-verify` first to confirm it's actually broken, then `handoff` if escalating).

```markdown
# Debug Context — <id>

## Symptom
<1-3 sentences: what the user observes vs. what they expected>

## Repro
<numbered steps, or "intermittent — see notes" if not reliable>
1. ...
2. ...

## Environment
<bullet list>
- OS / runtime versions
- Branch / commit SHA
- Relevant env vars (redacted as `<env:VAR_NAME>` if sensitive)

## Attempts So Far
| # | What was tried | Outcome | Why ruled out (or partial) |
|---|----------------|---------|----------------------------|
| 1 | ...            | ...     | ...                        |

## Current Hypothesis
<1-3 sentences. May be empty on first call.>

## Files Touched
<bullet list of paths the user thinks are involved>
```

This is the **canonical shared input shape**. Both skills' outputs reference it.

---

## Pinned Schema — `_debug/<id>/protocol.md` (output of `debug-self-verify`)

This schema is the **acceptance contract** for `debug-self-verify`. Authoring is done when a produced protocol matches this shape and `validator.py` passes.

```markdown
# Verification Protocol — <id>

## Bug Summary
<1-2 sentences referencing _debug/<id>/context.md § Symptom>

## Hypothesis Under Test
<1-3 sentences: which hypothesis from context.md does this protocol verify? If protocol is hypothesis-agnostic (just "is the symptom gone?"), state that explicitly.>

## Verification Steps

Each step is independently executable. Steps are ordered cheap-to-expensive (so the AI bails early on first signal).

### Step 1: <short name>
- **Command:** `<exact shell command>`
- **Expected output (success):** `<literal string or regex, fenced>`
- **Expected output (still-broken):** `<literal string or regex, fenced>` *(optional — when present, gives a positive failure signal)*
- **Pass criterion:** `<one-line predicate, e.g. "exit code 0 AND stdout matches expected">`

### Step 2: ...
(repeat)

## Success Criteria

The bug is verified fixed when **all** of the following hold:
- [ ] Step 1 pass criterion met
- [ ] Step 2 pass criterion met
- [ ] ... (one checkbox per step above)

## Failure Exit Conditions

If any of these occur, STOP the protocol and escalate (typically to `debug-handoff`):
- A step's command errors with a setup failure (not a test failure) — e.g. `command not found`, missing dependency
- A step's output matches neither expected-success nor expected-broken — protocol no longer covers reality
- Maximum N=3 retry attempts on a flaky step exhausted

## Notes for Future Re-runs
<free-form bullet list. AI fills in things observed during the protocol design that the next runner should know.>
```

**Why this shape:**
- The "Verification Steps" section is **machine-runnable**: the AI executes each command and compares output to the expected fence. No human-in-the-loop required for the protocol to produce a verdict.
- "Failure Exit Conditions" is the safety valve — without it, a broken protocol loops or false-passes.
- "Hypothesis Under Test" forces the protocol author to decide: am I verifying the **symptom is gone** (hypothesis-agnostic) or **a specific cause is fixed** (hypothesis-specific)? Both are valid, but mixing them silently breaks the protocol.

---

## Pinned Schema — `_debug/<id>/handoff.md` (output of `debug-handoff`)

This schema is the **acceptance contract** for `debug-handoff`. Authoring is done when a produced handoff matches this shape and `validator.py` passes.

```markdown
# Debug Handoff — <id>

> Paste this entire file into a fresh chat. It is self-contained: no prior context required.

## Bug Description
<2-5 sentences. Symptom + impact + repro reliability.>

## Repro Steps
1. ...
2. ...

(If non-deterministic: state frequency, e.g. "fails ~30% of the time on Mondays".)

## Environment
- OS / runtime: <values>
- Branch / commit: <SHA>
- Relevant env vars: <redacted list>
- Last working commit (if known): <SHA>

## Attempts So Far

| # | What was tried | Outcome | Why ruled out |
|---|----------------|---------|---------------|
| 1 | <action>       | <result>| <reasoning>   |
| 2 | ...            | ...     | ...           |

## Current Hypothesis
<1-3 sentences. State confidence: low / medium / high.>

## Suggested Next Steps
1. <next experiment, with rationale>
2. <fallback experiment if 1 fails>
3. <escalation path if both fail — e.g. "ask the user for more logs">

## Files & Paths Involved
- `<path>` — <one-line role in the bug>
- ...

## Open Questions for the Next Agent
- <question 1>
- <question 2>

## Out-of-Scope (do NOT do these)
- <action that was explicitly ruled out by the user>
- ...
```

**Why this shape:**
- "Paste this entire file into a fresh chat" is the **explicit usage contract** — the file's job is to be self-contained. The validator checks that no `<id>` placeholders remain unresolved, no relative paths leak (everything must be absolute or repo-rooted).
- "Out-of-Scope" is the **anti-rabbit-hole guard** — without it, the next agent re-tries things the user has already ruled out.
- "Attempts So Far" is a **table** (not prose) so the next agent can scan it in 5 seconds. Prose buries information.
- "Confidence: low/medium/high" on the hypothesis is required — the next agent calibrates how aggressively to challenge it.

---

## File Targets (absolute paths)

### Skill 1: `debug-self-verify`
- Create: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/impl-quality/debug-self-verify/SKILL.md`
- Create: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/impl-quality/debug-self-verify/validator.py`
- Create: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/impl-quality/debug-self-verify/examples/protocol-flaky-test.md`
- Create: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/impl-quality/debug-self-verify/examples/protocol-build-error.md`

### Skill 2: `debug-handoff`
- Create: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/impl-quality/debug-handoff/SKILL.md`
- Create: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/impl-quality/debug-handoff/validator.py`
- Create: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/impl-quality/debug-handoff/examples/handoff-auth-redirect.md`
- Create: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/impl-quality/debug-handoff/examples/handoff-database-deadlock.md`

---

## Task 1: Author `impl-quality/debug-self-verify`

**Files:**
- Create: `impl-quality/debug-self-verify/SKILL.md`
- Create: `impl-quality/debug-self-verify/validator.py`
- Create: `impl-quality/debug-self-verify/examples/protocol-flaky-test.md`
- Create: `impl-quality/debug-self-verify/examples/protocol-build-error.md`

**Pinned READS / WRITES contract:**

```
READS
  ? _debug/<id>/context.md           — shared interview state (if a prior debug skill ran)
  package.json / pyproject.toml      — to detect runnable test/build commands
  ? _slice/impl/<id>/plan.md         — if invoked from inside a slice, the plan's testing strategy

WRITES
  _debug/<id>/protocol.md            — the verification protocol (canonical schema above)
  _debug/<id>/context.md             — only if it does not yet exist (interview output)
```

**Pinned `name:`** — `impl-quality-debug-self-verify` (path-based per CONTRIBUTING.md)

- [ ] **Step 1: Create the skill directory and stub examples**

Run:
```bash
mkdir -p impl-quality/debug-self-verify/examples
ls impl-quality/debug-self-verify/
```
Expected: directory exists, `examples/` subdir present, no other files yet.

- [ ] **Step 2: Draft `SKILL.md` frontmatter**

Required frontmatter fields per `contracts/asset_frontmatter.md`:
- `name: impl-quality-debug-self-verify`
- `description: "Use when the user is stuck on a bug and wants the AI to autonomously verify whether a fix worked. Produces a self-runnable verification protocol (test commands + expected outputs + success criteria) the AI executes without user-as-test-loop."`
- `metadata.version: "0.1.0"` (alpha, first release)
- `metadata.tags: [debug, verify, autonomous, protocol, test-loop, fix-verification]`
- `metadata.stage: alpha`
- `metadata.prerequisites.inputs_required` — `bug_description` (textarea), `repro_steps` (textarea)
- `metadata.prerequisites.inputs_optional` — `hypothesis` (textarea), `bug_id` (text — for `<id>` slug; auto-derive if missing)
- `metadata.prerequisites.reads` — `_debug/<id>/context.md`, `package.json`, `_slice/impl/<id>/plan.md`
- `metadata.prerequisites.produces` — `_debug/<id>/protocol.md`, `_debug/<id>/context.md`

- [ ] **Step 3: Draft `SKILL.md` body in DSL**

Required sections (per `contracts/skill_grammar.md`):

1. **ROLE** — one sentence: "Verification Protocol Author — turns a bug + hypothesis into a self-runnable test plan the AI executes autonomously to verdict."
2. **READS / WRITES** — copy from the pinned contract above.
3. **REFERENCES** — `contracts/iron_laws.md`, `contracts/skill_grammar.md`, plus `examples/protocol-flaky-test.md` and `examples/protocol-build-error.md` as tone targets.
4. **MUST / NEVER** — at minimum:
   - `MUST  ask the user for bug description and repro as a STANDALONE message (Iron Laws § 9)`
   - `MUST  produce a protocol that conforms to the pinned schema (every required heading present)`
   - `MUST  order verification steps cheap-to-expensive`
   - `MUST  include explicit failure exit conditions`
   - `NEVER  block waiting for human-in-the-loop verification — the protocol must be machine-runnable end to end`
   - `NEVER  invent test commands not supported by the project's `package.json` / `pyproject.toml`
5. **STEP 1: Read or gather context**
   - IF `_debug/<id>/context.md` exists: read it as authoritative
   - ELSE: interview the user. Ask **bug description** as one standalone message. Wait. Ask **repro steps** as a second standalone message. Wait. Ask **current hypothesis (optional)** as a third. Then write `_debug/<id>/context.md` per the shared schema.
6. **STEP 2: Detect runnable commands**
   - Read `package.json` scripts: `test`, `lint`, `typecheck`, `build`. Note any custom scripts mentioned in the bug description.
   - For Python projects, check `pyproject.toml` for `[tool.pytest.ini_options]`, `[tool.ruff]`, etc.
   - List the candidate commands the protocol may use.
7. **STEP 3: Choose hypothesis-agnostic OR hypothesis-specific**
   - If the user provided a hypothesis with confidence ≥ medium → produce a **hypothesis-specific** protocol (verifies the cause is fixed, e.g. "the race condition no longer occurs under N concurrent requests").
   - Otherwise → produce a **hypothesis-agnostic** protocol (verifies only the symptom is gone).
   - State the choice explicitly in the output's "Hypothesis Under Test" section.
8. **STEP 4: Draft verification steps**
   - Order: cheap (lint, typecheck) → medium (unit test) → expensive (integration / e2e / manual repro automation).
   - Each step gets exact command, expected-success regex, expected-broken regex (if relevant), pass criterion.
9. **STEP 5: Draft failure exit conditions**
   - Setup failure (command-not-found, env missing)
   - Output mismatch (neither success nor broken regex matches — protocol is stale)
   - Retry exhaustion on flaky steps (cap N=3)
10. **STEP 6: Write `_debug/<id>/protocol.md`** per the pinned schema.
11. **STEP 7: Self-validate** by running `python validator.py _debug/<id>/protocol.md`. If it fails, fix the protocol and re-run. Do not return until validator passes.
12. **CHECKPOINT** — show the protocol to the user. Standalone message. Ask: "Run this protocol now, or save it for later?" If "run now", iterate the protocol's steps and report the verdict.

13. **CHECKLIST** at the end of the SKILL body (per `contracts/skill_grammar.md`):
    - `[ ] _debug/<id>/protocol.md exists and validator passes`
    - `[ ] All verification steps have exact commands (no placeholders)`
    - `[ ] Hypothesis Under Test section is non-empty`
    - `[ ] Failure exit conditions present`
    - `[ ] User shown the protocol via standalone message`

- [ ] **Step 4: Verify SKILL.md frontmatter parses**

Run: `python -c "import yaml; doc = open('impl-quality/debug-self-verify/SKILL.md').read().split('---')[1]; print(yaml.safe_load(doc).get('name'))"`
Expected: `impl-quality-debug-self-verify`

- [ ] **Step 5: Write `validator.py`**

Schema-shape check on `_debug/<id>/protocol.md`:
- Required H1 heading: `# Verification Protocol —`
- Required H2 headings (in order): `## Bug Summary`, `## Hypothesis Under Test`, `## Verification Steps`, `## Success Criteria`, `## Failure Exit Conditions`, `## Notes for Future Re-runs`
- Under `## Verification Steps`: at least one `### Step ` heading
- Each `### Step ` block must contain the four bullets: `- **Command:**`, `- **Expected output (success):**`, `- **Pass criterion:**` (the "still-broken" bullet is optional)
- `## Success Criteria` must have at least one `- [ ]` checkbox
- Exit code 0 if shape valid, exit code 1 with diagnostic if not
- CLI: `python validator.py <path-to-protocol.md>`

- [ ] **Step 6: Run validator on a known-bad input**

Run:
```bash
echo "# wrong heading" > /tmp/bad-protocol.md
python impl-quality/debug-self-verify/validator.py /tmp/bad-protocol.md
echo "exit=$?"
rm /tmp/bad-protocol.md
```
Expected: non-zero exit, diagnostic mentions missing required headings.

- [ ] **Step 7: Author `examples/protocol-flaky-test.md`**

Worked example: a CI flaky test ("login_test fails 1 in 5 runs"). Hypothesis-agnostic protocol that runs the test 20 times and asserts pass-rate ≥ 19/20. Must conform to the pinned schema and pass the validator.

- [ ] **Step 8: Author `examples/protocol-build-error.md`**

Worked example: a TypeScript build error after a refactor. Hypothesis-specific protocol that runs `bun run typecheck` and `bun run build` and asserts both pass with exit 0. Must conform to the pinned schema and pass the validator.

- [ ] **Step 9: Run validator on both examples**

Run:
```bash
python impl-quality/debug-self-verify/validator.py impl-quality/debug-self-verify/examples/protocol-flaky-test.md && \
python impl-quality/debug-self-verify/validator.py impl-quality/debug-self-verify/examples/protocol-build-error.md
echo "exit=$?"
```
Expected: exit 0 for both.

- [ ] **Step 10: Commit Task 1**

Run:
```bash
git add impl-quality/debug-self-verify/
git status -s impl-quality/debug-self-verify/
git commit -m "feat(impl-quality): add debug-self-verify skill"
```
Expected: clean commit, only the new files.

---

## Task 2: Author `impl-quality/debug-handoff`

**Files:**
- Create: `impl-quality/debug-handoff/SKILL.md`
- Create: `impl-quality/debug-handoff/validator.py`
- Create: `impl-quality/debug-handoff/examples/handoff-auth-redirect.md`
- Create: `impl-quality/debug-handoff/examples/handoff-database-deadlock.md`

**Pinned READS / WRITES contract:**

```
READS
  ? _debug/<id>/context.md           — shared interview state (if a prior debug skill ran)
  ? _debug/<id>/protocol.md          — if self-verify ran first, attempts and outcomes feed the handoff
  ? _slice/impl/<id>/plan.md         — if invoked from inside a slice
  git log -10 --oneline              — recent commit history for the "Last working commit" field

WRITES
  _debug/<id>/handoff.md             — the handoff document (canonical schema above)
  _debug/<id>/context.md             — only if it does not yet exist (interview output)
```

**Pinned `name:`** — `impl-quality-debug-handoff` (path-based per CONTRIBUTING.md)

- [ ] **Step 1: Create the skill directory and stub examples**

Run:
```bash
mkdir -p impl-quality/debug-handoff/examples
ls impl-quality/debug-handoff/
```
Expected: directory exists, `examples/` subdir present.

- [ ] **Step 2: Draft `SKILL.md` frontmatter**

Required fields:
- `name: impl-quality-debug-handoff`
- `description: "Use when the user is stuck on a bug and wants to hand off to a fresh agent (or themselves after /clear). Produces a self-contained markdown summary — bug description, attempts so far, current hypothesis, suggested next steps — pasteable into a new chat with no prior context."`
- `metadata.version: "0.1.0"`
- `metadata.tags: [debug, handoff, fresh-chat, escalation, context-transfer]`
- `metadata.stage: alpha`
- `metadata.prerequisites.inputs_required` — `bug_description` (textarea), `attempts_so_far` (textarea)
- `metadata.prerequisites.inputs_optional` — `hypothesis` (textarea), `out_of_scope` (textarea), `bug_id` (text)
- `metadata.prerequisites.reads` — `_debug/<id>/context.md`, `_debug/<id>/protocol.md`, `_slice/impl/<id>/plan.md`
- `metadata.prerequisites.produces` — `_debug/<id>/handoff.md`, `_debug/<id>/context.md`

- [ ] **Step 3: Draft `SKILL.md` body in DSL**

Required sections:

1. **ROLE** — one sentence: "Debug Handoff Author — converts an in-progress debug session into a self-contained markdown brief the next agent can pick up cold."
2. **READS / WRITES** — copy from the pinned contract above.
3. **REFERENCES** — `contracts/iron_laws.md`, `contracts/skill_grammar.md`, plus the two `examples/handoff-*.md` files.
4. **MUST / NEVER** — at minimum:
   - `MUST  ask each interview question as a STANDALONE message (Iron Laws § 9)`
   - `MUST  produce a handoff that conforms to the pinned schema (every required heading present)`
   - `MUST  ensure the output is self-contained — no relative paths, no in-chat references like "as discussed above"`
   - `MUST  redact obvious secrets (api keys, passwords, tokens) using <env:VAR_NAME> placeholders`
   - `NEVER  link to chat history or local-only resources the next agent cannot access`
   - `NEVER  fabricate attempts or hypotheses — if the user did not state them, write "(none yet)"`
5. **STEP 1: Read or gather context** — same logic as `debug-self-verify` Step 1. Reads `_debug/<id>/context.md` if present; else interviews the user with one standalone question per field.
6. **STEP 2: Read prior protocol if present**
   - IF `_debug/<id>/protocol.md` exists, parse its "Verification Steps" and outcomes (if executed). Each executed step becomes a row in the handoff's "Attempts So Far" table.
7. **STEP 3: Read git log for "Last working commit" candidate**
   - `RUN  git log -10 --oneline`
   - Ask the user (standalone message): "Which of these commits was the last known good?" — or accept "unknown".
8. **STEP 4: Interview for missing fields**
   - Walk the schema. For each required section that is still empty, send one standalone question.
   - For "Out-of-Scope": explicitly ask "Are there any approaches you've ruled out that the next agent should NOT try?" — separate message.
9. **STEP 5: Draft `handoff.md`** per the pinned schema.
10. **STEP 6: Self-redact pass**
    - Scan for `process.env.SECRET_*`, hardcoded `Bearer `, AWS-key-shaped strings, etc.
    - Replace with `<env:VAR_NAME>` placeholders. Note the redaction in the "Environment" section.
11. **STEP 7: Self-validate** with `python validator.py _debug/<id>/handoff.md`. Fix any failures, re-run.
12. **CHECKPOINT** — show the handoff to the user. Standalone message: "Ready to copy. Anything to add before you paste it into a fresh chat?"

13. **CHECKLIST** at end:
    - `[ ] _debug/<id>/handoff.md exists and validator passes`
    - `[ ] All schema sections present and non-empty (or marked "(none yet)")`
    - `[ ] No relative chat references ("see above", "you mentioned earlier")`
    - `[ ] Secrets redacted to `<env:VAR>` placeholders`
    - `[ ] Confidence level on hypothesis is one of: low / medium / high`

- [ ] **Step 4: Verify SKILL.md frontmatter parses**

Run: `python -c "import yaml; doc = open('impl-quality/debug-handoff/SKILL.md').read().split('---')[1]; print(yaml.safe_load(doc).get('name'))"`
Expected: `impl-quality-debug-handoff`

- [ ] **Step 5: Write `validator.py`**

Schema-shape check on `_debug/<id>/handoff.md`:
- Required H1 heading: `# Debug Handoff —`
- Required H2 headings (in order): `## Bug Description`, `## Repro Steps`, `## Environment`, `## Attempts So Far`, `## Current Hypothesis`, `## Suggested Next Steps`, `## Files & Paths Involved`, `## Open Questions for the Next Agent`, `## Out-of-Scope (do NOT do these)`
- `## Attempts So Far` must contain a markdown table with header row `| # | What was tried | Outcome | Why ruled out |`
- `## Current Hypothesis` body must contain one of: `low`, `medium`, `high` (case-insensitive)
- `## Suggested Next Steps` must contain a numbered list (at least one `1. ` line)
- The `<id>` placeholder must NOT appear unresolved in the body
- Exit code 0 if shape valid, 1 with diagnostic if not
- CLI: `python validator.py <path-to-handoff.md>`

- [ ] **Step 6: Run validator on a known-bad input**

Run:
```bash
echo "# wrong heading <id>" > /tmp/bad-handoff.md
python impl-quality/debug-handoff/validator.py /tmp/bad-handoff.md
echo "exit=$?"
rm /tmp/bad-handoff.md
```
Expected: non-zero exit, diagnostic mentions both wrong heading and unresolved `<id>`.

- [ ] **Step 7: Author `examples/handoff-auth-redirect.md`**

Worked example: an OAuth callback redirect-loop bug. Includes 3 attempts (env var, middleware order, cookie domain), low-confidence hypothesis (cookie SameSite), suggested next steps (capture network log, test in incognito, check upstream provider's recent changelogs), out-of-scope (already ruled out: switching providers).

- [ ] **Step 8: Author `examples/handoff-database-deadlock.md`**

Worked example: an intermittent Postgres deadlock under load. Includes 4 attempts, medium-confidence hypothesis (transaction order), suggested next steps (enable `log_lock_waits`, reduce isolation level on read paths, batch the offending writes), out-of-scope (no schema changes — too risky pre-release).

- [ ] **Step 9: Run validator on both examples**

Run:
```bash
python impl-quality/debug-handoff/validator.py impl-quality/debug-handoff/examples/handoff-auth-redirect.md && \
python impl-quality/debug-handoff/validator.py impl-quality/debug-handoff/examples/handoff-database-deadlock.md
echo "exit=$?"
```
Expected: exit 0 for both.

- [ ] **Step 10: Commit Task 2**

Run:
```bash
git add impl-quality/debug-handoff/
git status -s impl-quality/debug-handoff/
git commit -m "feat(impl-quality): add debug-handoff skill"
```
Expected: clean commit, only the new files.

---

## Task 3: Cross-skill verification

- [ ] **Step 1: Both skills' name fields match their directories**

Run:
```bash
grep -h "^name:" impl-quality/debug-self-verify/SKILL.md impl-quality/debug-handoff/SKILL.md
```
Expected (exact, two lines):
```
name: impl-quality-debug-self-verify
name: impl-quality-debug-handoff
```

- [ ] **Step 2: Both skills' READS reference the shared `_debug/<id>/context.md`**

Run: `grep -l "_debug/<id>/context.md" impl-quality/debug-*/SKILL.md`
Expected: both SKILL.md paths printed.

- [ ] **Step 3: Both skills' MUST blocks reference Iron Laws § 9 (standalone questions)**

Run: `grep -l "Iron Laws" impl-quality/debug-*/SKILL.md`
Expected: both SKILL.md paths printed.

- [ ] **Step 4: Both validators are runnable**

Run:
```bash
python impl-quality/debug-self-verify/validator.py --help 2>&1 | head -3 || true
python impl-quality/debug-handoff/validator.py --help 2>&1 | head -3 || true
```
Expected: each prints a brief usage line (no traceback).

- [ ] **Step 5: Run the catalog-installer dry parse on both skills**

If a workspace-level lint script exists for SKILL.md frontmatter, run it. Otherwise, parse with PyYAML:
```bash
python <<'EOF'
import yaml, sys
for p in ["impl-quality/debug-self-verify/SKILL.md", "impl-quality/debug-handoff/SKILL.md"]:
    raw = open(p).read()
    fm = raw.split("---", 2)[1]
    doc = yaml.safe_load(fm)
    assert doc["name"] == p.split("/")[1].replace("-self-verify","-debug-self-verify").replace("-handoff","-debug-handoff") or doc["name"].startswith("impl-quality-debug-"), p
    assert "metadata" in doc and "version" in doc["metadata"]
    assert isinstance(doc["metadata"].get("tags"), list) and len(doc["metadata"]["tags"]) >= 2
    print(p, "ok", doc["name"])
EOF
```
Expected: both lines print `ok` with the correct `name:`.

- [ ] **Step 6: Final commit (if anything was tweaked during cross-verify)**

If any files changed during Task 3:
```bash
git add impl-quality/debug-self-verify/ impl-quality/debug-handoff/
git commit -m "chore(impl-quality): cross-skill verification fixes"
```
Otherwise: skip.

---

## Definition of Done

The mini-plan is complete when **all** of the following hold:

- [ ] All three Open Questions resolved with the user before Task 1 began
- [ ] `impl-quality/debug-self-verify/` exists with `SKILL.md`, `validator.py`, and 2 examples
- [ ] `impl-quality/debug-handoff/` exists with `SKILL.md`, `validator.py`, and 2 examples
- [ ] Both `SKILL.md` files have `name:` matching their directory (per CONTRIBUTING.md)
- [ ] Both `SKILL.md` files have valid frontmatter parseable by PyYAML
- [ ] Both `SKILL.md` bodies are written in the DSL from `contracts/skill_grammar.md` (ROLE, READS, WRITES, MUST/NEVER, numbered STEPs, CHECKLIST)
- [ ] Both bodies explicitly reference Iron Laws § 9 in their MUST block (interview-driven, standalone questions)
- [ ] Both validators pass on their own examples (4 example files, all green)
- [ ] Both validators fail (non-zero exit) on a deliberately-broken input
- [ ] The shared `_debug/<id>/context.md` schema is referenced from both SKILL.md files
- [ ] Each skill's "When to Use" block notes the two intended call sites: ad-hoc by the user, or invoked by another skill on bug-out (Open Question 2)
- [ ] Two atomic commits landed (one per skill), plus an optional third for cross-verify fixes
- [ ] No changes to any flow file (flow wiring is out of scope per Open Question 2)

---

## Notes for the Executing Agent

- **Iron Laws § 9 is not optional.** Both skills ask the user multiple questions during the interview phase. Each one is its own message. The SKILL.md MUST emphasize this in the STEP bodies, not just in a passing MUST line — see the parent plan stub's emphasis (`★ surfaces unstated assumptions`) for tone.
- **Tone reference:** read `impl-quality/audit/SKILL.md` for the parallel-sub-agent pattern (relevant if `debug-self-verify` ever needs to dispatch verification across multiple test suites in parallel — but **do NOT add that complexity in v0.1.0**; keep both skills single-agent).
- **No flow wiring.** These skills are not called from any `flows/*.flow.yaml` yet. Don't create or modify any flow file. Just note the intended call sites in each SKILL.md.
- **Output zone is provisional.** `_debug/<id>/` is a new zone; `SKILL_GRAPH.md` § 7 currently only documents `_concept/`, `_implementation/`, `_slice/`, `_feedback/`. If the user approves `_debug/`, propose adding it to § 7 in a follow-up commit (out of scope for this task).
- **DRY between skills.** The shared `_debug/<id>/context.md` is the DRY mechanism. Don't re-interview the user if the prior skill already wrote it. Both skills explicitly check for it as their first STEP.
- **YAGNI.** v0.1.0. Don't build flow integration, don't auto-detect `<id>` from git branch names, don't ship a `debug-resolve` skill that cleans up `_debug/`. Those are future work.
- **TDD.** Steps 5-6 and 7-9 of each task are deliberately structured as: write the validator → prove it rejects bad input → write the example that the validator must accept. This is the Red→Green cycle for schema-shape-checked outputs.
- **Frequent commits.** Each task ends with a commit. Don't batch them.
