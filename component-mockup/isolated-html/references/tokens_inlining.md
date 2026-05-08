# Tokens-inlining strategy

> **Source of truth:** `design/brand-visual/references/tokens_schema.md`. The
> rules below pin **how** this skill flattens that JSON shape into CSS custom
> properties inside an inline `:root { ... }` block in each generated HTML.

## Token shape (pinned)

```json
{
  "colors": {
    "primary": "#6366f1",
    "secondary": "#0ea5e9",
    "accent": "#f59e0b",
    "background": "#0f172a",
    "surface": "#1e293b",
    "text": "#f8fafc",
    "text_muted": "#94a3b8",
    "border": "#334155",
    "error": "#ef4444",
    "success": "#22c55e",
    "warning": "#f59e0b"
  },
  "fonts": { "heading": "...", "body": "...", "mono": "..." },
  "radius": "8px",
  "mode": "dark",
  "spacing_base": "8px",
  "shadows": { "sm": "...", "md": "...", "lg": "..." },
  "atmosphere": { "type": "...", "description": "..." },
  "tailwind": { "--color-primary": "#...", "--radius": "0.5rem" }
}
```

## Flattening rule

Dotted JSON path becomes `--token-<segments-joined-by-hyphen>`:

| JSON path                  | CSS variable                        |
| -------------------------- | ----------------------------------- |
| `colors.primary`           | `--token-colors-primary`            |
| `colors.text_muted`        | `--token-colors-text-muted`         |
| `fonts.heading`            | `--token-fonts-heading`             |
| `radius`                   | `--token-radius`                    |
| `spacing_base`             | `--token-spacing-base`              |
| `shadows.sm`               | `--token-shadows-sm`                |
| `atmosphere.type`          | `--token-atmosphere-type`           |
| `tailwind.--color-primary` | **passthrough**: `--color-primary`  |

## Naming convention rules (MUST be preserved)

1. Prefix is always `--token-` for nested-path variables (so they don't
   collide with the `tailwind:` block's variables, which are passed through
   as-is).
2. Path segments are joined with single hyphens.
3. Underscores within a path segment become single hyphens
   (`text_muted` → `text-muted`).
4. Camel-case segments become kebab-case via lowercase + hyphen-before-capital
   (no instances expected per the schema; defensive only).
5. Object values that aren't strings are flattened recursively. If a leaf
   value is non-string, it is **skipped with a warning** to keep CSS valid.
6. The `tailwind:` block is emitted **after** the flattened tree so any
   same-named override wins (Tailwind block authoritative for
   production-aligned values).

## Embedding placement

All variables are emitted inside a single `<style>...</style>` block in the
document `<head>`, scoped to `:root { ... }`. No external
`<link rel="stylesheet">` is permitted in produced HTML.
