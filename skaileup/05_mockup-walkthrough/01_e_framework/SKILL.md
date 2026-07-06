---
name: mockup-walkthrough-framework
description: "Use when stakeholders need the highest-fidelity clickable walkthrough rendered in the project's CHOSEN stack framework (Next.js / Nuxt / SvelteKit), resolved from the selected scaffold template. Generates a stack-native built site — one route/page per screen and per journey, plus a manifest.json that the mockup-feedback cluster reads. Best for appbuilder-complex tier."
metadata:
  version: "0.2.0"
  tags:
    - walkthrough
    - mockup
    - framework
    - stack-native
    - appbuilder-complex
    - frontend
    - prototype
    - data-spec
  stage: alpha
  artifacts:
    requires:
      - id: screens
        gate: hard
      - id: journeys
        gate: hard
      - id: brand-tokens
        gate: hard
      - id: techstack
        gate: hard
    consumes:
      - id: features
        gate: soft
    produces:
      - id: walkthrough
  prerequisites:
    files:
      - path: "experience/screens"
        gate: hard
        description: "Screen specs are the primary input — one page/route rendered per screen"
        min_entries: 1
      - path: "experience/journeys/stories.yaml"
        gate: hard
        description: "Journey definitions drive the journey/<id> route sequencing"
      - path: "design/tokens.json"
        gate: hard
        description: "Brand tokens injected as CSS vars in the built shell"
      - path: "_concept/blueprint/techstack.md"
        gate: hard
        description: "Frontmatter tech_stack_skill must resolve to a concrete template-* id — names the framework to render. If still abstract, run impl-architecture-templates-select first"
      - path: "experience/features"
        gate: soft
        description: "Feature files linked from manifest.json for traceability; absence is a warning"
        min_entries: 1
    reads:
      - path: "experience/screens/00_layout/shell.md"
        description: "Optional shared layout reference; if present, used as reference for the framework's root layout wrapper"
      - path: "09_impl-architecture/templates/<tech_stack_skill>/TEMPLATE.md"
        description: "Resolved scaffold template — learns the framework, scaffold/dev/build commands, and routing conventions"
  produces:
    - path: "_concept/mockup-walkthrough/framework"
      description: "Stack-native framework project source + built site: index, screen/<group>/<name>, journey/<id> routes, manifest.json"
---

# Walkthrough Mockup — Framework (stack-native)

## Overview

Highest-fidelity variant of walkthrough mockup cluster, used by
**appbuilder-complex** tier. Consumes same four inputs as
`mockup-walkthrough-static-html` (screen specs, journey definitions, brand
tokens, feature files) PLUS one more — `_concept/blueprint/techstack.md` —
produces built site rendered in **project's chosen framework**
(Next.js / Nuxt / SvelteKit) at `_concept/mockup-walkthrough/framework/`.

Framework is not fixed: resolved from `tech_stack_skill` field in
`techstack.md`, which names exactly one concrete scaffold template under
`09_impl-architecture/templates/template-*/`. That template's `TEMPLATE.md`
is authority for which framework to scaffold, its scaffold/dev/build
commands, its routing conventions. This makes framework walkthrough a true
preview of production stack — it doubles as seed of real application shell.

Every rendered DOM node carries same `data-spec-*` attributes as static-html
and astro variants so `mockup-feedback-*` cluster resolves clicks
identically across renderers. `manifest.json` schema is identical — only
`renderer: "mockup-walkthrough-framework"` and added `target_framework`
field differ.

**Two-mode behaviour — decision recorded.** Agent detects whether framework
project already exists by checking for
`_concept/mockup-walkthrough/framework/package.json`:

- **Init** (absent): resolve framework → scaffold minimal app in resolved
  framework using template's conventions → generate `specs.json` + token
  styles → install → build → write `manifest.json`
- **Update** (present): regenerate `specs.json` + token styles only →
  rebuild → rewrite `manifest.json`

On update runs, agent NEVER touches framework's config files
(`next.config.*`, `nuxt.config.*`, `svelte.config.*`, `package.json`) or
user-owned page/route templates — those belong to user.

**Generation approach — decision recorded.** Agent-direct: agent reads
screen specs, derives `specs.json` inline (no persistent generator script).
Same pattern as static-html's Python renderer and astro's inline derivation.

## Renderer Contract

**Public contract.** Every `data-spec-*` attribute MUST be emitted on same
DOM position as `mockup-walkthrough-static-html` so `mockup-feedback-*`
cluster resolves clicks identically across renderers — **regardless of
underlying framework.** If resolved framework uses client components /
islands / hydration, built (SSR/SSG) HTML MUST still carry `data-spec-*`
attributes server-side, so static fetch of built page resolves every
attribute without running JavaScript. *(This is the existing "data-spec-*
server-side" invariant this SKILL.md has always pinned — see below for its
extension to `href` resolution.)*

Implements shared walkthrough renderer contract — `contracts/walkthrough_renderer.md`
(schema_version "1.2"): data-spec-* attribute table, screen_id vs screen_path,
kind → DOM tag mapping (incl. `target` resolution, `table`, `tabs`, populated
`list`/`select`), § Target resolution, § App-shell navigation, § Auto-slug
fallback (narrowed source set), § Spec reference panel, manifest schema +
field semantics, warnings[].kind enum, shared error handling,
screen-in-multiple-journeys rule, shared MUST/NEVER. Read before rendering;
pinned, MUST NOT be restated here.

Renderer-specific manifest values: `renderer: "mockup-walkthrough-framework"`,
`renderer_version:` this SKILL.md's `metadata.version`.

Framework-specific: resolved framework's templates emit
`data-spec-provisional="true"` where `element.provisional === true`; NO
separate top-level `auto_slugged[]` array — `provisional: true` lives on
element object.

**Framework-specific corollary of the contract (not a deviation from it): all
target/content resolution happens in STEP 3, not in the route template.**
Same architectural constraint astro's and lit's renderers document, for the
same reason: whichever route/page file resolved framework's routing
convention scaffolds for the screen collection (`src/app/screen/[...slug]/page.tsx`
for Next.js, `pages/screen/[...slug].vue` for Nuxt, `src/routes/screen/[...slug]/+page.svelte`
for SvelteKit) is scaffolded **once** at project-init time (§ Two-mode
behaviour above) and is **never** rewritten on update runs — so every value
that route file's render logic would otherwise need to *resolve* (a
`target:` → href, an auto-slugged item's derived id, the spec panel's
rendered body, the app-nav's grouped shape) MUST already be sitting
fully-resolved in `specs.json` before that route file ever runs. Framework
route templates only interpolate a pre-resolved `href` string (`el.href ??
'#'`, or the framework-native equivalent); they never derive one. See §
`specs.json` shape and STEP 3 below.

**Framework-native link components are acceptable — with one condition.**
`next/link`, `NuxtLink`, and SvelteKit's plain `<a>` are all legitimate ways
to render a resolved `href` inside a route template (and are, in fact, the
idiomatic choice for each framework over a bare `<a>`) — **as long as the
built static HTML the framework emits (SSG/SSR output) contains a plain,
resolvable `href` attribute server-side**, per the existing "data-spec-*
server-side" invariant above extended to cover hrefs too: a client-only
router that only wires up navigation after hydration would leave the built
HTML's anchor without a real `href`, which breaks both the "openable
without JavaScript" acceptance criterion and `mockup-feedback-*`'s ability
to resolve a click to a target file from the static DOM alone. Concretely:
`<Link href={el.href}>{el.label}</Link>` is fine when Next.js's SSG output
renders that to `<a href="/screen/...">…</a>` in the built HTML; a component
that defers the `href` to client-side JS is not.

Framework's root layout (`<root layout / shell>` in the project layout
table above) renders `specs.app_nav` — as a `<nav class="app-nav">` sibling
placed after the header and before the main content slot, on **screen
pages only** (index and journey pages do not receive the `appNav` prop/slot
— same precedent astro's `Shell.astro` and lit's `renderAppNav()` already
established: "the generated nav renders only inside a screen's shell
wrapper"). See § App-shell navigation (STEP 3) and § `specs.json` shape
below for its exact shape.

## Inputs

Same four input shapes as `mockup-walkthrough-static-html`, plus techstack
gate:

| Path | Shape |
|---|---|
| `experience/screens/<group>/<screen>.md` | Markdown + YAML frontmatter with optional `elements:` block per `contracts/elements_block.md` |
| `experience/journeys/stories.yaml` | JSON `{ "journeys": [{ "id", "title", "description", "screen_sequence" }] }` |
| `design/tokens.json` | Token tree. Flattened to CSS custom properties (`--token-<dotted-path-with-hyphens>`). |
| `experience/features/<group>/<feature>.md` | Used only for `manifest.json#features`; not rendered as HTML. |
| `_concept/blueprint/techstack.md` | Frontmatter `tech_stack_skill` resolves the framework; the template's `TEMPLATE.md` supplies scaffold/build conventions. |

## Outputs

Generated under `_concept/mockup-walkthrough/framework/`:

| Path | Description |
|---|---|
| `<built index page>` | Router/menu — `<body data-spec-index="true">`. Lists every screen and journey. |
| `screen/<group>/<name>` (built) | One built page per screen. `<body data-spec-screen="<screen_id>">`. |
| `journey/<id>` (built) | One built page per journey. `<body data-spec-journey="<id>">`. Walks through screens in order. |
| `manifest.json` | Machine-readable index for `mockup-feedback-annotate`. |
| `package.json` + `dev`/`build`/`preview` scripts | So any developer can run the walkthrough — the skill itself does not auto-serve. |

> Exact built-output layout (e.g. `out/`, `.output/public/`, `build/`)
> depends on resolved framework's static build target. Validator is pointed
> at project root, discovers built HTML; `rendered_html` paths in
> `manifest.json` recorded relative to that project root.

## Framework project layout (framework-agnostic)

Project lays out one root layout/shell, one index page, one
screen-collection route, one journey-collection route, plus agent-managed
data file and stylesheet. Concrete file names follow resolved template's
routing convention.

```
_concept/mockup-walkthrough/framework/      ← project root (committed)
├── <data>/specs.json                       ← regenerated each run (agent-managed)
├── <styles>/global.css                     ← token vars (regenerated each run, agent-managed)
├── <root layout / shell>                   ← token-driven wrapper (scaffolded once)
├── <index page>                            ← site root, data-spec-index="true"
├── <screen collection route>               ← one route → all screens (catch-all slug)
├── <journey collection route>              ← one route → all journeys (id param)
├── <framework config>                      ← next.config.* | nuxt.config.* | svelte.config.* (scaffolded once)
├── package.json                            ← dev/build/preview scripts (scaffolded once)
└── manifest.json                           ← written after build, not by the framework
```

### Next.js (App Router) example

```
_concept/mockup-walkthrough/framework/
├── src/app/layout.tsx                       ← root layout (token CSS import, body data-spec passthrough)
├── src/app/page.tsx                         ← index, <body data-spec-index="true">
├── src/app/screen/[...slug]/page.tsx        ← generateStaticParams → all screens
├── src/app/journey/[id]/page.tsx            ← generateStaticParams → all journeys
├── src/data/specs.json                      ← regenerated each run
├── src/app/globals.css                      ← :root token vars (regenerated each run)
├── next.config.ts                           ← output: 'export' (static), scaffolded once
└── package.json
```

`src/app/page.tsx` sets `data-spec-index="true"` on document body; screen
route's `generateStaticParams()` returns one entry per `specs.screens[]`
with `slug = screen_id.split('/')`; journey route's
`generateStaticParams()` returns one entry per `specs.journeys[]` keyed by
`journey_id`. Each page's root element (or layout's `<body>`) carries
`data-spec-*` marker, and `next.config.ts` sets `output: 'export'` so build
emits static HTML carrying attributes server-side.

### Nuxt / SvelteKit equivalents

Follow resolved template's routing convention:

- **Nuxt** — `pages/index.vue`, `pages/screen/[...slug].vue`,
  `pages/journey/[id].vue`; `nuxt.config.ts` with `nitro.prerender` /
  `ssr: true` so routes prerendered to static HTML. `definePageMeta` or
  wrapping `<body>` attribute carries `data-spec-*` markers.
- **SvelteKit** — `src/routes/+page.svelte`,
  `src/routes/screen/[...slug]/+page.svelte`,
  `src/routes/journey/[id]/+page.svelte` with `+page.server.ts`
  `entries()` for prerender; `@sveltejs/adapter-static` so build emits
  static HTML. `<svelte:body>` / element attributes carry markers.

In every case, **built HTML must carry `data-spec-*` server-side** — see
Renderer Contract.

## `specs.json` shape

`specs.json` bridges source artefacts to the framework templates at build
time. Same architectural role as astro's and lit's `specs.json` (§ Renderer
Contract above: templates only interpolate, they never resolve) — every
value a route template would otherwise need to *resolve* — a `target:`
href, an item's derived id, a screen's rendered spec body, the app-nav's
grouped shape — is pre-resolved here.

**Href scheme.** Framework's routes are real, framework-routed pages (`/`,
`/screen/<screen_id>`, `/journey/<journey_id>`), not standalone files opened
via `file://` — so this renderer follows **astro's root-relative,
extension-less scheme**, not static-html's/lit's relative `../<group>/<name>.html`
file scheme: a resolved target `gB/nB` gets `href: "/screen/gB/nB"` (+
`#<fragment>` when present); the generated app-nav's per-screen links use
the same form. This matches the routing convention already shown in the
Next.js/Nuxt/SvelteKit examples above (`[...slug]` / `[id]` dynamic routes,
not per-screen static files).

```json
{
  "app_nav": [
    {
      "label": "login",
      "href": "/screen/00_auth/login",
      "source": "derived"
    }
  ],
  "screens": [
    {
      "screen_id": "01_user_auth/login",
      "screen_path": "experience/screens/01_user_auth/login.md",
      "rendered_html": "screen/01_user_auth/login.html",
      "group": "01_user_auth",
      "title": "Login",
      "implements": ["experience/features/01_user_auth/login.md"],
      "data_entities": ["User"],
      "layout": "experience/screens/00_layout/shell.md",
      "body_html": "<p>Intro prose…</p><h3>Purpose</h3><p>…</p>",
      "elements": [
        {
          "element_id": "submit-button",
          "kind": "button",
          "label": "Sign in",
          "states": ["default", "loading"],
          "provisional": false,
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/submit-button"
        },
        {
          "element_id": "go-register",
          "kind": "link",
          "label": "Create an account",
          "states": ["default"],
          "provisional": false,
          "target": "01_user_auth/register",
          "href": "/screen/01_user_auth/register",
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/go-register"
        },
        {
          "element_id": "recent-signins",
          "kind": "table",
          "label": "Recent sign-ins",
          "states": ["default"],
          "provisional": false,
          "columns": ["Name", "Email"],
          "sample_rows": [["Lena M.", "lena@example.com"]],
          "row_target": "01_user_auth/verify_email",
          "row_href": "/screen/01_user_auth/verify_email",
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/recent-signins"
        },
        {
          "element_id": "signup-benefits",
          "kind": "list",
          "label": "Why join",
          "states": ["default"],
          "provisional": false,
          "items": [
            {
              "label": "See your login screen",
              "target": "01_user_auth/login",
              "href": "/screen/01_user_auth/login",
              "element_id": "see-your-login-screen",
              "provisional": true
            },
            {
              "label": "Get onboarding tips",
              "element_id": "get-onboarding-tips",
              "provisional": true
            }
          ],
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/signup-benefits"
        }
      ],
      "journeys": ["user-signs-in"]
    }
  ],
  "journeys": [
    {
      "journey_id": "user-signs-in",
      "title": "User signs in",
      "description": "First-time user authenticates.",
      "rendered_html": "journey/user-signs-in.html",
      "source": "experience/journeys/stories.yaml#user-signs-in",
      "screen_sequence": ["01_user_auth/login", "02_dashboard/home"]
    }
  ],
  "token_vars": {
    "--token-color-primary": "#0ea5e9",
    "--token-spacing-sm": "8px"
  },
  "features": [
    {
      "feature_path": "experience/features/01_user_auth/login.md",
      "rendered_screens": ["experience/screens/01_user_auth/login.md"]
    }
  ]
}
```

Every `items[]` entry (whether the schema's bare-string shorthand or the
`{label, target?}` dict form) is normalised in `specs.json` to always carry
its own resolved `element_id` and `provisional` — this is the § Auto-slug
fallback "items[] id derivation" rule (see STEP 3 below) executed once at
generation time so the route template never has to re-derive it. `href` is
present on an item only when the item declares a `target`.

**specs.json → manifest.json projection.** `specs.json` carries
template-convenience fields that MUST NOT be copied to `manifest.json`:
- `screens[].title`, `screens[].group`, `screens[].journeys[]`, `screens[].body_html`
- `screens[].elements[].href`, `screens[].elements[].row_href`
- `screens[].elements[].items[].element_id`, `screens[].elements[].items[].provisional`, `screens[].elements[].items[].href`
- `journeys[].title`, `journeys[].description`
- `app_nav[].href` (manifest's `app_nav[].target` carries the same resolved value, under the pinned field name — see § Manifest schema)

Build `manifest.json` from the in-memory model using the pinned shape
directly (not by serialising `specs.json`) — this also means every
`manifest.json#screens[].elements[].target` / `.row_target` /
`.items[].target` stays the **declared** `screen_id[#fragment]` value (per
`contracts/walkthrough_renderer.md` § Field semantics), never the resolved
`href` — only `specs.json` and the built HTML carry the resolved form.

## ROLE / READS / WRITES / REFERENCES

ROLE  Walkthrough stack-native renderer — resolves the project's chosen
      framework from techstack.md and converts screen specs + journey
      definitions + tokens into a built site in that framework whose DOM is
      annotatable end-to-end via the same data-spec-* contract as static-html.

READS
  _concept/blueprint/techstack.md       — frontmatter tech_stack_skill → framework
  09_impl-architecture/templates/<tech_stack_skill>/TEMPLATE.md — scaffold/build/routing
  experience/screens/**/*.md            — screen specs (frontmatter + body)
  experience/journeys/stories.yaml      — journey definitions
  design/tokens.json                    — brand tokens
  ? experience/features/**/*.md       — feature traceability (soft)
  ? experience/screens/00_layout/shell.md — shared layout reference (soft)
  ? _concept/mockup-walkthrough/framework/package.json — mode detection

WRITES
  _concept/mockup-walkthrough/framework/<data>/specs.json        (every run)
  _concept/mockup-walkthrough/framework/<styles>/global.css      (every run)
  _concept/mockup-walkthrough/framework/<framework config>       (init only)
  _concept/mockup-walkthrough/framework/package.json             (init only)
  _concept/mockup-walkthrough/framework/<root layout>            (init only)
  _concept/mockup-walkthrough/framework/<index page>             (init only)
  _concept/mockup-walkthrough/framework/<screen route>           (init only)
  _concept/mockup-walkthrough/framework/<journey route>          (init only)
  _concept/mockup-walkthrough/framework/<built index page>       (built — every run)
  _concept/mockup-walkthrough/framework/screen/<group>/<name>    (built — every run)
  _concept/mockup-walkthrough/framework/journey/<id>             (built — every run)
  _concept/mockup-walkthrough/framework/manifest.json            (every run)

REFERENCES
  contracts/walkthrough_renderer.md     — shared renderer contract (pinned)
  contracts/elements_block.md           — elements: schema + renderer contract
  contracts/frontmatter.md              — screen + feature + stories shapes
  contracts/asset_frontmatter.md        — this SKILL.md's own frontmatter shape
  contracts/skill_grammar.md            — DSL keywords used in this body
  contracts/iron_laws.md                — non-negotiable cross-skill constraints
  contracts/scripts/validator_lib.py    — used by mockup-walkthrough/framework/validator.py
  09_impl-architecture/templates/DOMAIN.md — the template cluster + naming exception
  09_impl-architecture/02_templates-select/SKILL.md — resolves tech_stack_skill to a template-* id
  docs/devlog/mockup-design.md § 4, § 6, § 10     — shared input contract + hybrid ID strategy + deployability
  mockup-walkthrough/static-html/SKILL.md — sibling skill (contract anchor)
  mockup-walkthrough/astro/SKILL.md     — sibling skill (structural anchor; href scheme precedent)
  mockup-walkthrough/lit/SKILL.md       — sibling skill (scaffold-once/pre-resolve precedent)

## STEP 1: Read feedback devlog (preserved intent)

- If `_concept/_feedback/devlog.md` exists, read it.
- Filter entries where `target_paths` overlaps files under
  `_concept/mockup-walkthrough/framework/`.
- For each matching entry: extract `patch_summary` as a preserved-intent constraint.
  Do not undo these during regeneration.
- If no devlog or no matching entries: proceed with no constraints.

## STEP 2: Resolve framework

Key differentiator from astro/static-html renderers. Framework isn't fixed
— read from project's stack decision.

- Read `_concept/blueprint/techstack.md` frontmatter. Extract
  `tech_stack_skill`.
- Resolve against `09_impl-architecture/templates/<tech_stack_skill>/`:
  - **If `tech_stack_skill` is unset, abstract (e.g. `nextjs`, `nuxt`),
    or `custom`** — it is NOT a real `template-*` directory. HARD-FAIL with:
    > "tech_stack_skill is not resolved to a concrete scaffold template. Run
    > `impl-architecture-templates-select` first to pick a template-* id,
    > then re-run this skill." Append `kind: "unresolved_template"` to
    > `warnings[]` (in the diagnostic, not a manifest — no manifest is
    > written on hard-fail). You MAY note that a static-html fallback exists
    > (the appbuilder-complex flow's `mock-static-fallback`) if the user wants a
    > walkthrough without resolving the template.
  - **If the directory does not exist on disk** — same hard-fail; the id is
    stale.
- Read `09_impl-architecture/templates/<tech_stack_skill>/TEMPLATE.md`. From
  its **Identity** table and **Scaffold Recipe** learn:
  - the framework (Next.js / Nuxt / SvelteKit) → derive `target_framework`
    (`nextjs` | `nuxt` | `sveltekit`)
  - the scaffold command, the package manager, and the dev/build commands
  - the routing convention (App Router catch-all, Nuxt `pages/`, SvelteKit
    `src/routes/`)
- Derive `target_framework` from the Identity table's Frontend value
  (Next.js → `nextjs`, Nuxt → `nuxt`, SvelteKit → `sveltekit`). This value
  is recorded in `manifest.json#target_framework`.

EMIT  [mockup-walkthrough-framework] checkpoint phase=framework_resolved tech_stack_skill=<id> target_framework=<value>

## STEP 3: Read inputs

Mirrors `mockup-walkthrough-static-html`'s STEP 2 (and `mockup-walkthrough-astro`'s
and `mockup-walkthrough-lit`'s STEP 2, which mirror it exactly) for parsing,
validation, target resolution, and auto-slug derivation — only the output
shape differs (an in-memory model that STEP 6 serialises to `specs.json`,
rather than strings substituted directly into a template).

- Glob `experience/screens/**/*.md` (excluding `00_layout/`); sort
  lexicographically by path. **Build the rendered-screen-id set first** (all
  `screen_id` values from this glob) before resolving any element's
  `target:` — every `target`/`row_target`/`items[].target` is validated
  against this set (§ Target resolution below); building it up front means
  resolution never depends on parse order.
- For each screen: parse YAML frontmatter (PyYAML); extract `implements[]`,
  `data_entities[]`, `layout`, `elements[]` (default `[]`). Capture the
  screen body markdown (needed for `body_html` below and for auto-slug
  discovery).
- Validate `elements[]` against `contracts/elements_block.md` (v0.3). If
  `lab/validate-elements-block/` available, delegate; otherwise apply these
  checks per element and emit `warnings[]` accordingly (render the node
  regardless — soft-fail always):
  - `kind` outside the v0.3 enum (`input, button, link, image, text,
    region, list, form, nav, media, custom, table, tabs`) → warning
    `kind: "unknown_element_kind"`, treat as `custom`.
  - `target` / `row_target` present → resolve against the rendered-screen-id
    set (§ Target resolution below); unresolved → `href: null` on the
    in-memory element (the route template falls back to `'#'`) +
    `kind: "unresolved_target"` warning. Resolved → set `href` / `row_href`
    to the framework-scheme resolved path (see § Target resolution). This is
    the only target-related check this renderer performs at render time —
    shape/grammar validation (malformed `screen_id`, `target` on a
    non-interactive kind, etc.) is `lab/validate-elements-block`'s job per
    the contract, not re-litigated here.
  - `columns` / `sample_rows` / `items` / `options` — parsed and carried
    verbatim into the in-memory model (§ Content fidelity); this renderer
    does not re-validate `sample_rows` row length against `columns` length
    — authoring-time validation owns that.

  > **Design note:** this renderer does NOT re-validate `elements:` block
  > schema shape — `sample_rows` row-length vs. `columns`, per-kind `items`
  > shape, or `target`/`screen_id` grammar. That's `lab/validate-elements-block`'s
  > job at authoring time. This renderer assumes schema-valid input and
  > handles only render-time semantics — target resolution success/failure,
  > reflected via `unresolved_target` warnings (see § Target resolution
  > below). Consistent with `contracts/walkthrough_renderer.md`'s
  > `warnings[].kind` enum, which has no length-mismatch or shape-mismatch
  > kind at all.

- **§ Target resolution** (`contracts/elements_block.md` § Navigation
  targets, `contracts/walkthrough_renderer.md` § Target resolution): a
  `target`/`row_target` value is `screen_id[#fragment]`. Strip the
  fragment; the target resolves iff the remaining `screen_id` is in the
  rendered-screen-id set built above. A resolved target `gB/nB` gets
  `href: "/screen/gB/nB"` (+ `#<fragment>` when present) — framework's
  root-relative, extension-less scheme (§ `specs.json` shape above), NOT
  static-html's/lit's `../<group>/<name>.html` file scheme. Unresolved →
  `href: null` (the route template renders `'#'`) + `unresolved_target`
  warning (declared-but-unresolved only; an absent `target:` is not an
  error, gets no warning, and the element simply has no `href` key).
- Parse `experience/screens/00_layout/shell.md` frontmatter, when the file
  exists, for an `elements:` entry with `kind: nav` and non-empty `items:`
  — this is the **shell-authoritative app nav** (§ App-shell navigation,
  used below). Absent file, absent `elements:`, absent `kind: nav` entry,
  or an entry with empty/absent `items:` — all fall through to the
  **derived-default** case.
- Read `experience/journeys/stories.yaml`. Validate each `journeys[]` entry
  has `id` AND `screen_sequence`. Missing `screen_sequence` → warning
  `kind: "missing_screen_sequence"`, skip that journey render.
- Read `design/tokens.json`. Flatten nested tree depth-first into flat dict
  keyed `--token-<dotted-path-with-hyphens>`. Example:
  `{"color": {"primary": "#0ea5e9"}}` → `--token-color-primary: #0ea5e9`.
- Glob `experience/features/**/*.md`; sort lexicographically. Build
  `feature -> screens[]` map by inverting `screens[].implements[]`.
- **Auto-slug source set** (`contracts/walkthrough_renderer.md` § Auto-slug
  fallback) — walked only when a screen's `elements:` is absent OR partial
  (i.e. for any widget not already covered by an explicit entry, matched by
  label-equality, case-insensitive):
  - (a) markdown `##`/`###` headings, **excluding** — case-insensitive —
    the canonical spec-template headings `Purpose`, `Route`, `What the
    User Sees`, `Wireframe`, `Information Displayed`, `Actions`,
    `Situations`, `UI Elements`, `Template Data`; the shell template's own
    `Navigation`, `Layout Areas`, `Responsive Behaviour`; and any
    `# Screen: *` / `# Shell: *` H1 (H1s are never scanned regardless —
    only `##`/`###` are widget sources). These excluded headings become
    the § Spec reference panel's `body_html` skeleton instead (see below)
    and are **never** rendered as `el-region` widgets. A screen's own
    non-canonical heading (e.g. a bespoke `## Notes`) stays in the
    discovery net and produces an inert `kind: text` element.
  - (b) form-field lines matching `[label]: input|button|...` pattern,
  - (c) acceptance-criteria mentions in body text,
  - (d) **`## Actions` bullets, label-extracted.** For each bullet: label
    = the first quoted token (`"…"` or `„…“`) when present; otherwise the
    clause preceding the first `→`, with a leading interaction verb
    (`Click`, `Change`, `Select`, `Switch`, `Drag`, `Pick`, `Open`,
    optionally preceded by an article) stripped, truncated to ≤ 40 chars.
    The bullet's full text becomes the synthesized element's `describes:`.
    Kind inference: a quoted token, or a `Click …` verb → `button`;
    `Change …` / `Select …` / `Pick …` → `input`; `Switch tab` → `tabs`
    (items sourced from bold/quoted tab names in `## What the User Sees`,
    or two placeholder items if none found).
  ID generation: kebab-case slug of the label; `<kind>-<n>` fallback when
  the label slugs to empty; `-2`/`-3`… suffix on collision;
  `auto_slug_collision` warning when colliding with an explicit id. Each
  auto-slugged element gets `provisional: true` and a `warnings[]` entry of
  `kind: "auto_slugged"`.

  > **`items[]` id derivation (`nav` / `tabs` / `list`, used by the
  > shell-authoritative app nav too).** `elements_block.md` leaves `id`
  > optional on `nav`/`tabs` items and doesn't define an `id` field on
  > `list` items at all — an id-less `items[]` entry is the normal case,
  > not an edge case. When an entry declares `id:`, use it verbatim
  > (`provisional: false`, no warning) on the normalised in-memory item.
  > When it does **not**:
  > 1. Derive an id via the same kebab-slug algorithm as top-level
  >    auto-slug, **scoped to that element's own `items[]`** — a collision
  >    suffix (`-2`/`-3`…) disambiguates only within the same element's
  >    items, never across the whole screen.
  > 2. Set the normalised item's `element_id` to the derived id and
  >    `provisional: true` — this is what the route template reads to emit
  >    `data-spec-element="<derived-id>"` and
  >    `data-spec-provisional="true"`, never re-deriving it itself.
  > 3. Append a `warnings[]` entry of `kind: "auto_slugged"` to the
  >    in-memory model (`element_id` = the derived item id, `screen_path` =
  >    this screen's path) — one entry per id-less item.
  >
  > This follows directly from `contracts/walkthrough_renderer.md`'s
  > `data-spec-*` attribute table, which names "list items, nav items"
  > explicitly as `data-spec-provisional`-eligible whenever "no explicit
  > `elements:` entry exists for it" — an id-less `items[]` entry has no
  > explicit entry establishing its own identity (it's derived from
  > `label`), exactly like a top-level auto-slugged widget. Every `items[]`
  > entry — whether it declared an explicit `id` or not — gets normalised
  > to carry `element_id`/`provisional` in the in-memory model /
  > `specs.json`, so the route template never branches on "did this come
  > with an id"; it just reads `item.element_id`.
  >
  > Every `items[].target` (dict-shaped entries only) is resolved exactly
  > like a top-level `target` (§ Target resolution above), yielding the
  > item's own `href`. A bare-string item, or a dict item with no
  > `target`, gets no `href` key (legal + inert, same as an untargeted
  > button).

- **Spec panel body** (`body_html`, consumed by the scaffolded root layout's
  `<details class="spec-panel">` block, per `contracts/walkthrough_renderer.md`
  § Spec reference panel) — computed once per screen, here, not at build
  time (§ Renderer Contract above explains why): render to an HTML fragment
  string = the screen body's top-level intro prose (any paragraph before the
  first `##`/`###` heading) **plus** every canonical section present
  (heading as `<h3>`, its content below) **plus** the `### Wireframe` fence
  verbatim as `<pre><code>…</code></pre>`. A screen's own non-canonical
  heading is **not** additionally duplicated here — it's already surfaced
  via auto-slug discovery (or an explicit element). HTML-escape every
  interpolated string per the shared MUST. No `data-spec-*` attribute of any
  kind belongs inside `body_html` — it's reference prose, not an annotatable
  surface.
  - **Zero explicit elements.** When the screen has no `elements:` at all
    (or an empty one) AND the auto-slug walk above discovers nothing
    either, record on the in-memory screen model that its spec panel MUST
    render `open` (the route template reads this off
    `screen.elements.filter(e => !e.provisional).length === 0`, so no
    separate boolean field is needed in `specs.json`) and emit a
    `warnings[]` entry of `kind: "no_explicit_elements"`.
- **§ App-shell navigation** (`contracts/walkthrough_renderer.md` § App-shell
  navigation) — build the `app_nav` in-memory model, one entry per
  generated/authoritative link, each already carrying its resolved `href`:
  - **Shell-authoritative case** (shell nav found above): one entry per
    `items[]` entry on the shell's `kind: nav` element, `label`/`href`
    resolved per § Target resolution, `element_id` per the **`items[]` id
    derivation** rule above, `source` = `"experience/screens/00_layout/shell.md"`.
  - **Derived-default case**: one entry per *rendered* screen (this
    walkthrough's screens, in the same lexicographic-by-`screen_path` order
    as the screens array — deterministic, no separate sort invented),
    grouped by `<group>` (the screen's directory segment; group label =
    dir name with its `NN_` prefix stripped and underscores replaced by
    spaces — e.g. `00_auth` → `auth`). `element_id: "app-nav"` on the
    whole generated nav, `provisional: true`; each per-screen entry gets
    `element_id: "app-nav-<n>"` (1-based, flat position across all
    groups), `provisional: true`, `label` = screen filename stem with
    underscores → spaces (e.g. `verify_email` → `verify email`), `href`
    resolved exactly like any other target. Emit **exactly one**
    `auto_slugged` `warnings[]` entry for the whole generated nav
    (`element_id: "app-nav"`, no `screen_path` key — it isn't owned by one
    screen), never one per link.
- Build normalised in-memory model:
  `{ screens: [{..., body_html, elements: [{..., href?, row_href?, items?:
  [{..., element_id, provisional, href?}]}]}], journeys, token_vars,
  features, app_nav, shell_nav: {...} | null, warnings }`.

### Edge cases

- **Malformed YAML** → fail loudly, exit non-zero, name the offending file.
- **Screen in journey but absent on disk** → `kind: "missing_screen"`,
  dead-end placeholder step (link present, class `journey-step-missing`).
- **`elements:` kind outside v0.3 enum** → render as `custom`,
  `kind: "unknown_element_kind"`.
- **`layout:` reference to non-existent file** → `kind: "missing_layout"`,
  fall back to the scaffolded root layout default.
- **`experience/features/` empty or missing** → soft gate,
  `kind: "missing_feature"`, continue. `manifest.features[]` → `[]`.
- **Zero journeys** → render "No journeys defined",
  `kind: "no_journeys"`.
- **`target`/`row_target`/`items[].target` declared but unresolved** →
  `href: null` on the in-memory model (route template renders `'#'`) +
  `kind: "unresolved_target"`; never hard-fail.

## STEP 4: Detect mode

Check `_concept/mockup-walkthrough/framework/package.json`.
- Absent → **Init** (proceed to STEP 5 then STEP 6).
- Present → **Update** (skip STEP 5, run the § `stale_scaffold` check below,
  then proceed directly to STEP 6).

### `stale_scaffold` check (update mode only)

Scaffolded route/page files (the screen-collection route, the root layout)
are never rewritten on update runs (§ Two-mode behaviour above) — so a
project scaffolded before this SKILL.md revision (or hand-edited since) may
be missing the resolved-`href` interpolation or the spec-panel block this
revision adds. Detect this **before** regenerating `specs.json` so the
warning reflects the scaffold as it stood at the start of the run:

- Resolve the screen-collection route file from `target_framework` (STEP 2):
  `src/app/screen/[...slug]/page.tsx` (Next.js), `pages/screen/[...slug].vue`
  (Nuxt), `src/routes/screen/[...slug]/+page.svelte` (SvelteKit).
- Read that file as text — same literal-substring check astro/lit run
  against their own scaffolded template. If it does **not** contain the
  literal substring `el.href`, OR does **not** contain the literal
  substring `spec-panel` → append a `warnings[]` entry of `kind:
  "stale_scaffold"` (`message: "<resolved route file> predates this
  renderer's target/content-fidelity revision (missing el.href and/or
  spec-panel) — delete the scaffold to let it regenerate, or port the
  template changes from this SKILL.md by hand."`).
- This is a warning, not a failure — the build still proceeds against the
  stale scaffold (whatever it renders is what ships); the warning exists so
  `mockup-feedback-annotate`/the user knows target/content fidelity may be
  incomplete on this project.

## STEP 5: Scaffold project (Init only)

Scaffold minimal app in resolved framework using template's conventions.
Do NOT do this on update runs.

- Run template's **scaffold command** (from its Scaffold Recipe) into
  project root `_concept/mockup-walkthrough/framework/`, then prune scaffold
  down to four routes this walkthrough needs. Configure framework for
  **static export** target so build emits plain HTML:
  - **Next.js** — `next.config.ts` with `output: 'export'`
  - **Nuxt** — `nuxt.config.ts` with `nitro.prerender` (or
    `nuxi generate`)
  - **SvelteKit** — `@sveltejs/adapter-static` + per-route `prerender = true`
- Author four route/page files (root layout, index, screen collection,
  journey collection) per framework's routing convention — see layout
  examples above. Each must wire `data-spec-*` onto built body, read from
  `specs.json`. Specifically:
  - The **screen-collection route** interpolates each element's pre-resolved
    `href`/`row_href`/`items[].href` (`el.href ?? '#'`, or the
    framework-native link component reading the same pre-resolved field —
    see § Renderer Contract) — it MUST NOT compute a target's href itself;
    renders `columns`/`sample_rows`/`items`/`options` as real DOM content
    per `contracts/walkthrough_renderer.md` § kind → DOM tag mapping; and
    renders `screen.body_html` inside a collapsed (or, when
    `screen.elements.filter(e => !e.provisional).length === 0`, open)
    `<details class="spec-panel">`.
  - The **root layout** renders `specs.app_nav` as a `<nav class="app-nav">`
    sibling on screen pages only (§ Renderer Contract above).
- Emit `package.json` with `dev`, `build`, `preview` scripts so any developer
  can run walkthrough locally (mockup-design.md § 10 "Walkthrough
  deployability"). Skill itself never auto-serves; only builds. Example
  scripts (Next.js):

  ```json
  {
    "name": "mockup-walkthrough-framework",
    "private": true,
    "scripts": {
      "dev": "next dev",
      "build": "next build",
      "preview": "npx serve out"
    }
  }
  ```

  Nuxt: `dev: nuxi dev`, `build: nuxi generate`,
  `preview: npx serve .output/public`. SvelteKit: `dev: vite dev`,
  `build: vite build`, `preview: vite preview`.
- Install dependencies using the template's package manager.

On update runs, agent NEVER regenerates framework config or route/page
templates — only `specs.json` and token stylesheet.

## STEP 6: Generate `specs.json` and token styles (both modes)

Write `specs.json` (under framework's data dir, e.g. `src/data/specs.json`)
derived from the in-memory model built in STEP 3 (screens with `body_html`,
pre-resolved `href`/`row_href`, normalised `items[]`, and top-level
`app_nav[]`). Schema as shown in `specs.json` shape section above. Overwrite
unconditionally.

Write token stylesheet (e.g. `src/app/globals.css` or
`assets/css/global.css` per template) with one `:root` custom property per
flattened `token_var`:

```css
:root {
  /* one line per flattened token_var */
  --token-<name>: <value>;
}
```

Overwrite unconditionally. File is agent-managed every run.

On update runs only: compare count of `--token-*` keys in freshly derived
in-memory model vs. CSS var declarations in existing stylesheet before
overwriting. If counts differ, append `kind: "stale_token_styles"` to
`warnings[]`.

## STEP 7: Build

Run template's **build command** from
`_concept/mockup-walkthrough/framework/`. Fall back to `bun run build` if
template doesn't name a build command:

```bash
bun run build
```

On non-zero exit: print full stderr, exit non-zero. Do not write
`manifest.json`.

After build, agent MUST verify built HTML carries `data-spec-*`
server-side: fetch one built `screen/<group>/<name>` page from disk,
confirm `data-spec-screen` present in static HTML (not only injected at
runtime). If absent → fail: "built HTML missing data-spec-* server-side —
move attributes out of client-only code into SSR/SSG output".

Agent MUST also verify that same fetched page's resolved-target node (any
element the in-memory model gave a non-null `href` in STEP 3) carries a
plain, resolvable `href` attribute in the static HTML — not merely a
framework-native link component's props object that only resolves after
hydration. If a resolved element's rendered node has no plain `href` in the
static HTML → fail: "built HTML missing a resolvable href server-side —
the framework-native link component must resolve to a plain <a href=...>
in SSR/SSG output" (§ Renderer Contract above).

## STEP 8: Write `manifest.json`

Emit pinned schema (`contracts/walkthrough_renderer.md` § Manifest schema,
`schema_version: "1.2"`). Build from the STEP 3 in-memory model — NOT by
serialising `specs.json`. Template-only fields from `specs.json`
(`screens[].title`, `screens[].group`, `screens[].journeys[]`,
`screens[].body_html`, `screens[].elements[].href`, `.row_href`,
`items[].element_id`/`.provisional`/`.href`, `journeys[].title`,
`journeys[].description`, `app_nav[].href`) MUST NOT appear in
`manifest.json` — see § `specs.json` → `manifest.json` projection above.

New fields this revision adds to `manifest.json#screens[].elements[]`:
`target` / `row_target` / `columns` / `sample_rows` / `items` / `options`,
echoed **verbatim** from the declared frontmatter (the *declared* value,
never the resolved `href` — matches static-html/astro/lit and the pinned
contract exactly). Top-level `app_nav[]` — one entry per rendered nav link,
in rendered order (positional, not alphabetic): `{label, target, source}`
where `target` IS the resolved href (per contract § Field semantics,
`app_nav`'s `target` is the rendered value, unlike element `target`).

Sort `screens[]` by `screen_path`, `journeys[]` by `journey_id`,
`features[]` by `feature_path`. `app_nav[]` is NOT sorted — it keeps
rendered order. Write atomically (tmp → fsync → rename).

`renderer: "mockup-walkthrough-framework"`, `renderer_version:` this
SKILL.md's `metadata.version`.

`target_framework` is one field added beyond pinned schema. Records
framework resolved in STEP 2 (`nextjs` | `nuxt` | `sveltekit`) so
`mockup-feedback-annotate` knows how built HTML was produced. `rendered_html`
paths recorded relative to project root (framework's static-export output
location).

## STEP 9: Validate

Run from repo root:

```bash
python mockup-walkthrough/framework/validator.py _concept/mockup-walkthrough/framework
```

Exit 0 = ready. Exit 2 = violation report.

> **NOTE — validator gap (pre-existing, not fixed by this revision).**
> `mockup-walkthrough/framework/validator.py` does not exist on disk yet,
> same gap as `mockup-walkthrough/lit/validator.py` (Task 7). When it is
> eventually authored it MUST include the same checks static-html's/astro's
> validators implement — in particular: `target`/`row_target`/
> `items[].target` resolution (every resolvable target renders a real
> `href` in the built HTML, never a stray `href="#"`); table-row-count/
> items-count/options-count fidelity against the declared `elements:`
> block (rendered `<tbody>` row count matches `sample_rows[]` length,
> rendered items/options count matches declared `items[]`/`options[]`
> length); canonical-heading-slug-leak detection (no `data-spec-element`
> value is a canonical-heading slug — § Auto-slug fallback exclusion
> list); `<details class="spec-panel">` presence on every built screen
> page; and the `no_explicit_elements` open-panel case. This SKILL.md's
> STEP 9 already assumes that validator exists; do not author it as part
> of any task whose scope is this SKILL.md alone — this note only records
> what it must cover once it is written.

## Error handling

### Shared conditions

See `contracts/walkthrough_renderer.md` § Shared error handling.

### Framework-specific

| Condition | Behaviour |
|---|---|
| `tech_stack_skill` abstract / `custom` / unset | HARD-FAIL — tell user to run `impl-architecture-templates-select`; `kind: "unresolved_template"`; note `mock-static-fallback` exists |
| `tech_stack_skill` names a non-existent `template-*` dir | HARD-FAIL — stale id; `kind: "unresolved_template"` |
| Dependency install exits non-zero | Fail loudly with stderr; do not build |
| Build command exits non-zero | Fail loudly with stderr; do not write `manifest.json` |
| Built HTML missing `data-spec-*` server-side | Fail: attributes must be emitted in SSR/SSG output, not client-only |
| Token count differs from CSS var count (update runs only) | `kind: "stale_token_styles"`; user must extend the token stylesheet manually |
| Scaffold missing `el.href` and/or `spec-panel` (update runs only) | `kind: "stale_scaffold"`; user must delete the scaffold or port the template changes (§ `stale_scaffold` check, STEP 4) |

### `warnings[].kind` enum

Shared enum per `contracts/walkthrough_renderer.md` § warnings[].kind enum
(`auto_slugged`, `auto_slug_collision`, `missing_layout`, `missing_feature`,
`unknown_element_kind`, `missing_screen`, `missing_screen_sequence`,
`no_journeys`, `unresolved_target`, `no_explicit_elements`);
`unresolved_template`, `stale_token_styles`, and `stale_scaffold` are
framework-specific additions. `unresolved_template` emitted in hard-fail
diagnostic (STEP 2) — no `manifest.json` written when framework can't be
resolved.

## MUST / NEVER

Shared MUST/NEVER: `contracts/walkthrough_renderer.md` § Shared MUST / NEVER.

MUST  resolve target_framework from techstack.md `tech_stack_skill` before scaffolding
MUST  hard-fail when `tech_stack_skill` is abstract/custom/unset or has no template-* dir
MUST  emit every data-spec-* attribute in the built (SSR/SSG) HTML server-side, not client-only
MUST  configure the framework for a static-export build target
MUST  emit package.json with dev/build/preview scripts (deployability)
MUST  write specs.json and token styles before running the build
MUST  regenerate the token stylesheet on every run (agent-managed)
MUST  pre-resolve every `target`/`row_target`/`items[].target` into an `href` (or `null`) in `specs.json` at STEP 3/6 — route templates only interpolate `el.href ?? '#'` (or the framework-native link component reading the same pre-resolved field), they never resolve a target themselves
MUST  ensure any framework-native link component (`next/link`, `NuxtLink`, ...) used in a route template resolves to a plain, resolvable `href` in the built (SSR/SSG) HTML — never a client-only-wired href
MUST  render declared `columns`/`sample_rows`/`items`/`options` as real DOM content in the scaffolded route templates — no placeholder when content is declared
MUST  render the spec body only inside the collapsed (or, when zero explicit elements, open) `<details class="spec-panel">`, sourced from `body_html`
MUST  render the generated app-shell nav (`specs.app_nav`) inside the root layout on screen pages
MUST  run the `stale_scaffold` check on every update run and record a `warnings[]` entry when the scaffold predates this revision

NEVER regenerate the framework config or route/page templates on update runs
NEVER invent a target_framework not derived from a real template-* TEMPLATE.md
NEVER use a separate auto_slugged[] array — set provisional: true on the element object (the kind: "auto_slugged" warning entry in manifest.warnings[] is still required per the auto-slug step)
NEVER let a scaffolded route template re-derive target resolution or auto-slug ids at build time — that logic lives in STEP 3 only

## CHECKLIST

- [ ] `tech_stack_skill` resolved to an existing `template-*` directory before scaffolding
- [ ] `manifest.target_framework` matches the resolved template's framework
- [ ] Built index page exists under `_concept/mockup-walkthrough/framework/`
- [ ] `_concept/mockup-walkthrough/framework/manifest.json` exists and parses as JSON
- [ ] `manifest.schema_version == "1.2"` and `manifest.renderer == "mockup-walkthrough-framework"`
- [ ] One built `screen/<group>/<name>` page per screen file under `experience/screens/`
- [ ] One built `journey/<id>` page per journey in `stories.yaml`
- [ ] Every screen page `<body>` has `data-spec-screen` in the built HTML (server-side)
- [ ] Every annotatable node in screen pages has `data-spec-element`
- [ ] Every auto-slugged element node also has `data-spec-provisional="true"`
- [ ] Every journey page `<body>` has `data-spec-journey`
- [ ] Index page `<body>` has `data-spec-index="true"`
- [ ] `package.json` declares `dev`, `build`, and `preview` scripts
- [ ] Every screen page renders the app nav (`<nav class="app-nav">`, built HTML, server-side) with one resolvable `href` per entry
- [ ] Every element with a resolvable target renders a real `<a>` (or framework-native link component resolving to one) whose `href` resolves to an existing built page in the built HTML — no `href="#"` on a node whose manifest element declares a resolved target
- [ ] No canonical spec heading appears as an `el-region` widget (no `data-spec-element` value is a canonical-heading slug)
- [ ] Every declared table renders `sample_rows` verbatim as `<tbody>` rows in the built HTML
- [ ] Spec body appears only inside `<details class="spec-panel">`
- [ ] No auto-slugged label exceeds 40 chars or contains an action sentence
- [ ] `manifest.app_nav[]` is present and every entry resolves to an existing built page
- [ ] Validator (`mockup-walkthrough/framework/validator.py`) exits 0

EMIT  [mockup-walkthrough-framework] started run_id=<uuid>
EMIT  [mockup-walkthrough-framework] checkpoint phase=framework_resolved tech_stack_skill=<id> target_framework=<value>
EMIT  [mockup-walkthrough-framework] checkpoint screens=<N> journeys=<M>
EMIT  [mockup-walkthrough-framework] completed run_id=<uuid> target_framework=<value> screens=<N> journeys=<M> warnings=<W>
