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

**Concerns are written by the receiver.** A `build-*` run appends its concerns to `_concept/11_build/decisions.md` before it returns (`tree/11_build/decisions.md`); any other run records them where its route keeps reasons (a feature's dossier), or else only under `Concerns:`.

**The interview relay.** A delegate cannot reach the user in Claude Code or omp, so every user conversation stays with the lead.

1. The receiver resolves facts (`tree/protocol/running.md § How a skill runs`, rule 1) and drafts. The draft stays where the route already keeps work in progress, a file that carries no `approved:` until the yes (the `open` feature dossier, a pending brief), and `Draft:` names its path. An artifact its node writes only after the yes is not written early: `Draft:` then holds the draft itself. When it needs a decision it returns `NEEDS_CONTEXT` whose `Question:` is one decision batch formatted per rule 2 of that section.
2. The lead answers the batch per the run's domain row of `## Working together` in `_concept/01_meta/expectations.md` (`tree/01_meta/expectations.md § Reading it`): under `user decides` it puts the batch to the user unchanged (no rewording, no options added or dropped). It sends the run again with the answers verbatim and the `Draft:` line unchanged.
3. An approval is a decision batch like any other: the receiver writes `approved:` only in the run that carries the user's own yes; an artifact the lead approved under `agent decides and reports` is written without it.
4. The lead never edits an artifact a delegate owns. A host tool only the lead holds (a review hunk, an editor that opens a file) carries the delegate's change unchanged: the delegate returns the change, the lead submits it and passes the user's decision back.

**Hosts without the skaileup agents.** Where the `skaileup-lead` and its delegates are not installed, the session agent is the lead and the relay above applies unchanged. It sends a skill run to a generic subagent with the verbatim `Run skill <id>` prompt, the status-block contract of this section and the sentence "You cannot reach the user: return NEEDS_CONTEXT with a decision batch for every choice the user owns; never close one with your recommendation." A plan written by the session agent answers no skill's decision batch in advance.

**Work another agent owns.** A receiver whose route needs a skill another agent composes does not run it: it returns `NEEDS_CONTEXT` with no `Question:` and the run under `Missing:`, `evidence pass — <skill> <scope>` for `concept-reverse` or `concept-research` and `skill run — <skill> <args>` for any other (a `spec-feature` run that needs a new screen: `skill run — experience-screen <screen>`). The lead sends that run to the agent that owns the skill, then sends the original run again with the result's paths. A receiver that cannot start its own helper contexts runs its helper passes itself, one after another.

**Parallel only when the write sets are disjoint.** Two receivers run at once only when no path one may write or propose into is one the other may (`owner:` and `may_propose:` of the nodes their routes visit).

A partial result with no status leaves the sender guessing; a code makes it act.
