---
path: _concept/10_blueprint/architecture.md
summary: C4 levels — system context, containers, components, deployment, risks
owner: [architecture-system]
may_propose: []
---

# _concept/10_blueprint/architecture.md

The apps, custom modules, communication protocols and external integrations this project adds beyond its template, and nothing else, organised by the levels of the [C4 model](https://c4model.com/). What the chosen stack already provides is written once, in `templates/<tech_stack_skill>/TEMPLATE.md`; restating it here produces a second copy that drifts. The artifact is optional by design: a project whose features need nothing beyond its stack gets a short document saying exactly that, which is the answer `build-plan` needs. `architecture-datamodel` reads it for the entities a module implies, `build-plan` for the work a slice crosses, `build-implement` for what to build against. The HTTP and message contracts that sit beside it are `tree/10_blueprint/openapi.md` and `tree/10_blueprint/asyncapi.md`.

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

Body: these sections, in this order, each holding only what its name says. Prose and diagrams, no code. An empty frontmatter list is a real result: say in the body that the stack covers this project as it stands instead of inflating sections to look complete.

### System context

Who uses the system and which outside systems it talks to. Its `### External Integrations` subsection is the only place in `_concept/` that records third-party services (payments, mail and SMS, file storage, analytics, error tracking, auth providers beyond the template's own); `techstack.md` carries none. An integration names the API or SDK, what data crosses the boundary, the retry and fallback behaviour and where the credentials live — left out here, these get invented differently in every slice that touches the integration.

### Containers

The `apps`, `custom_services` and `protocols`: what runs separately and how the parts talk. A protocol names its endpoints, message types, connection lifecycle and error behaviour.

### Components

The `custom_modules`, written only where a container's insides matter; the section is left out when no module earns one. A module names its purpose, what it depends on and the feature that asked for it.

### Deployment

Where each container runs, as far as the stack and the features fix it.

### Risks and technical debt

What is known to be weak or deferred, each item with the feature or integration it touches.

## Writing it

1. **Resolve the stack first, so you write the delta.** `_concept/10_blueprint/techstack.md` names `tech_stack_skill`; that template's `## Identity` and `## Scaffold Recipe` say what the project already gets — server runtime, ORM, auth provider, directory structure. Then read `_concept/brief.md`, every feature under `_concept/05_features/` and, when it exists, `_concept/10_blueprint/datamodel/` (a soft input: the entities the payloads of step 7 name). Every one of these is read when it exists and derived or asked when it does not (`tree/README.md § How a skill runs`, rule 1): a stack the code already holds comes from `concept-reverse` scoped `stack` (`_concept/02_grounding/findings/stack.md`), features and endpoints from the same skill scoped `routes`, and what neither settles goes into step 3's batch. A stack the user names in that batch without a `techstack.md` behind it is `architecture-techstack`'s to record.
2. **Read the features for architecture signals**: real-time behaviour (chat, live updates, collaborative editing), background work (scheduling, long jobs, file processing), outside systems (payments, mail, third-party APIs), and data flows the stack has no shape for (event logs, multi-step workflows, pipelines). Where `_concept/06_behaviors/<featureset>.md` exists, its state tables sharpen all three: a transition on a timer is background work, one two actors race for is real-time, one that waits on an outside system names an adapter.
3. **Ask only what the features left open** (one decision batch per message — `tree/README.md § How a skill runs`): background or scheduled work, live updates, external services, streaming or instant communication, non-standard data handling. A question the feature specs already answer spends the round you needed for a real one.
4. **Screen each addition against the design red flags** (below) before writing it; a module that fails the shallow-module question is usually a feature's helper, not an architecture entry.
5. **Give every outside dependency a seam.** A module the app does not own — payment gateway, mail sender, model provider — is declared as an interface with a real implementation and an in-memory stand-in behind it, chosen by configuration, so a slice can be built and tested before anyone has credentials.
6. **Write `architecture.md`** per `## Format`: the frontmatter lists, then the five sections in order.
7. **Write the API and event contracts where the project has them.** An HTTP API served to clients other than the project's own UI — always for project type `api-service` — gets `_concept/10_blueprint/openapi.yaml` per `tree/10_blueprint/openapi.md`. A project that publishes or consumes messages on a channel — a broker, a websocket, a webhook stream — gets `_concept/10_blueprint/asyncapi.yaml` per `tree/10_blueprint/asyncapi.md`. A project with neither writes neither file; the stack already covers it, and the body of `architecture.md` says so. Payload schemas name entities from `_concept/10_blueprint/datamodel/model.json`, read and never coined; where that file does not exist they come from the glossary (`tree/glossary.md § Where the words live`), and a payload concept with neither becomes a `proposed` term, filed per `tree/glossary.md § Where the words live`, that the schema is named for. Each error response and each failed message names what the caller sees, which is the behaviour step 2 read in prose.
8. **Approve it in plain language**: what the structure lets the app do, which features get live updates and over what, what the custom logic is for in business terms, which outside services it depends on and, where step 7 wrote a contract, which endpoints or channels outside parties can rely on. The counts — apps, modules, protocols, integrations, endpoints, channels — go underneath. Approve, or name what to change; the contracts are approved with `architecture.md`, not separately.

### Changing a contract

`quality-e2e` reads `openapi.yaml`; `build-scaffold` and `build-implement` read both contract files; all three gate on them softly. An endpoint, a channel or a payload that a reader needs changed belongs to `architecture-system`: the reader names the change, steps 6–8 re-run for the affected parts, and the reader never edits `openapi.yaml` or `asyncapi.yaml` itself.

### Design red flags

Ask each question of every candidate module, protocol and integration; a yes means reshape or drop it before anyone builds against it.

1. **Shallow module** — is the interface about as big as what it hides? *Fix:* merge it into its caller, or widen what it hides until the interface is small next to it.
2. **Information leakage** — is one representation decision (message format, file layout, retry policy, provider ID scheme) known in two places? *Fix:* give the decision one owner and route everyone else through it.
3. **Temporal decomposition** — is the split drawn by when things run (read, transform, write) rather than by what each piece hides? *Fix:* draw the boundary around a piece of knowledge and let one module run every step that needs it.
4. **Pass-through** — does a layer forward calls with the shape it received, adding no decision, translation or protection? *Fix:* remove the layer, or give it the job that justified it — usually the seam to an outside dependency.

**Design it twice.** When a module admits two plausible interfaces, write both as signatures (operations, inputs, returns) before choosing, and keep the deeper one: the one whose callers need to know less.

## Checks

- Every entry in the frontmatter lists is described in the body with its dependencies and its error behaviour, under the C4 section its name says.
- Third-party services appear under `System context` and not in `techstack.md`.
- `openapi.yaml` and `asyncapi.yaml` exist exactly where step 7 says they are due.
- The user approved `architecture.md` and any contract together.
