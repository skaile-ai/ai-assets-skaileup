---
path: _concept/02_grounding/findings/screens.md
summary: page components behind the routes, with bindings, interactions and states
writers: [concept-reverse]
---

# _concept/02_grounding/findings/screens.md

The page components behind the routes in `tree/02_grounding/findings/routes.md`: evidence that
`experience-shell` and the `spec-feature` loop read. Feature and screen specs are written from it
by the skills that own those trees.

## Format

Frontmatter per `tree/02_grounding/findings/README.md`. Per screen, with its defining file cited:
the layout or template it wraps in; the entities it fetches or submits; the interactions a user
has (buttons, forms, links, and where each leads); the states the component renders
conditionally (loading, empty, error, populated); and the guard or middleware protecting it,
which is the evidence for who is allowed there.

## Writing it

Find each page component by framework:

| framework | where the page component lives |
|---|---|
| Nuxt | `pages/**/*.vue`, with `layouts/` for the frame |
| Next.js | `app/**/page.tsx`, `pages/**/*.tsx` |
| Vue Router | `views/`, `src/pages/` |
| React Router | `src/routes/`, `src/pages/` |
| SvelteKit | `src/routes/**/+page.svelte` |
| Django | `templates/**/*.html` |
| Rails | `app/views/**/*.erb` |

## Checks

Every screen entry cites its component file, which exists on disk.
