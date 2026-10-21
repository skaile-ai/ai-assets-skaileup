---
path: _concept/07_screens/shell.md
summary: the app frame — shell frame, navigation model, the one destination list
owner: [experience-shell]
may_propose: []
---

# _concept/07_screens/shell.md

The frame every screen appears inside: which shell frame holds it, the navigation model it realises, the one destination list every navigation surface renders, and the conventions screens are not each meant to re-decide. `experience-shell` writes exactly this one file and no screen spec; it needs no feature and no screen to exist, so a frame can be drawn before, between or after the screens it holds. Where `APP-DESIGN.md` exists the frame follows its § Navigation model, § Objects and the message, edit and modal entries, read per `tree/APP-DESIGN.md § Reading it`. The walkthrough renders the `kind: nav` element below as the app nav on every screen page; without it the renderer derives a default nav, one ungrouped link per screen in `screen_id` order labelled by the screen's `title`, and flags it provisional.

## Format

Frontmatter, then body sections named exactly because the renderer's spec panel shows them:

```yaml
---
shell_frame: shell-sidebar       # a floorplan id of kind `shell`: shell-sidebar | shell-topbar | shell-mobile-tabs | shell-dock
organization: hybrid             # object-led | task-led | hybrid — from APP-DESIGN.md § Navigation model
primary_surface: sidebar         # sidebar | topbar | tabs | rail+drawer | bottom-tabs | none
navigation: decided              # decided | provisional — provisional while the model is a fallback nobody decided
elements:                        # the kind: nav block (schema: tree/07_screens/README.md)
  - id: app-nav
    kind: nav
    label: "Main navigation"
    states: [default]
    items:                       # same destinations, same order as ## Navigation
      - { label: "Tasks", target: task-list }
last_updated: YYYY-MM-DD
---
```

- `## Navigation` — the one destination list: each destination by the `screen_id` it has or will have, its group, its badge source and its prominence (primary, or pinned for a narrow tab bar or pill). Under `navigation: provisional` its first line says so (`Provisional: grouped by feature set because no navigation model is decided — see APP-DESIGN.md § Open`), so the fallback is not mistaken for the design.
- `## Layout Areas` — what the app puts into the regions of its `shell_frame` (its `§ Regions` in `rulebook/floorplans/<shell_frame>/README.md`): header actions, the persistent context line, what stays put while the content changes.
- `## Responsive Behaviour` — the frame's own `§ Responsive` is the default; this section records only the breakpoints the app moves and what the navigation becomes below each.
- `## Shared Patterns` — layout only: page-header composition, breadcrumb placement, which regions persist, and what the content region shows while loading. Empty, error, confirmation, message and editing patterns are not decided here: they cite the `APP-DESIGN.md` MSG, EDIT and MOD entries by id.
- `## Proposed interaction patterns` — only when `APP-DESIGN.md` is absent: the empty, error, confirmation, message and editing patterns this frame needs, written as proposals for `experience-interaction`.

## Writing it

1. **Resolve the facts** (`tree/README.md § How a skill runs`, rule 1). Read, in any order and none required: `APP-DESIGN.md` for § Navigation model (`organization`, `primary_surface`) and § Objects; `_concept/glossary.md` for each object's `navigation` axis; `_concept/02_grounding/findings/routes.md` and `screens.md` for the destinations the code already has (where the code holds routes and the findings do not, run `concept-reverse` scoped to `routes`); the screens already written under `07_screens/` for their `screen_id` and `title`; `_concept/05_features/featuresets.md`, `04_journeys/stories.yaml` for the order users move through the app, and `03_brand/brand.tokens.json` for the palette, type scale and spacing the frame is drawn in (format: `tree/03_brand/brand.tokens.md`) — reference brand values by name, because a hex invented here diverges from the tokens the renderers use. What none of them settles goes into the batch of step 3.
2. **Derive the destination list.** Under a decided navigation model (`rulebook/rules.md § P12`, `§ P22`) primary navigation lists the indexes of the objects whose `navigation` axis is `primary` and the few workspaces its NAV entries name; supporting objects sit behind their parent. Where there is no `APP-DESIGN.md`, take the destinations from the findings and the screens, and let the journey stage (`stories.yaml § stages`) decide prominence: hero and vital journeys earn primary navigation, hygiene flows sit behind a settings or admin entry. A destination names the `screen_id` that serves it; one whose screen is not written yet is listed for `experience-screen` in the completion summary and resolves as soon as that screen exists. A nav with one item per screen is a menu of the file system rather than of the product.
3. **Decide what is open, in one batch** (`tree/README.md § How a skill runs`, rules 2 and 5): the organization and primary surface when no model is recorded, the groups, the badges, which entries are pinned for a narrow screen. Without a decided model the list is grouped by feature set when `featuresets.md` exists, else left ungrouped; the file records `navigation: provisional` and the visible line of `## Navigation`, and the completion summary names `experience-interaction` as the owner of the decision.
4. **Choose the shell frame** with `rulebook/rules.md § P18` and the four `kind: shell` floorplan READMEs, following the primary surface by the map in `rulebook/rules.md § P22`, which covers every value: `shell-dock` is taken for `none` and for a `sidebar` whose app is a desktop-native docked tool, never chosen on the kind of tool alone. Where `APP-DESIGN.md` names an archetype (`rulebook/archetypes.md`), its row's frame is the starting point, and a different frame is a NAV entry there. The choice is written once for the whole app; a frame that deviates from the model is an exception for `APP-DESIGN.md`, not a quiet override.
5. **Write the sections** as the format says, settling the responsive behaviour once, here — decided on each screen it is decided differently on every one. Empty, error, confirmation, message and editing patterns are cited by id from the `APP-DESIGN.md` MSG, EDIT and MOD entries; without the file, record them under `## Proposed interaction patterns` — a pattern this skill settles alone is the one every screen would otherwise make inconsistently.
6. **Mirror the destination list into `elements:`.** The frontmatter carries a `kind: nav` element whose `items[]` are the step-2 destinations, in the same order, each with its `target`, shaped per `tree/07_screens/README.md § Content fidelity` — an unmirrored `## Navigation` section renders as a nav the user never designed. A target whose screen is not written resolves once `experience-screen` writes it under that id; until then it is reported as an unresolved target, not a failure.
7. **Show the frame to the user in their terms** — where things live, what is always on screen, what happens on a phone — and iterate until they approve; then write `approved:` per `tree/README.md § Frontmatter every markdown artifact carries`.

## Checks

- `shell_frame` is a directory under `rulebook/floorplans/` whose README has `kind: shell`, and it matches `primary_surface` per `rulebook/rules.md § P22`.
- `shell_frame` equals the frame of the archetype `APP-DESIGN.md § Navigation model` declares, or `APP-DESIGN.md` has a NAV entry naming the departure.
- `organization` and `primary_surface` equal `APP-DESIGN.md § Navigation model` when that section decides them; otherwise `navigation: provisional` and the visible line under `## Navigation` are both present.
- The `elements:` nav block lists the same destinations as `## Navigation`, in the same order, with every `target` a `screen_id`.
- No destination list exists elsewhere: sidebar, rail, drawer, tab bar and palette entries are all rendered from this one.
