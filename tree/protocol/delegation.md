# Delegation

## Delegation

One protocol for every hand-over of work to another agent context: the lead sending a skill run to the agent that owns the skill, and a skill sending a helper pass (a research topic, a detection pass) to a fresh context. Agents cite this section; nothing restates it.

**The task goes verbatim.** The receiver holds only what the prompt carries and the files it reads, none of the conversation. Paste the full task: for a skill run, the whole `Run skill <id>` prompt as the host sent it, the skill body and any onboarding block included, never a summary and never a pointer to a plan file. A repeat run carries the answers verbatim and the receiver's `Draft:` line unchanged.

**The receiver ends with one status block**, and the sender acts on the status and collects the artifacts:

```
STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED

[If DONE_WITH_CONCERNS]  Concerns: <trade-offs, deviations, debt incurred>
[If NEEDS_CONTEXT]       Missing:  <what is absent>
                         Question: <one decision batch, or none when Missing names a run another agent owns>
                         Draft:    <the path of the draft, or the draft itself>
[If BLOCKED]             Reason:   <what cannot be resolved>
                         Route:    context | escalate-model | decompose
```

| Status | Meaning | Sender's action |
|---|---|---|
| `DONE` | All requirements met, tests pass | Accept output, advance flow |
| `DONE_WITH_CONCERNS` | Implemented but with trade-offs or notes | Accept, name the concerns in the completion summary, advance |
| `NEEDS_CONTEXT` | Missing information or ambiguous requirement | A decision batch: answer it per the interview relay, step 2. A run another agent owns: send it to that agent, never to the user (`Work another agent owns`). Then send the run again with the answers or the result's paths and the `Draft:` line |
| `BLOCKED` | Cannot proceed — see route | Follow the route below |

| Route | When to use | Sender's response |
|---|---|---|
| `context` | A specific question can unblock the task | Answer it as a decision batch (interview relay, step 2); re-dispatch with the answer |
| `escalate-model` | Task exceeded model capability | Name it in the completion summary; re-dispatch on a stronger model |
| `decompose` | Task is too large to execute atomically | Break into smaller tasks; re-dispatch each |

**Concerns are written by the receiver.** A `build-*` run posts its concerns as one comment on the parent issue of the spec it built (the spec's tracker issue) before it returns, and repeats them under `Concerns:`; without a tracker issue, `Concerns:` is their only place. Any other run records them where its route keeps reasons (a feature's dossier), or else only under `Concerns:`. A concern that is itself an ADR-grade choice — it passes the three-test gate of `tree/docs/adr/README.md § Writing it` — is also written into the run's proposal file as a decision record; the rest never becomes one.

**The interview relay.** A delegate cannot reach the user in Claude Code or omp, so every user conversation stays with the lead.

1. The receiver resolves facts (`tree/protocol/running.md § How a skill runs`, rule 1) and drafts. The draft stays where the route already keeps work in progress, a file that carries no `approved:` until the yes (the `open` feature dossier, a pending brief), and `Draft:` names its path. An artifact its node writes only after the yes is not written early: `Draft:` then holds the draft itself. When it needs a decision it returns `NEEDS_CONTEXT` whose `Question:` is one decision batch formatted per rule 2 of that section.
2. The lead answers the batch per the run's domain row of `## Working together` in `_concept/01_meta/expectations.md` (`tree/01_meta/expectations.md § Reading it`): under `user decides` it puts the batch to the user unchanged (no rewording, no options added or dropped). It sends the run again with the answers verbatim and the `Draft:` line unchanged.
3. An approval is a decision batch like any other: the receiver writes `approved:` only in the run that carries the user's own yes; an artifact the lead approved under `agent decides and reports` is written without it.
4. The lead never edits an artifact a delegate owns. A host tool only the lead holds (a review hunk, an editor that opens a file) carries the delegate's change unchanged: the delegate returns the change, the lead submits it and passes the user's decision back.

**Hosts without the skaileup agents.** Where the `skaileup-lead` and its delegates are not installed, the session agent is the lead and the relay above applies unchanged. It sends a skill run to a generic subagent with the verbatim `Run skill <id>` prompt, the status-block contract of this section and the sentence "You cannot reach the user: return NEEDS_CONTEXT with a decision batch for every choice the user owns; never close one with your recommendation." A plan written by the session agent answers no skill's decision batch in advance.

**`build-implement` is never delegated.** It follows `implement-spec`, which starts an implementer subagent per ticket, and a delegate cannot start subagents of its own; the lead runs it in its own context, with or without the skaileup agents.

**Work another agent owns.** A receiver whose route needs a skill another agent composes does not run it: it returns `NEEDS_CONTEXT` with no `Question:` and the run under `Missing:`, `evidence pass — <skill> <scope>` for `concept-reverse` or `concept-research` and `skill run — <skill> <args>` for any other (a `spec-feature` run that needs a new screen: `skill run — experience-screen <screen>`). The lead sends that run to the agent that owns the skill, then sends the original run again with the result's paths. A receiver that cannot start its own helper contexts runs its helper passes itself, one after another.

**Parallel only when the owned write sets are disjoint.** Two receivers run at once only when no path one owns is one the other owns (`owner:` of the nodes their routes visit). `may_propose:` does not count, nor does `_concept/proposals/`: each run that proposes writes a new proposal file of its own (`tree/proposals/README.md`), so two runs never write the same one.

A partial result with no status leaves the sender guessing; a code makes it act.

## Several specs at once

Several features move through the concept and the build at once. The work runs in parallel, and four points run serially; the lead owns those points and the order between waves.

- **Parallel per feature, across features.** `spec-feature`, `experience-behaviors` (per featureset), `experience-screen` (per screen), `build-plan`, `build-implement` and `quality-review` run at once for different features: each run owns disjoint paths, and proposals never collide because each run writes its own proposal file (`## Delegation`, *Parallel only when the owned write sets are disjoint*). `build-plan` is the exception for specs that share a `follows:` pattern or a `data_entities` entry: the lead runs those one after another, so each run finds the tickets of the one before it (serial points 3 and 4); specs that share neither still plan at once.
- **Serial point 1 — the promotion pass.** After each parallel wave, every owner with pending proposal entries settles them in one run of its own. Owners of different artifacts settle in parallel; an owner never runs in parallel with itself. `skaileup`'s ADR promotion (`tree/docs/adr/README.md § Writing it`) is part of the pass.
- **Serial point 2 — the proposal gate.** `build-plan` and `build-implement` for a feature stop while a pending proposal targets that feature's spec, a screen it names, a model entity it names or a glossary term it names. The check is a grep of `_concept/proposals/*.yaml` for entries at `status: proposed` whose `target` (and, for the model and the glossary, `anchor`) is one of those.
- **Serial point 3 — a shared pattern.** The first `build-plan` to meet a `kind: pattern` ADR its spec `follows:` that has no shared-module ticket yet (`gh issue list --search "adr:<slug>"` finds none) creates one ticket, "Shared module for adr:<slug>", under its own parent. Every later spec that follows that ADR makes its first ticket `blocked-by` that ticket, a native link across parents.
- **Serial point 4 — data model migrations.** `architecture-datamodel` promotes model changes one run at a time. Each spec's schema ticket is `blocked-by` the schema ticket of every earlier open spec that touches the same entity, earlier meaning its parent issue was opened first. Integration branches merge into their base (`main`, or `build/<app-slug>` where `build-branch` opened one) one at a time, and each rebases on that base before its PR is marked ready.
- **One `implement-spec` per spec.** Each spec builds in its own session and worktree. The lead prints one run line per spec (`/build-implement <featureset>/<feature>`) rather than juggling several frontiers; the order across specs lives only in the tracker's `blocked-by` edges.
