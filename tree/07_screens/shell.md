---
path: _concept/07_screens/shell.md
summary: the app frame — navigation, layout areas, breakpoints, shared patterns
owner: [experience-shell]
may_propose: []
---

# _concept/07_screens/shell.md

The frame every screen appears inside: navigation, layout areas, breakpoints, and the conventions screens are not each meant to re-decide. `experience-shell` writes exactly this one file and no screen spec. It normally runs after the feature loop, so the frame is drawn around screens that exist; in the reverse flow, where it runs before `spec-feature`, it is drawn around the screens the codebase already has. Where `APP-DESIGN.md` exists the frame follows its navigation and message/edit/modal decisions, read per `tree/APP-DESIGN.md § Reading it`. The walkthrough renders the `kind: nav` element below as the app nav on every screen page; without it the renderer derives a default nav, one link per screen grouped by feature directory, and flags it provisional.

## Format

Frontmatter: `elements:` carries the `kind: nav` block (schema in `tree/07_screens/README.md`) and `last_updated` as in `tree/README.md § Frontmatter every markdown artifact carries`. Body sections, named exactly because the renderer's spec panel shows them:

- `## Navigation` — the destinations, grouped by featureset, each by the screen id it already has, with prominence.
- `## Layout Areas` — header, primary navigation, content region and anything persistent beside them: what each holds and what stays put while the content changes; a short ASCII sketch carries this faster than three paragraphs.
- `## Responsive Behaviour` — the breakpoints, and what the navigation becomes below each.
- `## Shared Patterns` — layout only: page-header composition, breadcrumb placement, which regions persist, and what the content region shows while loading. Empty, error, confirmation, message and editing patterns are not decided here: they cite the `APP-DESIGN.md` MSG, EDIT and MOD entries by id.
- `## Proposed interaction patterns` — only when `APP-DESIGN.md` is absent: the empty, error, confirmation, message and editing patterns this frame needs, written as proposals for `experience-interaction`.

```yaml
---
elements:
  - id: app-nav
    kind: nav
    label: "Main navigation"
    states: [default]
    items:                       # same destinations, same order as ## Navigation
      - { label: "Tasks", target: 20_tasks/task_list }
last_updated: YYYY-MM-DD
---
```

## Writing it

1. **Read what the app is for and where its screens are.** `brief.md` for the hero flow, `05_features/featuresets.md` for the featuresets and their features, `04_journeys/` for the order users move through them, and `03_brand/brand.tokens.json` for the palette, type scale and spacing the frame is drawn in (format: `tree/03_brand/brand.tokens.md`) — reference brand values by name, because a hex invented here diverges from the tokens the renderers use. Read `APP-DESIGN.md` when it exists, per `tree/APP-DESIGN.md § Reading it`. The screens come from `07_screens/<feature_slug>/*.md`: each file's `id` and title are a candidate nav destination. Where `07_screens/` holds none (the reverse flow), take them from the screens recorded in `02_grounding/findings/screens.md` and say in `shell.md` which source each destination came from. With neither, stop and name the missing step — `spec-feature` or `concept-reverse` — because a nav drawn without screens behind it is a nav invented here.
2. **Derive the navigation from those screens.** Every destination is a screen a spec or a finding names, under the screen id it already has; a destination nothing backs is dropped. Where `APP-DESIGN.md` exists, derive under its Navigation section (rule P12, `rulebook/rules.md § P12`): primary navigation lists core objects and the few workspaces its entries name, and supporting objects sit behind their parent. Without it, group by featureset and let the journey stage (`stories.yaml § stages`) decide prominence: hero and vital journeys earn primary navigation, hygiene flows sit behind a settings or admin entry. A nav with one item per screen is a menu of the file system rather than of the product.
3. **Describe the layout areas** as the format above says.
4. **Settle the responsive behaviour once, here** — decided anywhere else, it gets decided differently on every screen.
5. **Write the shared patterns** every screen reuses, as layout only (see `## Format`). Empty, error, confirmation, message and editing patterns are cited by id from the `APP-DESIGN.md` MSG, EDIT and MOD entries (`tree/APP-DESIGN.md § Reading it`), never decided here. Without the file, record them under `## Proposed interaction patterns` and hand them to `experience-interaction` — a pattern this skill settles alone is the one every feature spec would otherwise make inconsistently.
6. **Mirror the navigation into the `elements:` block.** `shell.md`'s own frontmatter carries a `kind: nav` element whose `items[]` are the destinations from step 2, in the same order, each with its `target`, shaped per `tree/07_screens/README.md § Content fidelity` — an unmirrored `## Navigation` section renders as a nav the user never designed. A target taken from the findings resolves once `spec-feature` writes that screen under the same id; until then it is reported as an unresolved target rather than a failure.
7. **Show the frame to the user in their terms** — where things live, what is always on screen, what happens on a phone — and iterate until they approve. Then point at the next step: `spec-feature` in the reverse flow, where it writes every screen inside this frame, and the walkthrough otherwise.

## Checks

- `shell.md` has its navigation, layout areas, breakpoints and shared patterns.
- Its `elements:` nav block lists the same destinations as `## Navigation`, in the same order.
