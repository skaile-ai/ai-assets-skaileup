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
  1. `floorplans/<id>/README.md` with its id, the task it serves, its regions and each region's default tier, posture and density defaults, responsive transformation, interaction constraints (what may be a drawer, what must stay a page), an ASCII sketch and when not to use it;
  2. `floorplans/<id>/preview.html`, one self-contained file with neutral CSS variables, sample data, and a wide and a narrow view;
  3. a rule that cites it, normally in the list of `P18`, so no floorplan sits in the catalogue unreachable;
  4. an exemplar row in `docs/floorplan-exemplars.md`, which holds the real-project paths and is not part of this asset.
- **Retiring** follows the id rule above: the heading stays, marked `retired`.
