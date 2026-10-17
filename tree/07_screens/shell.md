---
path: _concept/07_screens/shell.md
summary: the app frame — navigation, layout areas, breakpoints, shared patterns
writers: [experience-shell]
---

# _concept/07_screens/shell.md

The frame every screen appears inside: navigation, layout areas, breakpoints, and the conventions screens are not each meant to re-decide. `experience-shell` writes exactly this one file and no screen spec. It normally runs after the feature loop, so the frame is drawn around screens that exist; in the reverse flow, where it runs before `spec-feature`, it is drawn around the screens the codebase already has. The walkthrough renders the `kind: nav` element below as the app nav on every screen page; without it the renderer derives a default nav, one link per screen grouped by feature directory, and flags it provisional.

## Format

Frontmatter: `elements:` carries the `kind: nav` block (schema in `tree/07_screens/README.md`) and `last_updated` as in `tree/README.md § Frontmatter every markdown artifact carries`. Body sections, named exactly because the renderer's spec panel shows them:

- `## Navigation` — the destinations, grouped by featureset, each by the screen id it already has, with prominence.
- `## Layout Areas` — header, primary navigation, content region and anything persistent beside them: what each holds and what stays put while the content changes; a short ASCII sketch carries this faster than three paragraphs.
- `## Responsive Behaviour` — the breakpoints, and what the navigation becomes below each.
- `## Shared Patterns` — page-header composition, breadcrumb placement, empty, loading and error states, where confirmations and destructive actions surface.

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

1. **Read what the app is for and where its screens are.** `brief.md` for the hero flow, `05_features/featuresets.md` for the featuresets and their features, `04_journeys/` for the order users move through them, and `03_brand/tokens.json` for the palette, type scale and spacing the frame is drawn in — reference brand values by name, because a hex invented here diverges from the tokens the renderers use. The screens come from `07_screens/<feature_slug>/*.md`: each file's `id` and title are a candidate nav destination. Where `07_screens/` holds none (the reverse flow), take them from the screens recorded in `02_grounding/findings/screens.md` and say in `shell.md` which source each destination came from. With neither, stop and name the missing step — `spec-feature` or `concept-reverse` — because a nav drawn without screens behind it is a nav invented here.
2. **Derive the navigation from those screens.** Every destination is a screen a spec or a finding names, under the screen id it already has; a destination nothing backs is dropped. Group them by featureset and let the journey stage (`stories.yaml § stages`) decide prominence: hero and vital journeys earn primary navigation, hygiene flows sit behind a settings or admin entry. A nav with one item per screen is a menu of the file system rather than of the product.
3. **Describe the layout areas** as the format above says.
4. **Settle the responsive behaviour once, here** — decided anywhere else, it gets decided differently on every screen.
5. **Write the shared patterns** every screen reuses; each is a decision a feature spec would otherwise make alone, and inconsistently.
6. **Mirror the navigation into the `elements:` block.** `shell.md`'s own frontmatter carries a `kind: nav` element whose `items[]` are the destinations from step 2, in the same order, each with its `target`, shaped per `tree/07_screens/README.md § Content fidelity` — an unmirrored `## Navigation` section renders as a nav the user never designed. A target taken from the findings resolves once `spec-feature` writes that screen under the same id; until then it is reported as an unresolved target rather than a failure.
7. **Show the frame to the user in their terms** — where things live, what is always on screen, what happens on a phone — and iterate until they approve. Then point at the next step: `spec-feature` in the reverse flow, where it writes every screen inside this frame, and the walkthrough otherwise.

## Checks

- `shell.md` has its navigation, layout areas, breakpoints and shared patterns.
- Its `elements:` nav block lists the same destinations as `## Navigation`, in the same order.
