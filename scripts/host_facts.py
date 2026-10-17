#!/usr/bin/env python3
"""host_facts.py — the facts about other people's repos that `check.py` rests on.

About a dozen of `check.py`'s rules are copies of behaviour in `forge-concept` or
`@skaile/workspaces`. Until this table they were justified by comments naming a
`file:line`, and nothing re-checked them: ticket 40 measured 14 distinct refs and found
**4 rotted in roughly two weeks while every underlying fact still held**. A reference
that resolves to nothing quietly is this collection's own defect class, so the coupling
gets what every other reference here gets — one enumerable place, a date, and a test.

A row is one *fact*, not one rule: `profiles.get.ts` reading `meta.onboarding` backs
three rules, and the verifier greps facts. Each row carries

  id         `host:<slug>`, the token a rule cites via `rep.error(..., fact=...)`
  host       a key of `HOSTS`
  path       repo-relative, inside that host
  signature  a **grep-able token**, never a line number — a distinctive string
             survives a refactor and `:47` does not, which is what the measurement showed
  expect     `present` | `absent`; absence is first-class, because a host that *gains*
             a `${...}` resolver silently makes a ban wrong and nothing would say so
  claim      one sentence, the thing the rules actually depend on
  rules      the rule ids resting on it. Not prose: every `rep.error(..., fact=...)`
             site passes `rule=`, `Report.error` refuses an id this column does not
             list, and `test_check.py` reconciles both directions against `check.py`'s
             AST — so a fact no rule cites and a rule id no site uses both fail. A
             column only a human reads would rot exactly like the line numbers did
  verified   ISO date the signature was last confirmed by `verify_host.py`
  seen_at    **advisory output**, refreshed by `verify_host.py --update`. Never
             hand-maintained: line numbers are what rotted.

Nothing here is imported for its line numbers. `check.py` interpolates `path` into its
error text so a message cannot drift out of step with its row, and
`scripts/verify_host.py` greps the signatures against local checkouts.

No rule currently rests on `platform`; it stays in `HOSTS` because the collection is
installed there too and the next fact may be its.
"""
from __future__ import annotations

from dataclasses import dataclass

# Where each host sits relative to the super-repo root — `verify_host.py --hosts <root>`.
HOSTS = {
    "forge-concept": "forge/forge-concept",
    "skaile-forge": "forge/skaile-forge",
    "workspaces": "workspaces",
    "platform": "platform",
}

PRESENT = "present"
ABSENT = "absent"


@dataclass(frozen=True)
class Fact:
    id: str
    host: str
    path: str
    signature: str
    expect: str
    claim: str
    rules: tuple[str, ...]
    verified: str
    seen_at: str = ""

    @property
    def where(self) -> str:
        """The location as an error message should name it: host and path, no line."""
        return f"{self.host} `{self.path}`"


FACTS: tuple[Fact, ...] = (
    # -- @skaile/workspaces: installation, resolution, the flow loader ------------
    Fact(
        id="host:prerequisite-project-root",
        host="workspaces",
        path="packages/workspaces/resolver/src/validator.ts",
        signature="path.join(projectDir, req.path)",
        expect=PRESENT,
        claim="A declared prerequisite path is joined to the *project* root, never to the concept, so a concept path without the `_concept/` prefix resolves one level too high.",
        rules=("prerequisite-prefix", "prerequisite-path-resolves"),
        verified="2026-09-09",
        seen_at="L86",
    ),
    Fact(
        id="host:skill-metadata-nesting",
        host="workspaces",
        path="packages/workspaces/resolver/src/parser.ts",
        signature="const meta = fm.metadata ?? {};",
        expect=PRESENT,
        claim="`parseSkillRequirements` reads the machine layer only from `metadata:` and never falls back to the frontmatter root, so a root-level block parses clean and reports an unmet gate as satisfied.",
        rules=("machine-layer-nesting",),
        verified="2026-09-09",
        seen_at="L45",
    ),
    Fact(
        id="host:asset-name-slug",
        host="workspaces",
        path="packages/workspaces/core/src/models.ts",
        signature="export function slugifyAssetName(raw: string): string",
        expect=PRESENT,
        claim="An asset is indexed under its slugified `name:`, so `_` is not a legal identity character and a per-file `contract:` ref could never resolve.",
        rules=("contract-manifest-slug", "contract-asset-is-one", "requires-contract-per-file"),
        verified="2026-09-09",
        seen_at="L330",
    ),
    Fact(
        id="host:flow-asset-named-from-name",
        host="workspaces",
        path="packages/workspaces/core/src/manifest.ts",
        signature="slug = slugifyAssetName(e.name);",
        expect=PRESENT,
        claim="A flow's asset identity comes from its `name:`, not its `id:`, so a title that slugifies to something else installs under a name no `flow:` ref uses.",
        rules=("flow-name-slugifies-to-id",),
        verified="2026-09-09",
        seen_at="L932",
    ),
    Fact(
        id="host:flow-manifest-requires-name",
        host="workspaces",
        path="packages/workspaces/factory-assets/connectors/flow/engine/flow-manifest.ts",
        signature="name: z.string().min(1),",
        expect=PRESENT,
        claim="`FlowManifestSchema` requires a non-empty top-level `name:`, so a flow without one fails `validateFlow` wherever it is checked.",
        rules=("flow-name-present",),
        verified="2026-09-09",
        seen_at="L60",
    ),
    Fact(
        id="host:loader-discards-incomplete-flow",
        host="workspaces",
        path="packages/workspaces/factory-assets/connectors/flow/engine/loader.ts",
        signature="if (def.id && def.nodes && def.edges)",
        expect=PRESENT,
        claim="The loader keeps only flows carrying all three of id, nodes and edges — one missing key and the flow is dropped without an error.",
        rules=("flow-has-nodes",),
        verified="2026-09-09",
        seen_at="L148",
    ),
    Fact(
        id="host:doctor-walks-requires",
        host="workspaces",
        path="packages/workspaces/asset-manager/src/index.ts",
        signature="for (const req of full.requires)",
        expect=PRESENT,
        claim="`AssetManager.doctor()` walks a deployed asset's `requires` list, which is the one dependency declaration with a live reader in the shipped installer.",
        rules=("skill-declares-contract",),
        verified="2026-09-09",
        seen_at="L2620",
    ),
    # -- forge-concept: the onboarding card ---------------------------------------
    Fact(
        id="host:profile-description",
        host="forge-concept",
        path="server/api/pipeline/profiles.get.ts",
        signature='description: flow.description ?? ""',
        expect=PRESENT,
        claim="The onboarding card publishes a flow's `description:` verbatim and falls back to the empty string, so a missing one renders a blank card rather than an error.",
        rules=("flow-description",),
        verified="2026-09-09",
        seen_at="L31",
    ),
    Fact(
        id="host:profile-icon",
        host="forge-concept",
        path="server/api/pipeline/profiles.get.ts",
        signature='icon: meta?.icon ?? "i-heroicons-document-text"',
        expect=PRESENT,
        claim="`meta.icon` is passed straight to the icon component, which renders nothing for a name outside the `i-` prefixed Iconify set.",
        rules=("flow-icon",),
        verified="2026-09-09",
        seen_at="L32",
    ),
    Fact(
        id="host:profile-onboarding",
        host="forge-concept",
        path="server/api/pipeline/profiles.get.ts",
        signature="meta?.onboarding?.input_style",
        expect=PRESENT,
        claim="`meta.onboarding` is read here and its `input_style` is *cast* to the union without being checked, so an unknown value branches to nothing and a missing block leaves a structured form with no fields.",
        rules=("flow-meta", "onboarding-present", "onboarding-input-style", "onboarding-fields"),
        verified="2026-09-09",
        seen_at="L35",
    ),
    Fact(
        id="host:research-depth-seed",
        host="forge-concept",
        path="server/api/pipeline/profiles.get.ts",
        signature="flow.globals?.research_depth",
        expect=PRESENT,
        claim="`globals.research_depth` seeds the onboarding depth picker, defaulting to `moderate` when the block is missing.",
        rules=("flow-globals",),
        verified="2026-09-09",
        seen_at="L33",
    ),
    Fact(
        id="host:research-depth-options",
        host="forge-concept",
        path="server/api/pipeline/profiles.get.ts",
        signature='research_depth_options: ["skip", "light", "moderate", "deep"]',
        expect=PRESENT,
        claim="Exactly these four depths are published as selectable, so a value outside them is offered as a selected option the picker cannot show.",
        rules=("research-depth",),
        verified="2026-09-09",
        seen_at="L47",
    ),
    Fact(
        id="host:onboarding-placeholder-freeform",
        host="forge-concept",
        path="app/components/OnboardingWizard.vue",
        signature=':placeholder="currentPlaceholder"',
        expect=PRESENT,
        claim="The profile's placeholder is bound to the freeform textarea only, so it has no reader under any other `input_style`.",
        rules=("onboarding-placeholder",),
        verified="2026-09-09",
        seen_at="L94",
    ),
    # -- forge-concept: running a node --------------------------------------------
    Fact(
        id="host:skill-identity-is-the-directory",
        host="forge-concept",
        path="server/api/flows/nodes/[nodeId]/run.post.ts",
        signature="const skillId = node.data?.skill ?? node.id;",
        expect=PRESENT,
        claim="A flow node resolves its skill through `data.skill` against the deployed directory and never reads the skill's `name:`, so a mismatch is invisible until the node runs with an empty prompt.",
        rules=("skill-name-matches-directory",),
        verified="2026-09-09",
        seen_at="L53",
    ),
    Fact(
        id="host:prompt-is-verbatim",
        host="forge-concept",
        path="server/api/flows/nodes/[nodeId]/run.post.ts",
        signature=r"replace(/\$\{",
        expect=ABSENT,
        claim="No `${...}` resolver runs on the flow-node run path — the skill body is concatenated into the prompt verbatim, so an interpolation reaches the model as its literal text. (The flow *connector* in @skaile/workspaces does resolve `${}`; forge-concept does not call it, which is why this fact is scoped to this file.)",
        rules=("no-interpolation",),
        verified="2026-09-09",
        seen_at="",
    ),
    Fact(
        id="host:flow-edge-orders-run",
        host="forge-concept",
        path="server/api/flows/nodes/[nodeId]/run.post.ts",
        signature='e.target === nodeId && e.type === "flow"',
        expect=PRESENT,
        claim="Handoff context is gathered along `type: flow` edges and nothing else, so a differently-typed edge draws on the canvas and carries nothing.",
        rules=("edge-type-flow",),
        verified="2026-09-09",
        seen_at="L62",
    ),
    Fact(
        id="host:flow-edge-gates-state",
        host="forge-concept",
        path="server/utils/flow-extended-state.ts",
        signature='e.type === "flow" && !satisfied(e.source)',
        expect=PRESENT,
        claim="Node readiness is computed over `type: flow` edges only, so an edge of any other type orders nothing.",
        rules=("edge-type-flow",),
        verified="2026-09-09",
        seen_at="L48",
    ),
    # -- forge-concept: phases, lanes, dead keys ----------------------------------
    Fact(
        id="host:phase-lane-vocabulary",
        host="forge-concept",
        path="shared/flow-phases.ts",
        signature='export const PHASE_ORDER: Phase[] = ["conceptualization", "implementation", "review"];',
        expect=PRESENT,
        claim="These three are the whole lane vocabulary; a `data.phase` outside them is swallowed silently rather than reported.",
        rules=("node-phase-enum",),
        verified="2026-09-09",
        seen_at="L10",
    ),
    Fact(
        id="host:phase-guessed-from-skill",
        host="forge-concept",
        path="shared/flow-phases.ts",
        signature="return phaseForSkill(node.data?.skill ?? node.id);",
        expect=PRESENT,
        claim="A flow node that declares no `data.phase` gets one guessed from its skill name's domain prefix, so the flow renders in a lane nobody authored.",
        rules=("node-phase-present",),
        verified="2026-09-09",
        seen_at="L41",
    ),
    Fact(
        id="host:group-phase-wins",
        host="forge-concept",
        path="app/utils/flow-layout.ts",
        signature="(n.parentNode && groupPhase.get(n.parentNode)) || phaseForNode(n)",
        expect=PRESENT,
        claim="A group's phase overrides its children's, which is the only reason group nodes are worth carrying — and why a flow node's own `data.phase` can be silently ignored.",
        rules=("group-nodes-per-phase", "node-phase-agrees-with-group", "skill-node-parent"),
        verified="2026-09-09",
        seen_at="L93",
    ),
    Fact(
        id="host:positioned-nodes-lose-lanes",
        host="forge-concept",
        path="app/utils/flow-layout.ts",
        signature="if (unpositioned.length === 0) return { positions, lanes: [], width: 0 };",
        expect=PRESENT,
        claim="Positioned flow nodes are dropped from the lane computation and a fully positioned flow returns `lanes: []`, so authoring geometry costs the phase swimlanes.",
        rules=("node-position",),
        verified="2026-09-09",
        seen_at="L64",
    ),
    Fact(
        id="host:node-writes-legacy-read",
        host="forge-concept",
        path="server/utils/flow-manager.ts",
        signature="flowNode?.data?.writes as string | null",
        expect=PRESENT,
        claim="`data.writes` is still read for legacy flows when resolving a flow node's concept folder, so a stray block steers the explorer rather than being inert.",
        rules=("node-data-writes",),
        verified="2026-09-09",
        seen_at="L361, L508",
    ),
    Fact(
        id="host:sub-flow-parameters-read",
        host="forge-concept",
        path="shared/flow-extended.ts",
        signature="n.data?.parameters?.flow",
        expect=PRESENT,
        claim="`data.parameters.flow` is the one live read of `data.parameters` host-wide — a sub-flow node's child id — so a stray block is not inert either.",
        rules=("node-data-parameters",),
        verified="2026-09-09",
        seen_at="L52",
    ),
    # -- skaile-forge: the dialog input file ---------------------------------------
    Fact(
        id="host:grounding-user-input",
        host="skaile-forge",
        path="server/utils/content.ts",
        signature='join(stepFolder, "user_input.json")',
        expect=PRESENT,
        claim="The host saves each step's dialog input to `<conceptDir>/_grounding/<step>/user_input.json`, a path it hardcodes and no skill's frontmatter names, so only a step that reads it by that path ever sees what the user typed in the wizard.",
        rules=("onboard-names-host-input",),
        verified="2026-10-16",
        seen_at="L175",
    ),
    # -- skaile-forge: node done-state ---------------------------------------------
    Fact(
        id="host:node-done-from-produced-by",
        host="skaile-forge",
        path="server/utils/artifact-contract.ts",
        signature="const canonical = producedBy[0];",
        expect=PRESENT,
        claim="The editor marks a flow node done by mapping its skill to the artifact whose first `produced_by` entry names it in `contracts/artifacts.yaml`, a registry this collection no longer ships, so each skill's `metadata.artifacts.produces` list is the declaration that read has to switch to (ADR 0013).",
        rules=("produces-shape",),
        verified="2026-10-16",
        seen_at="L152",
    ),
)


BY_ID: dict[str, Fact] = {f.id: f for f in FACTS}


def fact(fact_id: str) -> Fact:
    """The row `fact_id` names. Raises rather than returning a default: an unknown id in
    an error message is the dangling reference this whole table exists to make loud."""
    try:
        return BY_ID[fact_id]
    except KeyError:
        raise KeyError(f"no host fact {fact_id!r} — add a row to scripts/host_facts.py") from None

