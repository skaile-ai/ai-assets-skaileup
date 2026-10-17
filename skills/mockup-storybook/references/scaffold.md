# Scaffold — the files step 2 writes

All paths are under `_concept/09_mockup/storybook/`. Every value in angle brackets is either
one of the six stack values resolved in step 1 or a key from
`_concept/03_brand/tokens.json`.

## `package.json`

```json
{
  "name": "storybook",
  "private": true,
  "scripts": {
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build",
    "build": "storybook build"
  },
  "devDependencies": {
    "storybook": "^8.0.0",
    "<storybook_addon>": "^8.0.0",
    "@storybook/addon-essentials": "^8.0.0",
    "typescript": "^5.0.0"
  }
}
```

Add whatever else the resolved addon needs — a React-on-Vite addon wants `vite`, for
instance. Then `<package_manager> install`.

## `.storybook/main.<ts|js>`

- `framework` — the resolved `storybook_addon`
- `stories: ['../src/**/*.stories.*']`
- `addons: ['<storybook_addon>', '@storybook/addon-essentials']`
- viewport presets built from the breakpoints in `07_screens/shell.md`

## `.storybook/theme.<ts|js>`

A Storybook theme object built entirely from tokens and the brief:

| Theme key | Source |
|---|---|
| `base` | `tokens.mode` (`light` or `dark`) |
| `appBg` | `tokens.colors.background` |
| `fontBase` | `tokens.fonts.body` |
| `fontCode` | `tokens.fonts.mono` |
| `brandTitle` | the app name from `brief.md` |

## `.storybook/preview.<ts|js>`

Imports `../src/styles/brand.css`, applies the token custom properties as a global decorator,
and declares the same viewport presets as `main`.

## `src/styles/brand.css`

`:root` carrying the Google Fonts import for the heading and body faces, then one custom
property per token:

```
--color-primary --color-secondary --color-accent --color-background --color-surface
--color-foreground --color-muted --color-border --color-destructive --color-success
--color-warning --radius --spacing-base
--font-heading --font-body --font-mono
--shadow-sm --shadow-md --shadow-lg
```

`tokens.mode: "both"` adds a `.dark { … }` block overriding the colour set. A single-mode
brand gets no `.dark` block at all — an unused one drifts silently, because nothing renders
it.

## `src/@types/`

Create the directory with a `README.md` saying that types are built incrementally by each
layer and cover only the properties a component renders. Steps 3 and 4 add the interfaces;
nothing generates them here. When the project later has a real data model, those minimal
interfaces are what a codegen pass replaces.
