---
path: _concept/10_blueprint/architecture.md
summary: custom modules, protocols and every external integration beyond the template
writers: [architecture-system]
---

# _concept/10_blueprint/architecture.md

The apps, custom modules, communication protocols and external integrations this project adds beyond its template, and nothing else. What the chosen stack already provides is written once, in `templates/<tech_stack_skill>/TEMPLATE.md`; restating it here produces a second copy that drifts. The artifact is optional by design: a project whose features need nothing beyond its stack gets a short document saying exactly that, which is the answer `build-plan` needs. `architecture-datamodel` reads it for the entities a module implies, `build-plan` for the work a slice crosses, `build-implement` for what to build against.

## Format

```yaml
---
apps: []                        # deployable units, e.g. [api, web, worker]
custom_services: []             # runtime services outside the main app
custom_modules: []              # code-level module boundaries within the app
protocols: []                   # e.g. [http, trpc, websocket]
external_integrations: []       # third-party APIs, services
last_updated: YYYY-MM-DD
---
```

Body: one section per addition, in the frontmatter order. Prose and diagrams, no code.

- A custom module names its purpose, what it depends on and the feature that asked for it.
- A protocol names its endpoints, message types, connection lifecycle and error behaviour.
- An external integration names the API or SDK, what data crosses the boundary, the retry and fallback behaviour and where the credentials live — left out here, these get invented differently in every slice that touches the integration.
- `## External Integrations` is the only place in `_concept/` that records third-party services (payments, mail and SMS, file storage, analytics, error tracking, auth providers beyond the template's own).
- An empty frontmatter list is a real result: say in the body that the stack covers this project as it stands instead of inflating four sections.

## Writing it

1. **Read the stack first, so you write the delta.** `_concept/10_blueprint/techstack.md` names `tech_stack_skill`; that template's `## Identity` and `## Scaffold Recipe` say what the project already gets — server runtime, ORM, auth provider, directory structure. Then read `_concept/brief.md` and every feature under `_concept/05_features/`.
2. **Read the features for architecture signals**: real-time behaviour (chat, live updates, collaborative editing), background work (scheduling, long jobs, file processing), outside systems (payments, mail, third-party APIs), and data flows the stack has no shape for (event logs, multi-step workflows, pipelines). Where `_concept/06_behaviors/<featureset>.md` exists, its state tables sharpen all three: a transition on a timer is background work, one two actors race for is real-time, one that waits on an outside system names an adapter.
3. **Ask only what the features left open** (one question per message — `tree/README.md § How a skill runs`): background or scheduled work, live updates, external services, streaming or instant communication, non-standard data handling. A question the feature specs already answer spends the round you needed for a real one.
4. **Screen each addition against the design red flags** (below) before writing it; a module that fails the shallow-module question is usually a feature's helper, not an architecture entry.
5. **Give every outside dependency a seam.** A module the app does not own — payment gateway, mail sender, model provider — is declared as an interface with a real implementation and an in-memory stand-in behind it, chosen by configuration, so a slice can be built and tested before anyone has credentials.
6. **Write the file** per Format.
7. **Approve it in plain language**: what the structure lets the app do, which features get live updates and over what, what the custom logic is for in business terms, which outside services it depends on; the counts underneath. Approve, or name what to change.

### Design red flags

Ask each question of every candidate module, protocol and integration; a yes means reshape or drop it before anyone builds against it.

1. **Shallow module** — is the interface about as big as what it hides? *Fix:* merge it into its caller, or widen what it hides until the interface is small next to it.
2. **Information leakage** — is one representation decision (message format, file layout, retry policy, provider ID scheme) known in two places? *Fix:* give the decision one owner and route everyone else through it.
3. **Temporal decomposition** — is the split drawn by when things run (read, transform, write) rather than by what each piece hides? *Fix:* draw the boundary around a piece of knowledge and let one module run every step that needs it.
4. **Pass-through** — does a layer forward calls with the shape it received, adding no decision, translation or protection? *Fix:* remove the layer, or give it the job that justified it — usually the seam to an outside dependency.

**Design it twice.** When a module admits two plausible interfaces, write both as signatures (operations, inputs, returns) before choosing, and keep the deeper one: the one whose callers need to know less.

## Checks

- Every entry in the frontmatter lists is described in the body with its dependencies and its error behaviour.
- Third-party services appear here and not in `techstack.md`.
- The user approved the file.
