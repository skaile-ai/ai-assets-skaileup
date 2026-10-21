# Renderer: astro

A built Astro site at `_concept/09_mockup/walkthrough/astro/`, Tailwind-styled from the brand
tokens. Route item 3 of `../../SKILL.md` expands into steps 1–4 below; the shared
`tree/09_mockup/walkthrough/README.md` still owns everything else.

## Why this renderer resolves everything up front

The `.astro` templates are scaffolded **once**, at init, and then belong to the user. They
run at build time, long after the agent that could resolve a target or derive an auto-slug
id has finished. So resolve everything in the in-memory model and hand the templates a
fully-resolved `src/data/specs.json`: the template interpolates `el.href ?? '#'` and derives
nothing itself. static-html may resolve at render time because its templates run then too.

Three consequences, all astro-only:

- **Hrefs are root-relative and extension-less** — `/screen/<screen>`, `/floorplan/<screen>`,
  `/journey/<id>`, `/`. The build emits real `.html` files (`build.format: 'file'`), but the served URL is the
  clean form.
- **`provisional: true` sits on the element object**, and on every normalised `items[]` entry,
  rather than in a separate top-level `auto_slugged[]` array. The `auto_slugged` warning entry
  is still required.
- **`items[]` ids are derived into `specs.json`**, not at render time. The derivation itself is
  the contract's (`tree/09_mockup/walkthrough/README.md § items[] id derivation`) — this renderer only
  changes *when* it runs.

Before the steps, read `_concept/09_mockup/feedback/devlog.md` when it exists and treat each
applied line for a screen or feature file you are about to render as a constraint — a
regeneration that reverts a change a stakeholder already asked for reads as the tool ignoring
the feedback round.

## Steps

1. **Detect the mode.** `astro.config.mjs` absent → **init**: copy `scaffold/` into the project
   and run `bun install`. Present → **update**: the scaffold is the user's, so leave
   `astro.config.mjs`, `tailwind.config.mjs` and every `.astro` file untouched, and check for
   staleness — if `src/pages/screen/[...slug].astro` lacks the literal `el.href`, `spec-panel` or `floorplan-frames`, or `src/pages/floorplan/[...slug].astro` is absent,
   record a `stale_scaffold` warning naming the fix (delete the scaffold to regenerate, or port
   the template changes by hand). Run the check before regenerating, so the warning describes
   the scaffold as it stood at the start of the run. It is a warning, not a failure; the build
   proceeds and ships whatever the stale template renders.
2. **Write `src/data/specs.json` and `src/styles/global.css`** on every run, overwriting.
   Shape, and the `specs.json` → `manifest.json` projection: `specs-json.md`. `global.css` is
   the Tailwind base, a `.floorplan-notice` rule (dashed amber border, padded, so the no-floorplan notice is visible), plus one `--token-*` line per token of `03_brand/brand.tokens.json`,
   flattened per `tree/03_brand/brand.tokens.md § Flattening to CSS`, and a `.dark { … }` block
   from `brand.dark.tokens.json` when that file exists. On update runs, compare the `:root`
   token count against the CSS var count in the existing file's `:root` first; a mismatch means
   `tailwind.config.mjs` needs a hand edit — record `stale_tailwind_config`.
3. **Build** with `bun run build` from the project root. On non-zero exit, print the full
   stderr, stop, and leave `manifest.json` alone.
4. **Write `manifest.json` from the in-memory model, not by serialising `specs.json`** — the
   two shapes differ, and `specs-json.md` lists the template-only fields the manifest must not
   carry.

## Floorplan frames

The frame document is built in the in-memory model like every other resolved value (the contract: `tree/09_mockup/walkthrough/README.md § Floorplan frame`) and handed to the templates as `floorplan_frame_html`; `src/pages/floorplan/[...slug].astro` emits it unchanged as `floorplan/<screen>.html`, and the screen page embeds it twice. The rulebook is read at generation time from the installed contract `<contracts>/app-design-rulebook/`; `validator.py --rulebook <dir>` takes the same path and defaults to the harness's `<contracts>/app-design-rulebook/` under the working directory, then to the `rulebook/` of the collection checkout.

## The astro config is load-bearing

`outDir: '.'`, `emptyOutDir: false`, `build.format: 'file'`, and `getStaticPaths()` slugs
without trailing slashes. These four together are what put the built HTML where the feedback
cluster expects it and keep the previous build's files alive. A `dist/` directory appearing
under the project root means `outDir` drifted: fail with that message rather than shipping a
walkthrough the annotator cannot find. `scaffold/astro.config.mjs` already encodes all four —
copy it rather than writing one.

Two failures are worth stopping for: `bun install` and `bun run build` exiting non-zero.
Everything else in the shared `warnings[].kind` enum is soft — render the node, record the
warning, keep going — plus this renderer's own `stale_scaffold` and `stale_tailwind_config`.
