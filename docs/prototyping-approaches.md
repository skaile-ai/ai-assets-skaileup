# Prototyping approaches

Ways to prototype an app — its **layout** (screens, shell, navigation, floorplans) and its **features** (interaction, state, data, flows) — sorted by what question each answers, how an agent can drive it, and how it compares with what `09_mockup/` does today. It is a maintainer's aid next to [layout-pattern-sources.md](./layout-pattern-sources.md), which covers where to study finished layouts and design-system floorplans; this file covers how to *build* a prototype and does not repeat those galleries. It is not part of a shipped asset, and no skill reads it.

Every source was opened on 2026-10-21 unless its row says otherwise; `[INFERENCE]` marks a reading not stated by the source (including every statement about this collection's gaps), and `[not opened]` marks a row that rests on metadata or on a source I did not read. Prices, star counts and push dates are the vendors' or GitHub's own figures on that date; "GitHub API" means `gh api repos/<r>` metadata.

## Start here

### Families compared

Fidelity follows NN/g's three axes — interactivity, visuals, content ([NN/g](https://www.nngroup.com/articles/ux-prototype-hi-lo-fidelity/)) — written as I/V/C, each L(ow), M(id) or H(igh).

| family | fidelity (I/V/C) | layout? | feature behavior? | speed | code handoff | agent-drivable | review / annotation |
|---|---|---|---|---|---|---|---|
| 1. Paper, Wizard of Oz, fake door, concierge | L/L/L, or H/H/H faked by a human | rough | only whether it is wanted or how it should respond | minutes to days | none | no (a human is the system) | in the session itself |
| 2. Sketch / wireframe tools (Excalidraw, Balsamiq, tldraw) | L/L/M | yes | no (links between boards at most) | minutes | none; Balsamiq exports to Claude/Jira/etc. | Excalidraw (JSON + MCP), Balsamiq (MCP), tldraw (SDK + agent kit) | comments (Balsamiq), shared canvas |
| 3. Design-tool prototypes (Figma, Penpot, ProtoPie, Axure, Framer) | M–H/H/M–H | yes, strongest | scripted: variables, conditions, repeaters | hours | Dev Mode / Code Connect / MCP; Framer hosts the site | Figma, Penpot, Balsamiq, Framer via MCP or API; ProtoPie MCP on Pro; Axure none seen | native comments, unmoderated test tools |
| 4. AI app and UI generators (v0, Lovable, Bolt, Replit, Stitch, Figma Make, Artifacts) | M–H/H/M–H | yes | yes, real code with a backend | minutes to hours | GitHub sync (v0, Lovable, Bolt); NN/g: "still just prototypes" | prompt in, code out; Stitch and v0 have MCP | share link, comments in the tool |
| 5. Code-based click-dummies (static HTML, kits, Storybook, Astro) | M–H/M–H/M–H | yes | journeys and component states | hours | the code is the artifact; GOV.UK: not for production | fully (text files) | in-house overlay, Chromatic, Vercel comments |
| 6. Behavior prototypes in code (MSW, json-server, XState, PGlite, BaaS, flags) | H/any/H | n/a | yes: data volume, error and empty states, lifecycle | hours to days | handlers, machines and schemas can survive into the app | fully | rides on the host (Storybook, preview URL) |
| 7. Low-code builders (Retool, Appsmith, Budibase, Glide, Softr) | H/M/H | admin-style only | yes, on a real datasource | hours | none: the builder is the runtime (Appsmith self-hostable) | partial (AI app builders) | in-tool |
| 8. Testing and review layers (Maze, Useberry, Lyssna, comments) | rides on 3–5 | — | — | hours | — | mostly no; agentation has MCP | the point of the family |

### Pick by question

| question you need answered | method | tool |
|---|---|---|
| Is this the right arrangement of regions for the task? | static mid-fi, two variants side by side | in-house `preview.html`; Balsamiq; Stitch variants ([stitch-skills](https://github.com/google-labs-code/stitch-skills)) |
| Can people find things (navigation, IA)? | tree test, first-click on a clickable prototype | [Useberry](https://www.useberry.com/) (tree test, first click, 5-second test); Maze |
| Can a person finish the task end to end? | clickable flow, 5 users | Figma prototype; Penpot flows; Storybook journey; [GOV.UK kit](https://prototype-kit.service.gov.uk/docs/) |
| Does a data-heavy screen survive real volume, empty and error states? | code prototype on mocked data | MSW + faker; json-server; PGlite |
| Does the lifecycle allow an illegal transition? | executable state machine | XState / Stately; Axure conditions; Figma conditionals |
| Will anyone want this feature at all? | fake door, smoke test | painted-door page; AdWords smoke test ([Ries](https://leanstartup.co/resources/articles/what-is-an-mvp/)) |
| Can we deliver the AI or backend behavior? | Wizard of Oz, concierge | a human behind the UI ([NN/g](https://www.nngroup.com/articles/wizard-of-oz/)) |
| Does it hold up on a real datasource with real permissions? | low-code or BaaS prototype | Retool, Appsmith; PocketBase, Supabase |
| Which of N variants wins? | variant test or in-product flag | Maze (up to five variants per study); Useberry A/B; GrowthBook |
| Do stakeholders agree with the look? | shared preview URL plus pinned comments | Figma comments; Vercel comments; Chromatic UI Review; in-house overlay |
| Is the riskiest assumption covered, whatever the fidelity? | prototype only that assumption | RAT ([Higham](https://hackernoon.com/the-mvp-is-dead-long-live-the-rat-233d5d16ab02)) |

### Against what the collection does today

> Superseded 2026-10-23 by [ADR 0026](adr/0026-the-mockup-stage-is-one-vue-storybook-package.md): the four surfaces below collapsed into one Vue Storybook package (`09_mockup/storybook/`), which takes up the seed-scenario switch, `play`-function journeys and the annotation round-trip named under "Gaps and ideas". This table is the state the decision was taken against.

| surface | what it is | nearest external family | what the research adds or contradicts |
|---|---|---|---|
| `09_mockup/prototypes/` ([node at 49e9c38](https://github.com/skaile-ai/ai-assets-skaileup-tree/blob/49e9c38/tree/09_mockup/prototypes/README.md)) | static `a.html`/`b.html` from a floorplan preview and `seed.json` sample data, neutral styling, no external reference, answers "right layout for this task?" before the spec | 2 (low/mid static wireframe) and NN/g static prototype | Fits NN/g's low-fidelity case: fast, stakeholders read it as unfinished. Variants match "test several variants" (Maze: up to five). No behavior at all: no click, state or data switch. |
| `walkthrough/` ([node at 49e9c38](https://github.com/skaile-ai/ai-assets-skaileup-tree/blob/49e9c38/tree/09_mockup/walkthrough/README.md)) | clickable static HTML or Astro, one page per screen and journey, `data-spec-*`, `manifest.json`; tabs have "no JS switching (static fidelity boundary)" | 5 (code click-dummy), GOV.UK kit | GOV.UK kit adds **branching journeys** (show a page by user input) and publishing; the walkthrough links fixed `target:`s only. |
| `storybook/` ([node](../tree/09_mockup/storybook/README.md)) | components, full-page compositions, one `Interactive` journey story per journey wired through real UI | 5 (Storybook) | Storybook's own `play` functions, Vitest interaction tests, MSW addon and MCP server are the unused half. |
| `feedback/` + `mockup-annotate` + `mockup-feedback` ([node](../tree/09_mockup/feedback/README.md)) | overlay resolves a click to `data-spec-element`, session JSON, patches against specs, human review before apply | 8 (comment overlays) | Closer to agentation (structured annotation for agents) than to Figma or Vercel comments, and stronger on one point: the click resolves to a **spec element**, not a CSS selector or source path. |
| the floorplans' `preview.html` files (16, one per floorplan) | 16 neutral previews with wide and narrow behavior | 2/5 (layout-only static HTML) | Same family as `prototypes/`; the floorplan is the design-system layer. |

Gaps and ideas — all `[INFERENCE]`:

- **No feature/behavior prototype tier.** Every surface answers "is the layout right?" or "does the journey link up?"; none answers "does this stateful or data-heavy feature behave?". NN/g's [AI-prototyping article](https://www.nngroup.com/articles/test-earlier-with-ai/) asks for exactly the inputs the collection already holds: decide which interactions, states and data must work; write down layout, hierarchy, edge cases (empty, error); collect data (real or synthetic). Those map to `07_screens/` situations, `10_blueprint/datamodel/seed.json` scenarios and `06_behaviors/`.
- **Seed scenarios as a state switch.** `prototypes/` already takes the `populated` scenario. A scenario selector (`empty`, `populated`, `error`) in a walkthrough page or Storybook toolbar is the cheapest data-driven prototype; Axure's repeater and Figma's variables are the same idea in design tools (§3).
- **Contract-derived mocks.** `@msw/source` generates MSW handlers from OpenAPI documents (§6); `10_blueprint/openapi.yaml` is the input. A behavior prototype would be handlers plus seed data behind the existing Storybook, with no new authoring format.
- **Executable behaviors.** `06_behaviors/[featureset].md` states machines in prose; XState/Stately models the same thing as a runnable machine that a click-dummy can drive (§6).
- **Journey stories that check themselves.** Journey click-dummies are wired by hand; `play` functions plus the Vitest addon turn them into interaction tests, and Storybook's MCP server lets an agent run them (§5).
- **No "will anyone want this?" layer.** No file under `tree/`, `skills/` or `docs/` mentions assumptions, fake doors, Wizard of Oz or concierge tests (grep, 2026-10-21). A riskiest-assumption note on a feature dossier, with the cheapest prototype that tests it, is the missing link between `goals.md` and `09_mockup/`.
- **Design-token interchange.** Stitch's [DESIGN.md](https://github.com/google-labs-code/design.md) (Apache-2.0) is tokens in YAML plus rationale in prose; `03_brand/brand.tokens.json` plays the same role. A one-way exporter would let Stitch, and any tool that reads DESIGN.md, generate on-brand variants.
- **Review round-trip.** Figma, Vercel and Chromatic comments live in the vendor's system; the in-house overlay returns a file that `mockup-feedback` patches into specs. No external tool replaces that; Vercel comments on a deployed walkthrough would only add reach (accounts required, §8).
- **Agent-drivable surfaces already exist.** Because the prototypes are plain files an agent writes, MCP servers for canvases (Figma, Penpot, Excalidraw, Balsamiq) add little for the pipeline itself; they matter if a human wants to edit visually and hand the file back.

### Skip

- tldraw `make-real` — repo archived 2026-02-18 (GitHub API); use the tldraw agent starter kit if you need the idea.
- `storybookjs/mcp` and `penpot/penpot-mcp` repos — both archived (GitHub API); the code lives on in Storybook's docs (`/docs/ai/mcp`) and `penpot/penpot/mcp`.
- Mirage JS — last release v0.1.48, 2023-10-30, last push 2025-08-11 (GitHub API); MSW is the maintained route.
- json-server for anything stable — v1 is a beta that "expect[s] breaking changes" ([README](https://github.com/typicode/json-server)).
- Magic Patterns, Miro Prototypes — alive, but nothing readable on the opened pages about export or agent access; kept in the tables as `[not opened]` rows rather than recommended.
- Design-gallery tools (Mobbin, Refero) — already in `layout-pattern-sources.md`.

## 1. Method and fidelity frameworks

These say which question a prototype can answer; none depends on a tool.

| method | what it is | question it answers | fidelity | cost / speed | source |
|---|---|---|---|---|---|
| Fidelity axes | A prototype can be high or low in **interactivity, visuals, content and commands** independently; the choice depends on test goals, completeness, tools, resources | which axis the question needs; a single page vs. multi-page, hand-sketched vs. realistic, clickable vs. a person acting as the computer | any mix | — | [NN/g](https://www.nngroup.com/articles/ux-prototype-hi-lo-fidelity/) |
| High fidelity | Realistic system response; "with high-fidelity interactivity and/or visuals, you can test workflow, specific UI components … graphical elements" | workflow, component behavior, hierarchy, legibility; people behave as with live software | H | slow to prepare; "building an interactive prototype can be time consuming" | same |
| Low fidelity | Less prep time, easy change during a test, less pressure on users, designers less wedded, "stakeholders recognize that the work isn't finished" | is this the right idea or layout | L | fast | same |
| Paper prototype | Sketch screens; a person plays the "computer" | early design ideas "at an extremely low cost"; "biggest improvements in user experience come from gathering usability data as early as possible" | L | minutes | [NN/g](https://www.nngroup.com/articles/paper-prototyping/) |
| Wizard of Oz | A person controls the user's screen; the user is told it is "unfinished and slow". Steal-the-mouse is the same in one room. "Particularly useful for testing AI-based systems before you have implemented the artificial intelligence" | can the system respond usefully, before building the system | I faked, V any | hours | [NN/g wizard](https://www.nngroup.com/articles/wizard-of-oz/); [NN/g fidelity](https://www.nngroup.com/articles/ux-prototype-hi-lo-fidelity/) |
| Fake / painted door | A button, menu item or pricing option for a feature that does not exist; "illusion of a feature or service without you having to actually build it"; a click leads to a "coming soon" or waitlist | will users try it (demand, not usability) | L visually, H on one control | hours | [Optimizely](https://www.optimizely.com/optimization-glossary/painted-door-test); [Amplitude](https://amplitude.com/explore/experiment/fake-door-testing) |
| Smoke test | Present the idea as if it existed and measure response; Ries: "a simple AdWords smoke test would have revealed how utterly bad the concept was" | is there interest before build | L | days | [Lean Startup Co](https://leanstartup.co/resources/articles/what-is-an-mvp/) |
| Concierge MVP | A human delivers the service manually, customers know it | does the value exist, before automating | none | days to weeks | defined in Ries's *The Lean Startup* — `[not opened]`; [book page](https://theleanstartup.com/book) opened, no definition on it |
| Riskiest Assumption Test | Replace "build an MVP" with "identify your riskiest assumption and test it"; "it's not a product. It's a way of testing whether you've found a problem worth solving" | the one belief whose failure kills the idea | whatever the assumption needs | smallest possible | [Higham, Hackernoon](https://hackernoon.com/the-mvp-is-dead-long-live-the-rat-233d5d16ab02); [Skyscanner, Medium](https://medium.com/@Skyscanner/the-mvp-is-dead-long-live-the-rat-3bc3da90de98) |
| Design sprint | Monday map, Thursday "hammer out a high-fidelity prototype", Friday test "with real live humans" | a complete idea against real users in five days | H visually, faked data | 5 days | [GV](https://www.gv.com/sprint/) |
| GOV.UK three types | sketches (explore ideas), click-through (design tool, early idea, feedback), **code** ("looks and behaves like GOV.UK (best for user research)") | type by stage | L→H | — | [prototype kit: prototyping](https://prototype-kit.service.gov.uk/prototyping/); [service manual](https://www.gov.uk/service-manual/design/making-prototypes) |
| AI prototyping | Tools "can follow instructions to achieve a general goal" but "lack the sophistication" to weigh tradeoffs; "best suited for ideation, concept exploration, and early-phase prototype testing"; "AI Prototypes Are Still Just Prototypes" | early layouts; complex interfaces with many states (filters, dashboards, conversational AI) that were too tedious to test by hand | M–H | minutes | [NN/g evaluation](https://www.nngroup.com/articles/ai-prototyping/); [NN/g test earlier](https://www.nngroup.com/articles/test-earlier-with-ai/) |

NN/g's six steps for a complex AI-built prototype ([test earlier](https://www.nngroup.com/articles/test-earlier-with-ai/)): decide what the prototype must do (interactions, states, data, responses); make the design decisions including empty and error states; collect data (export real data without PII, or generate a synthetic set); write a prompt with decisions and data; feed it to Cursor, v0 or Figma Make; edit and pilot-test. `[INFERENCE]` Steps 1–3 are what the collection's screen specs, situations and `seed.json` already are; step 5 is the missing consumer.

## 2. Sketch and wireframe tools

| tool | what it is | agent access | handoff | review | price / licence | source |
|---|---|---|---|---|---|---|
| Excalidraw | Collaborative whiteboard with a hand-drawn look | `.excalidraw` is plaintext JSON ([schema](https://docs.excalidraw.com/docs/codebase/json-schema)); remote MCP at `https://mcp.excalidraw.com` streams diagrams with fullscreen editing for MCP Apps clients ([excalidraw-mcp](https://github.com/excalidraw/excalidraw-mcp); pushed 2026-03-24) | none; diagrams, not UI code | share/collab | MIT; 134k stars; pushed 2026-10-21 | [excalidraw.com](https://excalidraw.com/); [repo](https://github.com/excalidraw/excalidraw) |
| Balsamiq | Wireframes; AI makes a wireframe from a prompt or screenshot, and "interactive prototypes"; boards can be linked | hosted MCP `https://bais.balsamiq.com/mcp`: read and analyze designs, create and edit boards; trial capped at 100 write calls per 24 h | export to PDF/image; sharing icons for Notion, Jira, Slack, Claude, Linear | Teams plan: unlimited reviewers who view or comment | Teams $24/editor/mo annual; Enterprise $35 incl. 2,500 AI credits (~156 wireframes or ~50 prototypes) | [home](https://balsamiq.com/); [AI](https://www.balsamiq.com/product/ai/); [MCP](https://balsamiq.com/support/integrations/mcp/); [pricing](https://balsamiq.com/pricing/) |
| tldraw | Infinite-canvas SDK for React; agent starter kit | agent can create/update/delete shapes, draw, align and distribute, read canvas screenshots, call external APIs | none | multiplayer starter kit | SDK licence: development use only; no use "in Production Environments" without a licence key ([LICENSE.md](https://raw.githubusercontent.com/tldraw/tldraw/main/LICENSE.md)); GitHub API shows `NOASSERTION` | [tldraw.dev](https://tldraw.dev/); [agent kit](https://tldraw.dev/starter-kits/agent) |
| Make Real (tldraw) | "Draw a ui and make it real": sketch → HTML via a model | repo has API routes for Anthropic, Google, OpenAI, Replit | HTML | link sharing | **repo archived 2026-02-18**; site still resolves | [site](https://makereal.tldraw.com/); [repo](https://github.com/tldraw/make-real) |
| Miro Prototypes | "Turn ideas into interactive prototype flows your team can explore before you or your coding agent writes a single line" | `[not opened]` beyond the page | none stated | Miro board | business plan | [miro.com/ai/prototyping](https://miro.com/ai/prototyping/) |
| FigJam | Whiteboard in Figma | Figma MCP can "retrieve FigJam resources" so "early-stage ideas, flows, and architecture maps carry into development" | — | Figma comments | with Figma | [MCP docs](https://developers.figma.com/docs/figma-mcp-server/) |
| ASCII / text wireframes | Layout drawn in monospace text | the only fidelity an agent both writes and diffs reliably `[INFERENCE]` | none | none: not clickable | free | `ui-craft` `/ui-craft:shape`: "ASCII layout + content inventory + state list + open questions before any JSX" ([README](https://raw.githubusercontent.com/educlopez/ui-craft/main/README.md)); the screen spec's `### Wireframe` fence does the same here |

`[INFERENCE]` Sketch tools answer "is this the right arrangement?" no better than the floorplan `preview.html` the collection already renders with real sample data; their value is the whiteboard session with a stakeholder, not the file.

## 3. Design-tool prototypes

| tool | prototyping / logic | handoff | agent access | review | price | source |
|---|---|---|---|---|---|---|
| **Figma** | Connect frames; "any team or plan"; play in Presentation view ([guide](https://help.figma.com/hc/en-us/articles/360040314193-Guide-to-prototyping-in-Figma)). Variables of string/number/color/boolean type set by prototype actions: update text, change dimensions or auto-layout, toggle visibility; multiple actions per trigger and if/else conditionals; **paid plans** ([variables](https://help.figma.com/hc/en-us/articles/14506587589399-Use-variables-in-prototypes); [conditionals](https://help.figma.com/hc/en-us/articles/15253220891799-Multiple-actions-and-conditionals)) | Dev Mode: inspect, generated code, asset download, compare changes; Code Connect swaps generated code for the team's component code ([Dev Mode](https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode)) | Figma MCP server: generate code from frames, extract variables/components/layout, retrieve Make and FigJam resources, **write native content to the canvas** (needs remote server and a Full seat outside drafts; "free during the beta … will eventually become a usage-based paid feature"), turn live UI from localhost or production into design layers ([docs](https://developers.figma.com/docs/figma-mcp-server/)) | Comments for anyone with view access, on files and prototypes ([guide](https://help.figma.com/hc/en-us/articles/360039825314-Guide-to-comments-in-Figma)) | Starter free, 150 AI credits/day up to 500/mo ([pricing](https://www.figma.com/pricing/)); paid seat prices not captured | links above |
| **Figma Make** | Prompt-to-app; attach existing designs; edit with the properties panel, draw tool, annotations and chat; share previews; publish as a website; backend via a generated Payload backend (database, file storage, auth, admin panel) or a manual Supabase connection; Full seats on paid plans, trial on others | code editor and export code are listed Make features with per-plan availability ([FAQ](https://help.figma.com/hc/en-us/articles/31722591905559-Figma-Make-FAQs)); Make resources reach agents over MCP | via the MCP resources above | team comments in the same conversations | credits per plan | [explore](https://help.figma.com/hc/en-us/articles/31304412302231-Explore-Figma-Make); [create](https://help.figma.com/hc/en-us/articles/31304485164695-Create-and-edit-a-functional-prototype-or-web-app); [backend](https://help.figma.com/hc/en-us/articles/32640822050199-Add-a-backend-to-a-functional-prototype-or-web-app) |
| **Penpot** | Open source (MPL-2.0; 61.5k stars). Prototype mode: drag a connection from a layer to a board; a flow start is created; play in View mode and share by link ([help](https://help.penpot.app/user-guide/prototyping-testing/prototyping)). Variables or conditions not mentioned on pages read `[INFERENCE: absent]` | design tokens `[not opened]`; MCP "design-to-design, code-to-design and design-code" | MCP server through the Plugin API: retrieve design data, create and modify elements; hosted remote server enabled under Account → Integrations → MCP; `penpot/penpot-mcp` archived, code at [`develop/mcp`](https://github.com/penpot/penpot/tree/develop/mcp) ([help](https://help.penpot.app/mcp/); [page](https://penpot.app/ai/mcp-server)) | View-mode link | Professional cloud $0/user/mo; self-host plans exist | [penpot.app](https://penpot.app/); [pricing](https://penpot.app/pricing); [repo](https://github.com/penpot/penpot) |
| **Framer** | Designs real sites: Code Components (React with visual controls), Code Overrides, Fetch API endpoints, plugins ([developers](https://www.framer.com/developers/)) | publishes the site; for marketing pages the design is the product `[INFERENCE]` | Server API (`npm i framer-api`) and external agents (Claude Code, Codex, Cursor) with "full access to your canvas, components, CMS" ([quick start](https://www.framer.com/developers/server-api-quick-start); [agents](https://www.framer.com/agents/external/)) | extra editors $20/mo, viewers free | Basic $10, Pro $30 ([pricing](https://www.framer.com/pricing)) | links |
| **ProtoPie** | Advanced interaction prototypes incl. hardware, automotive/HMI, TV, watches; "Use AI to generate interactions, perfect them credit-free, and hand off clean specs" ([home](https://www.protopie.io/)) | handoff recordings; Connect add-on | Pro tier lists "MCP Core" | user testing add-on on Pro | Free; Pro $47/editor/mo ([plans](https://www.protopie.io/plans)) | links |
| **Axure RP 11** | "Conditional Logic" with variables; data-driven tables and grids with the **repeater** that sort and filter dynamically; adaptive views; "no code required" ([features](https://www.axure.com/axure-rp)) | specifications and diagrams in the same tool ([home](https://www.axure.com/)) | none seen on pages read | unlimited reviewers on Pro | Pro $29/user/mo; 30-day trial ([pricing](https://www.axure.com/pricing)) | links |

`[INFERENCE]` Axure's repeater and Figma's variables are the design-tool form of "prototype with data": a handful of fixtures, a state, a condition. They stop at the prototype; `seed.json` plus a script gets the same effect in code without a seat.

## 4. AI app and UI generators

State on 2026-10-21. All first-party pages.

| tool | what it makes | layout vs feature | code ownership / export | design-system adherence | agent access | price | source |
|---|---|---|---|---|---|---|---|
| **v0** (Vercel) | "AI agent that helps anyone create real code and full-stack apps and agents"; "high-fidelity UIs from your wireframes or mockups"; backend connections; one-click deploy | both | GitHub: branches, previews, pull requests, CI | `[not opened]` | acts as an MCP client with presets (Notion, PostHog, Mobbin, Vercel, Zapier …) | Free; Plus $30/user/mo with $30 credits and $2 free daily | [docs](https://v0.app/docs); [GitHub](https://v0.app/docs/github); [MCP](https://v0.app/docs/MCP); [pricing](https://v0.app/pricing) |
| **Lovable** | Full-stack web apps from natural language: frontend, backend, database, auth, integrations | both | Git sync two-way to GitHub, GitLab, Bitbucket; "editable code" | `[not opened]` | `[not opened]` | Free, Pro, Business, Enterprise; credit-based | [welcome](https://docs.lovable.dev/introduction/welcome); [plans](https://docs.lovable.dev/introduction/subscription-plans); [git sync](https://docs.lovable.dev/integrations/git-sync-overview) |
| **Bolt.new** | Websites, web apps (JS frameworks) and mobile apps (Expo); input offers Prototype, Website, Slides, App; start from Figma, GitHub or a team template | both | GitHub repo sync and branches | `[not opened]` | `[not opened]` | `[not opened]` | [home](https://bolt.new/); [intro](https://support.bolt.new/building/intro-bolt); [git](https://support.bolt.new/integrations/git) |
| **Replit Agent** | "Tell Replit Agent your app or website idea, and it builds it through chat"; built-in database; Plan mode | both | export path `[not opened]` | `[not opened]` | `[not opened]` | Core $20/mo ($18 annual) | [agent](https://replit.com/products/agent); [pricing](https://replit.com/pricing) |
| **Google Stitch** (Labs, Beta) | "Generates UIs for mobile and web applications"; via skills: screens from text or image, edit, **design variants**, upload a `DESIGN.md`, convert screens to React/React Native, extract static HTML from a running app | layout first | HTML and React/RN via skills | **DESIGN.md** is Stitch's design system: YAML tokens + prose, spec repo Apache-2.0, 28k stars | MCP ("Stitch via MCP" docs page; body not readable, JS app); `stitch-skills` for Claude Code, Codex, Gemini CLI, Cursor | `[not opened]` | [site](https://stitch.withgoogle.com/); [skills](https://github.com/google-labs-code/stitch-skills); [DESIGN.md](https://github.com/google-labs-code/design.md) |
| **Claude artifacts** | A design, deck, doc, dashboard or small interactive tool beside the chat; also from Claude Code; templates Docs, Slides, Design (all plans), Dashboards and Motion (beta) | layout and small tools | share/publish; recipients use their own plan limits; "legacy artifacts" made before 2026-09-16 cannot be recreated; export `[not opened]` | `[not opened]` | native to Claude | Free to Max; connect apps and store data on Pro and above | [support](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them) |
| **Uizard** | AI screens, wireframe/screenshot scanners, prototyping; Autodesigner 2.0 | layout | "Developer handoff React CSS" on Pro | `[not opened]` | none seen | Free (3 generations/mo); Pro $12/mo annual; unlimited viewers/commenters | [home](https://uizard.io/); [pricing](https://uizard.io/pricing/) |
| **Magic Patterns** | Homepage now "MagicOS": an infinite canvas for ideas, designs and decisions | `[not opened]` | `[not opened]` | `[not opened]` | `[not opened]` | pricing page body not readable | [home](https://www.magicpatterns.com/) |
| **Subframe** | Design canvas "based on HTML & React"; "1:1 with code"; components with props, slots, variants "synced" with code; a coding agent on the canvas | layout | desktop app | components from the codebase | agent built in | `[not opened]` | [home](https://www.subframe.com/) |
| **Onlook** | Open-source visual editor for Next.js + Tailwind; edit the DOM visually; branching to experiment | layout, some features | your own repo | brand assets and tokens panel | `[not opened]` | Apache-2.0; 27k stars; pushed 2026-08-25 (GitHub API) | [repo](https://github.com/onlook-dev/onlook) |

NN/g's evaluation split these into three kinds: AI-assisted design tools (static wireframes or mockups), vibe-coding tools (interactive code prototypes) and general chatbots; **longer, specific prompts "consistently yield better results"**, particularly for code-based tools; outputs reflect training-data patterns ([evaluation](https://www.nngroup.com/articles/ai-prototyping/)).

`[INFERENCE]` Every generator in this table takes text plus optionally a design system, which is what the collection's specs plus `brand.tokens.json` are. The collection's advantage is that its prototypes stay derived from specs; a generator output would be a one-way view that drifts unless regenerated from the spec, like `prototypes/` already is.

## 5. Code-based prototypes

| approach | what it is | source |
|---|---|---|
| GOV.UK Prototype Kit | The reference practice: code prototypes that "look and behave like the real thing, on mobile and desktop"; test on the user's device and with assistive technology; **branching** ("show different pages based on user input") to test flows; publish on the web; Git for history. "You must not use prototype code for production." | [kit](https://prototype-kit.service.gov.uk/docs/); [prototyping](https://prototype-kit.service.gov.uk/prototyping/) |
| Static HTML, no build | One self-contained file per variant; this collection's `prototypes/a.html` and the floorplan `preview.html`. `[INFERENCE]` Cheapest code route; no state beyond a tiny inline script. | in-house |
| shadcn blocks and registry | `shadcn` CLI runs your own registry to distribute "components, hooks, pages, config, rules" to any project; the MCP server browses, searches and installs registry items by natural language | [registry](https://ui.shadcn.com/docs/registry); [MCP](https://ui.shadcn.com/docs/mcp); [blocks](https://ui.shadcn.com/blocks) |
| Nuxt UI templates | Starters "from a bare setup to a dashboard, a SaaS site or a chat app"; e.g. Calendar with day/week/month views, drag and drop, optimistic updates | [templates](https://ui.nuxt.com/templates) |
| Astro | "Content-driven websites"; islands architecture to cut JavaScript — the walkthrough's second renderer | [why Astro](https://docs.astro.build/en/concepts/why-astro/) |
| Storybook | `play` functions run after render to drive the component; interactions panel to debug; automate with the **Vitest addon** in UI, terminal or CI; composition lists stories of any published Storybook inside yours; MSW addon mocks network calls; autodocs; publish. MIT, 91k stars. **MCP server (preview)** gives agents your component docs, lets them generate stories and run interaction and a11y tests in a self-healing loop; the docs toolset needs a components manifest | [play](https://storybook.js.org/docs/writing-stories/play-function); [interaction tests](https://storybook.js.org/docs/writing-tests/interaction-testing); [composition](https://storybook.js.org/docs/sharing/storybook-composition); [mocking](https://storybook.js.org/docs/writing-stories/mocking-data-and-modules/mocking-network-requests); [MCP](https://storybook.js.org/docs/ai/mcp/overview); [autodocs](https://storybook.js.org/docs/writing-docs/autodocs) |
| Ladle | React stories on Vite; MIT; 3.0k stars; pushed 2026-06-28 | [repo](https://github.com/tajo/ladle) |
| Histoire | Vite-powered stories for React, Vue 3 and Svelte; MIT; 3.6k stars; pushed 2026-10-19 | [site](https://histoire.dev/); [repo](https://github.com/histoire-dev/histoire) |

`[INFERENCE]` For this collection, Ladle and Histoire add nothing: `mockup-storybook` already targets stack-specific story extensions, and Storybook's `play` plus MCP surface is the part the collection does not yet use.

## 6. Feature and behavior prototyping in code

The prototype answers what the layout cannot: how many rows, which state, what the API says.

| tool | what it does | fidelity | agent-drivable | status | source |
|---|---|---|---|---|---|
| MSW (Mock Service Worker) | Intercepts requests with the Service Worker API in the browser and Node; agnostic to framework and client; "a single source of truth for your API mocks across your entire stack" | H data/I, any visuals | text handlers | MIT; 18k stars; pushed 2026-10-17 (GitHub API) | [docs](https://mswjs.io/docs/) |
| `@msw/source` | Generates MSW handlers from HAR files and **OpenAPI documents** | — | CLI | 220 stars; pushed 2026-09-30 (GitHub API) | [repo](https://github.com/mswjs/source) |
| json-server | A `db.json` or `db.json5` file becomes a REST API | H data | text | MIT; 75.7k stars; **v1 beta, expect breaking changes** | [repo](https://github.com/typicode/json-server) |
| Mirage JS | API mocking inside the frontend: "build, test and share a complete working JavaScript application without having to rely on any backend services"; seeds with factories | H data | text | low activity (above) | [site](https://miragejs.com/) |
| faker-js | "Fake (but realistic) data for testing and development" | content | text | 15.5k stars; pushed 2026-10-21 (GitHub API) | [repo](https://github.com/faker-js/faker) |
| XState + Stately Studio | XState v5: state machines, statecharts and actors in JS/TS (MIT, 30k stars); Stately Studio: "visual software modeling platform" for the same machines | I, state | machines are code; Studio is visual | pushed 2026-10-21 | [docs](https://stately.ai/docs); [repo](https://github.com/statelyai/xstate) |
| PGlite | Postgres in WASM, "under 3MB Gzipped"; extensions incl. pgvector; reactive and live-sync primitives; Apache-2.0 | H data, no server | text | pushed 2026-10-21 | [site](https://pglite.dev/) |
| SQLite WASM | The SQLite project's own WASM and JS APIs for browsers | H data | text | official | [docs](https://sqlite.org/wasm/doc/trunk/index.md) |
| PocketBase | Open-source backend: embedded SQLite with realtime subscriptions, auth, dashboard UI, REST-ish API; one file | real backend | text/API | MIT; 61.5k stars | [docs](https://pocketbase.io/docs/) |
| Supabase | Hosted Postgres with quickstarts per framework; Figma Make's manual backend option | real backend | API | Apache-2.0; 112k stars | [docs](https://supabase.com/docs/guides/getting-started) |
| Feature flags | GrowthBook: open-source experimentation; OpenFeature: a standard that lets teams "enable, disable or change the behavior of certain features" | in-product variants | SDK | active | [GrowthBook](https://docs.growthbook.io/); [OpenFeature](https://openfeature.dev/) |

`[INFERENCE]` Handoff: unlike design-tool prototypes, MSW handlers, OpenAPI-derived mocks and XState machines are real TypeScript that can stay in the app's test suite; json-server and Mirage mock files cannot. In-browser Postgres (PGlite) lets the same SQL run in the prototype and the app. Flags are the only family here that prototypes inside the shipped product, so the "prototype" ships to real users.

## 7. Low-code and internal-tool builders

| tool | what it is | when it beats a custom prototype | limits | price | source |
|---|---|---|---|---|---|
| Retool | Internal-tool and app builder with AI; "Explore the new Retool app builder for free" | data-heavy admin on a real database or API in hours; self-host available | the builder is the runtime, not your code `[INFERENCE]` | Free: unlimited apps, up to 5 users; Team builder €9/mo annual; Business €46 | [home](https://retool.com/); [pricing](https://retool.com/pricing) |
| Appsmith | Open-source: drag widgets, connect datasources, write queries and JavaScript | same, self-hosted and inspectable | desktop-style admin UIs | Apache-2.0; 41k stars (GitHub API) | [docs](https://docs.appsmith.com/) |
| Budibase | Agents, apps and automations on your own data, LLMs and APIs | forms, approval flows, process tools | — | "Try it free"; 28k stars (GitHub API) | [home](https://www.budibase.com/) |
| Glide | GlideOS: describe software or upload a spreadsheet and an agent builds it; Glide Classic is a separate product | spreadsheet-backed field apps | `[not opened]` beyond the overview | Free, Basic, Plus, Pro, Enterprise | [home](https://www.glideapps.com/) |
| Softr | Portals and internal tools with database, workflow automation and permissions built in | client portals, CRMs, intranets | `[not opened]` beyond the overview | `[not opened]` | [home](https://www.softr.io/) |

`[INFERENCE]` These win when the open question is data and permissions rather than layout: the prototype is the product and the answer is "can the real datasource support this screen?". They lose when the design must be reviewed against a spec, because nothing carries `data-spec-*` or a floorplan. None offers a path into custom frontend code.

## 8. Testing and review of prototypes

| tool | what it does | works on | agent access | price / licence | source |
|---|---|---|---|---|---|
| Maze | Prototype testing "before you build"; a study from a goal via an AI study builder; "up to five design variants in a single study"; integrates with Figma prototypes | Figma prototypes | `[not opened]` | free tier offered | [prototype testing](https://maze.co/prototype-testing/) |
| Lyssna | "Validate your Figma designs with real users before a single line of code" | Figma | `[not opened]` | free sign-up | [prototype testing](https://www.lyssna.com/features/prototype-testing/) |
| Useberry | Imports Figma, ProtoPie, Sketch designs and **live websites** (or an embedded snippet); tree test, first click, 5-second test, A/B ("tasks or variations in random order") | design files and live URLs | `[not opened]` | Free; paid plan 300 responses/mo | [home](https://www.useberry.com/); [pricing](https://www.useberry.com/pricing/) |
| Figma comments | Pinned comments on files, FigJam and prototypes | Figma | — | any plan | [guide](https://help.figma.com/hc/en-us/articles/360039825314-Guide-to-comments-in-Figma) |
| Vercel Comments | Threads on any UI of a preview deployment through the Vercel Toolbar; links to Slack; on by default for all plans; participants need a Vercel account | preview deployments | — | free | [docs](https://vercel.com/docs/comments) |
| Chromatic UI Review | Linked to a pull request; visual changeset against main; designers and product managers approve or discuss intentional changes | Storybook | — | `[not opened]` | [docs](https://www.chromatic.com/docs/review/) |
| Agentation | Click an element, note, copy markdown for an agent: CSS selectors, source file paths, React component tree, computed styles; MCP integration and an annotation schema so agents can ask back and report fixes | any React page | MCP | **PolyForm Shield 1.0.0** (no competing product); 5.0k stars | [site](https://www.agentation.com/); [repo](https://github.com/benjitaylor/agentation); [LICENSE](https://raw.githubusercontent.com/benjitaylor/agentation/main/LICENSE) |
| In-house overlay | Click → nearest `data-spec-element`; session JSON; triage; reviewed patches to specs | walkthrough renderers | file-based | in repo | [node](../tree/09_mockup/feedback/README.md) |

`[INFERENCE]` Unmoderated tools (Maze, Lyssna, Useberry) measure completion on a *clickable* prototype, so they need the click-dummy to exist; Useberry's live-website import is the route for a published walkthrough. Agentation and the in-house overlay solve the same "describe the element" problem; agentation's license restricts building a competing tool.

## Not verified / dead ends

- Concierge MVP origin: no primary page opened that defines it; Ries's book page and blog posts opened do not use the term.
- Stitch docs (`stitch.withgoogle.com/docs`, `/docs/mcp/setup`, `/docs/mcp/reference`) are a JS app; only meta text was readable. Stitch capabilities above come from Google's `stitch-skills` and `design.md` repos.
- Magic Patterns pricing page, Bolt pricing, Replit export, Lovable/v0 design-system features, Claude artifact export: pages opened but the fact was not on them.
- Penpot variables/conditions, ProtoPie MCP capabilities (only the "MCP Core" line in the Pro plan), Balsamiq MCP tool list beyond the overview: not read.
- Figma paid-seat prices: the pricing page text lost its tier labels, so only Starter's terms are quoted.
- Figma `help.figma.com/.../Use-variables-in-prototypes` 15253220891543 and Figma Make 31304482564119 articles: 404; the working URLs above replaced them. NN/g `/articles/prototyping/` and `/fake-door-testing/`: 404.
- Docs pages for Retool beyond pricing, Glide and Softr feature detail: overview only.
