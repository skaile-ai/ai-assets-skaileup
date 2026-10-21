---
path: _concept/02_grounding/findings/interaction.md
summary: surfaces, editors, save models, messages, search as the code has them today
owner: [concept-reverse]
may_propose: []
---

# _concept/02_grounding/findings/interaction.md

The census of how the code lets a user work today: the surfaces, editors, finders, save models and message channels it has. `experience-interaction` seeds `APP-DESIGN.md` from it when the project already exists, and `quality-interaction` reads it as the baseline it judges the source against; a surface missing here is a decision nobody sees.

## Format

Frontmatter per `tree/02_grounding/findings/README.md` with `scope: interaction` and the freshness fields (`paths`, `source_sha`, `last_updated`). Every value carries a repository-root `file:line` citation and its grade in `extraction_confidence`. Sections:

- **Surfaces** — one row per overlay (modal, drawer, popover, palette): purpose (editor, confirm, picker, info), host component, trigger.
- **Editors** — per object type, the component that owns the field set and the submit, and its surface kind (modal, drawer, popover, inline, page editor).
- **Finders** — command palette, global search, shortcuts, action definitions.
- **Save models, messages, popups and buttons** — per `rulebook/rules.md § P14` to P17: autosave or explicit save and the leave guards; toast, inline and empty-state channels with the confirm components; tooltips and menus; icon-only buttons, solid-primary counts per view and destructive buttons.
- **Unread** — the regions of a large app read by sampling only; the last section of the file.

```markdown
| surface | purpose | host | trigger | grade |
|---|---|---|---|---|
| modal | create object | `app/components/CreateModal.vue:1` | header button `app/layouts/default.vue:34` | extracted |
```

A surface seen only in a vendored UI library is not in the census. A rule with no hit is `needs_review` with the grep that found nothing, because an absence nobody searched for reads exactly like one nobody found.

## Where UI sits per stack

Where screens, objects, editors and finders hide, per stack. `concept-reverse` reads it to write this file, and `quality-interaction` reads it to check the app's source against `APP-DESIGN.md` (the roots the stack names, or `src/`; `app/` and `server/` in Nuxt). Read the row for the detected stack; when a pattern is missing, extend the table rather than guess. The rules it serves are `rulebook/rules.md`; the shape of `APP-DESIGN.md` is `tree/APP-DESIGN.md § Format`.

### Intent and vocabulary

Before judging, read the app's `APP-DESIGN.md` at the project root (`tree/APP-DESIGN.md § Reading it`), the glossary (`tree/glossary.md § Where the words live`), the decision records (`docs/adr/`, or `docs/decisions/`, `_devlog/decisions/`), any UI or design concept (`docs/*konzept*`, `docs/*design*`, `docs/ui*`, `docs/*wireframe*`, UX documents inside `_concept/` — headings first, then the parts a rule touches) and `CLAUDE.md`/`AGENTS.md`. They name the objects (P13) and record deviations decided on purpose. A decision such a document holds that `APP-DESIGN.md` lacks becomes an entry citing it, not a finding.

### Screens (routes)

| stack | where |
|---|---|
| Nuxt | `app/pages/**` or `pages/**` (file = route, `[id]` = param); `layouts/`; `definePageMeta` |
| Next.js | `app/**/page.tsx` (App Router), `pages/**` (Pages Router); `layout.tsx`; parallel/intercepting routes `@slot`, `(.)x` are modal routes |
| SvelteKit | `src/routes/**/+page.svelte`, `+layout.svelte` |
| React SPA | router config: `createBrowserRouter`, `<Route path=`, TanStack `createFileRoute` |
| Vue SPA | `createRouter({ routes })` |

Tabs, steps and sub-views that change content without a route count as screens when they show a different object or task; note them as `route#tab`. Overlays mounted in the layout (create modals, palettes, inbox drawers) are screens too and are easy to miss.

### Objects (types)

In priority order: database schema (`schema.prisma`, Drizzle `pgTable`, migrations, Directus `snapshot.yaml`/collections, Supabase types), shared TS types/Zod schemas (`shared/`, `types/`, `*.schema.ts`), API routes (`server/api/**`, `app/api/**`), then the nouns in page titles and nav labels. The schema's name is evidence, the UI's label is what the user calls it — record both when they differ. A hand-maintained type file can drift from the real schema; mark names taken only from call sites as inferred.

### Editors and surfaces

| surface | grep for |
|---|---|
| modal | `Modal`, `Dialog`, `UModal`, `<dialog`, `AlertDialog`, `v-dialog`, `showModal` |
| drawer | `Drawer`, `Sheet`, `Slideover`, `USlideover`, `SidePanel`, `Offcanvas` — in Nuxt UI `USlideover` is the side panel, `UDrawer` a bottom sheet |
| popover | `Popover`, `UPopover`, `Popper`, `Dropdown` containing inputs; menus of actions (`UDropdownMenu`, `UContextMenu`) are not editors |
| inline | `contenteditable`, `@blur`/`onBlur` + save call on a single input, `isEditing` toggles, `InlineEdit`, `EditableText` |
| page editor | a route whose component holds a `<form>`/`UForm`/`useForm` bound to one object |

An *editor* is the component that owns the field set and the submit for one object type. Find them by the save call (`$fetch(... method: 'PATCH'|'POST')`, `useMutation`, `updateItem`, `createItem`, server actions) and walk up to the component that renders the inputs. Two components posting to the same endpoint with different field sets are two editors for one type.

Read every overlay match for its *purpose* — editor, confirm, picker, info — and its *host*: a surface census (one row per overlay: purpose, host, trigger) is where bespoke confirm dialogs and stacked modals show up. Stacking is state, not markup: an editor whose open-flag stays set while a confirm opens is a modal on a modal.

### Finders

| thing | grep for |
|---|---|
| command palette | `cmdk`, `kbar`, `UCommandPalette`, `UDashboardSearch`, `UDashboardSearchButton`, `CommandDialog`, `CommandPalette`, `ninja-keys`, `meta+k`, `ctrl+k`, a key handler on `metaKey`/`ctrlKey` with `key === "k"`, `defineShortcuts` |
| global search | a search input in the layout/header component, `/search` route, search API endpoint |
| shortcuts | `useMagicKeys`, `hotkeys`, `useHotkeys`, `defineShortcuts`, `keydown` listeners on `window`/`document` |
| action definitions | arrays of `{ label, icon, click/onSelect }` reused by menus, or `defineAction`/`defineForgeAction`/`registerAll` entries — the seed of an action registry |

A palette or finder component counts as present only where a layout or page renders it: grep for its tag outside its own file. One that is defined and registered but never rendered is `needs_review`, with the grep that found no mount.

### Saving, messages, popups and buttons

| rule | grep for |
|---|---|
| save model (P14) | autosave: `watchDebounced`, `useDebounceFn`, `@change`/`@update:model-value` with a save call; explicit: `type="submit"`, `@submit`; leave guards: `beforeunload`, `onBeforeRouteLeave`, `useBlocker`, `dismissible`, `prevent-close`, `@close:prevent` |
| messages (P15) | toasts: `useToast`, `toast.add`, `toast(`, `sonner`, `notify`; inline: `UAlert`, `Alert`, `role="alert"`, the app's own error strip; empty states: `UEmpty`, `EmptyState`, `v-if="!items.length"` |
| popups (P16) | `UTooltip`, `Tooltip`, `v-tooltip`, native `title=` on interactive elements; `UPopover`; `UDropdownMenu`, `DropdownMenu`, `Menu` |
| buttons (P17) | icon-only: a button with `icon=` and neither `label=` nor slot text; `aria-label`; hierarchy: `variant=`/`color=` per view, count of solid primaries; destructive: `color="error"`/`danger`/`destructive` |

Classify toasts by colour or type: error- and warning-coloured toasts are where P15 findings come from, unless `APP-DESIGN.md` decides that channel. Count buttons by parsing tags, not by line grep — a multi-line `<UButton …>` splits its attributes across lines. A "view" is a page or an overlay (modal, drawer) together with the components it renders in place; a mounted component's own overlay is a view of its own. The scanner reports per file, so add up a page's solid primaries with those of the components it renders in place before judging P17. For Vue, JSX and Svelte markup, adapt the tag names and the stack's default variant:

```python
import re, sys, pathlib  # python3 scan.py app/  -> one line per button
TAG = re.compile(r'<(UButton|Button|button)\b((?:[^>"\']|"[^"]*"|\'[^\']*\')*?)(/>|>(.*?)</\1>)', re.S)
for f in pathlib.Path(sys.argv[1]).rglob('*'):
    if f.suffix not in ('.vue', '.tsx', '.jsx', '.svelte') or 'node_modules' in f.parts: continue
    s = f.read_text(errors='ignore')
    for m in TAG.finditer(s):
        a, inner = m.group(2), m.group(4) or ''
        text = re.sub(r'<[^>]+>', '', inner).strip()
        has_icon = bool(re.search(r'\bicon=', a) or re.search(r'<(UIcon|Icon|svg)\b', inner))
        icon_only = has_icon and not re.search(r'(?<![\w-]):?label=', a) and not text
        # stack default: Nuxt UI's UButton is solid primary; a raw <button> has no variant
        solid = m.group(1) != 'button' and not re.search(r'\b(variant|color)=', a)
        tooltip = 'Tooltip' in s[max(0, m.start() - 300):m.start()]
        title = bool(re.search(r'(?<![\w-]):?title=', a))  # native title: fails keyboard focus (P16)
        print(f"{f}:{s.count(chr(10), 0, m.start()) + 1}", f"icon_only={icon_only}",
              f"named={'aria-label=' in a}", f"tooltip={tooltip}", f"title={title}", f"solid={solid}", sep='\t')
```

A button inside an `aria-hidden` or `inert` wrapper (a measuring copy of a toolbar) is not one users see: drop it from the counts.

### Generated and vendored code

Skip `node_modules/`, `.nuxt/`, `.output/`, `.next/`, `dist/`, `build/`, `storybook-static/`, lockfiles, `*.stories.*` and vendored third-party code. A vendored UI library is evidence of available components, not of app screens; the app's own module under `vendor/` is app code. A workspace package or submodule the app imports (`packages/*`, a shared `forge-common/`) is app code where the app mounts or calls its components: census the overlay from the app's side, with the package file as its host, and leave the rest of the package unread. Read a large app in full for overlays and editors and by grep per rule for the rest; sample files too large to read whole the same way, and end the census with a list of what went unread.

### Verifying citations

A cited `file:line` that does not exist turns a finding into an opinion. Cite the full path from the repository root every time, also on the second mention — `druck/[id].vue:12` or `components/X.vue:5` under an unstated root can be neither opened nor checked. Check every citation mechanically before finishing — existence and range, run from the repository root:

```sh
grep -ohE '[^[:space:]:`"(,;]+\.(vue|[cm]?[jt]sx?|svelte|py|md|ya?ml|json):[0-9]+(-[0-9]+)?' <artifacts> | sort -u |
while IFS=: read -r f l; do [ -f "$f" ] || { echo "missing $f"; continue; }
  [ "${l%-*}" -le "$(wc -l < "$f")" ] || echo "out of range $f:$l"; done
```

A bare file name (`Abschnitt.vue:12`) reports as missing — that is the point: cite it from the root. Shorthand that leans on an earlier mention escapes the script, so this must print nothing: ``grep -nE '`:[0-9]+' <artifacts>``. Prose locations ("lines 40–60 of `X.vue`") are not citations; write them as `path:40-60`. Then read a sample of the cited lines for meaning — the script proves the line exists, not that it says what the finding claims.

## Writing it

1. Read the row of `## Where UI sits per stack` for the stack `tree/02_grounding/findings/README.md § Extracting (concept-reverse)` detected; the code root is wherever the app's source is (`src/`, `app/` + `server/`, a workspace package).
2. Build the surface census and the editor per object type per `### Editors and surfaces`.
3. Add the finders per `### Finders`, and the save models, message channels and confirm components per `### Saving, messages, popups and buttons`.
4. Grade every value; give a rule with no hit `needs_review` with the grep that found nothing. A large app gets every overlay and editor read and the other rules sampled by grep, with the unread regions listed at the end of the file.
5. Verify the citations per `### Verifying citations`.

## Checks

- Every value carries a repository-root `file:line` that exists and a grade.
- No surface in the census comes from vendored UI-library code alone.
- Every rule of P14–P17 has a row or a `needs_review` entry naming its grep.
- `scope`, `paths`, `source_sha` and `last_updated` are set, and a row outside `paths` that predates `source_sha` carries `as_of`.
