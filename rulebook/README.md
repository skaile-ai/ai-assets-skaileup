# The app-design rulebook

The collection-level rules for how an application behaves: where each object's information lives, which surface edits what, how people find things and move between them, how a screen is laid out, how the app answers. An app's `APP-DESIGN.md` adopts these rules and records its decisions against them; a skill that interviews, specifies a screen, derives a shell or checks source cites them by id instead of re-deriving them.

**The app's decided entry wins over the rule it cites.** The rulebook is what a decision starts from, not what it must end at. An entry that applies a rule in a different form says so (`adapt` after the id) and is not an exception; an entry that removes a rule's obligation is listed in the app's `§ Exceptions` with its reason, so a reader neither follows nor overrules it in silence.

## Files

| file | holds |
|---|---|
| `rules.md` | the invariants `P1`–`P31`, then the `## Heuristics` table `H1`… |
| `defaults.md` | the bundle `DF1`… of rules independent projects re-derived identically, then the decisions that legitimately diverge |
| `floorplans/<id>/` | one directory per floorplan: `README.md` (regions, tiers, posture, density, responsive transformation, constraints, sketch, when not to use) and `preview.html` |

## How to read it

1. **Invariants (`P`).** A rule that holds in every app unless the app records an exception. Each has a statement, one clause of why, and a source with a strength grade. Where a rule fixes a number it points at a heuristic.
2. **Heuristics (`H`).** A value or range that practitioners use and sources do not fix: a field limit, a row height, a latency threshold. Nothing in `## Heuristics` is enforced until the app adopts a value in `APP-DESIGN.md`; the entry that adopts it names the `H` id, and a check measures against that value alone.
3. **Defaults (`DF`).** Rules that two or more projects here re-derived identically, offered as one bundle. An app adopts the bundle with one line, and a default it declines is one row in `§ Exceptions` citing the `DF` id. A choice that projects made differently is not a default: it sits under `## Decisions, not defaults` in `defaults.md`, and the app decides it.
4. **Floorplans.** Layout templates chosen per `P18`: the shell frame once for the app, a screen floorplan once per screen.

A P-rule is an invariant the app may override only by a recorded exception; an H value is adopted per app, with no exception needed to pick any value in its range.

## Ids

- Rules are `### P<n> — <title>` headings in `rules.md`; heuristics are rows `H<n>` of its `## Heuristics` table; defaults are `### DF<n> — <title>` headings in `defaults.md`.
- An id is unique across the whole rulebook and is never reused. `P1`–`P17` keep the numbers they had before the rulebook was split out, so files that cite them stay readable.
- A rule that is dropped keeps its heading, with the statement `retired: <date>, <reason>` and the id of its replacement where one exists. Its number is not reassigned; a revised rule keeps its id.
- Cite a rule by id (`P5`, `H1`, `DF4`) inside an entry, and a section by its file and heading as inline code, `rulebook/rules.md § P5 — Edit-surface ladder`.

## Strength grades

Every source carries one grade. A reader weighs a finding by it; a skill never states a heuristic more firmly than its grade.

| grade | means |
|---|---|
| `standard` | a published guideline, pattern library, book or paper from a named body or author; read in the original unless `rules.md § Sources` says otherwise |
| `field` | re-derived independently in two or more projects here, or seen in the code of two or more |
| `heuristic` | a practitioner rule of thumb or a single project's choice: a prompt to check, not proof of a defect |
| `owner` | decided for this collection by its owner; stands without outside evidence and changes only by the owner |

A rule that rests on several sources takes the strongest grade among them and names each source.

## Adding or retiring

- **A rule** takes the next free `P` number, with an id heading, a statement, one clause of why and a source with a grade. A numeric value belongs in a new `H` row, not in the statement.
- **A heuristic** takes the next free `H` number and fills every column of the table.
- **A default** needs two independent projects that arrived at the same rule; it cites the `P` rule it implements and each project's entry.
- **A floorplan** is added in four parts, none of which is optional:
  1. `floorplans/<id>/README.md`, shaped as below;
  2. `floorplans/<id>/preview.html`, shaped as below;
  3. a rule that cites it, normally in the list of `P18`, with the id in backticks, so no floorplan sits in the catalogue unreachable;
  4. an exemplar row in `docs/floorplan-exemplars.md`, which holds the real-project paths and is not part of this asset.

  **README shape.** Frontmatter, all five keys required: `id` (equals the directory name), `kind` (`shell` or `screen`), `summary` (at most 80 characters: the task it serves), `posture` (`sovereign`, `transient` or `auxiliary`), `density` (`compact`, `default` or `comfortable`). Then a `# <id> — <Title>` heading, one paragraph on the task it serves and the rule that selects it, and these six `##` sections: `Regions` (a table `region · role · default tier · holds`, role one of primary, secondary, tertiary, navigation, chrome, tier 1, 2, 3 or —, then one line on where tier 3 may surface), `Posture and density`, `Responsive` (wide at 960 px and up, narrow at 640 px and down: what folds, collapses or becomes an overlay or bottom bar), `Interaction constraints` (what may be a drawer, what must stay a page, which surfaces may edit), `Sketch` (a `text` fence: ASCII wide, then narrow, with the region names of the table) and `When not to use` (naming the floorplan to use instead by id).

  **Preview rules.** One self-contained file: `<!doctype html>`, a viewport meta tag, `<title>Floorplan preview — <id></title>`, an inline `<style>` and at most a tiny inline script to open and close a drawer, peek or popover. No external reference of any kind: no `http://` or `https://` string, no `<link>`, no `<script src>`, no image, no web font. `:root` defines the neutral `--fp-*` variables (`--fp-bg`, `--fp-surface`, `--fp-surface-2`, `--fp-border`, `--fp-fg`, `--fp-muted`, `--fp-accent`, `--fp-tier3`, `--fp-radius`, `--fp-gap`, `--fp-font`) and the page takes every colour from them, with no brand. Each region element carries `data-region="<name from the Regions table>"` plus `data-tier` or `data-role`, and the shared label CSS shows the name. The sample data is the one fictional design-studio project tracker every preview uses; tier-3 attributes appear only behind a peek, popover or disclosure. Wide and narrow sit in one file behind `@media (max-width: 640px)`, and the narrow layout implements the README's `Responsive` section. The gate (`floorplan-shape`, `floorplan-cited`) checks the frontmatter values, the six headings, the preview's presence, its self-containment and `--fp-bg`, and that a rule cites the id; a person still opens each preview at both widths.
- **Retiring** follows the id rule above: the heading stays, marked `retired`.
