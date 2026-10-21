---
path: [_concept/09_mockup/prototypes/<screen>/a.html, _concept/09_mockup/prototypes/<screen>/b.html]
summary: one screen's early prototype — a floorplan preview with the screen's sample data
owner: [experience-screen]
may_propose: []
---

# _concept/09_mockup/prototypes/<screen>/a.html, b.html

A floorplan's `preview.html` with the screen's own sample data and region contents swapped in, in the floorplan's neutral styling. It answers one question, "is this the right layout for this task?", before the screen is specified: the user opens it wide and narrow, says what is wrong, and the answer fixes `floorplan:` and `regions:` in the screen spec. It is a view, not a spec: the screen file stays the source of truth and a prototype is regenerated, never edited by hand to carry a decision.

## Format

One self-contained HTML file per variant, `a.html` for the recommended floorplan and `b.html` only when the user asks for a second variant (another floorplan, or the same floorplan with different region bindings or density).

- It is the floorplan's `rulebook/floorplans/<id>/preview.html` with its structure, `data-region` attributes, `data-tier` / `data-role` attributes, `--fp-*` variables and media queries kept, so the wide and narrow behaviour is the floorplan's own.
- `<title>` reads `Prototype — <screen_id> (<a|b>)` and `<meta name="floorplan" content="<floorplan id>">` names the floorplan.
- Region contents follow the screen's `regions:` bindings: the labels are glossary terms, each row, card or page is the bound representation, tier-1 attributes sit in the primary region and tier 3 behind the preview's own disclosure.
- Sample data is realistic and short (about 4–8 rows), taken from the seed's `populated` scenario, the findings, or the user's own words, never lorem ipsum.
- Neutral styling: no brand tokens, no external reference of any kind (`http://`, `https://`, `<link>`, `<script src>`, `<img>`, web fonts), at most the preview's own tiny inline script for opening and closing a drawer, peek or popover.

## Writing it

1. **Pick the variants.** `a` is the floorplan `tree/07_screens/[screen].md § Writing it` step 4 recommends; `b` exists only on request and differs in the one thing the user is unsure of, named in its first line under `<title>`.
2. **Gather the sample data** from the sources in `## Format`, with the screen's glossary terms and the attribute tiers of `APP-DESIGN.md § Information hierarchy` where that exists; an attribute without a tier is shown at tier 2.
3. **Copy the preview and swap the content**, region by region, per the screen's bindings; a region the screen leaves unbound shows only its name and an empty block, because preview content left in place reads as a decision.
4. **Open it for the user** in a browser, tell them the two widths to check (wide, and 640 px or narrower, the floorplan's `§ Responsive`), and ask what to change in one batch (`tree/README.md § How a skill runs`, rules 2 and 6). Regenerate on each answer; the settled choice goes into the screen spec, and a variant the user rejected stays on disk as the record of what was compared.

## Checks

- Each file passes the preview rules of `rulebook/README.md § Adding or retiring` (self-contained, neutral variables, no external reference).
- Every `data-region` value is a region id from the floorplan's `§ Regions`.
- `<title>` and the `floorplan` meta name the screen and the floorplan the screen spec ends up with, or the spec says why it chose differently.
