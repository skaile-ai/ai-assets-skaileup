# Pattern -> mock-cell registry

> Low-fidelity by design. This skill is the **early-design quick reference**;
> if you need pixel parity with the real component library, use
> `component-mockup-storybook` instead.

Each entry maps a value of the source `pattern:` frontmatter key to a small
HTML snippet that gets injected inside `<div class="cell">`. Snippets MUST:

1. Use only inline `style="..."` attributes that reference `var(--token-*)`
   variables defined in the inlined `:root` block — never hardcode colors.
2. Use only `<div>`, `<span>`, `<p>`, `<pre>`, `<table>` and similar zero-JS
   elements. No `<script>`, no event handlers, no external assets.
3. Honor the cell's `data-variant` and `data-state` for traceability — those
   attributes are set on the parent `<div class="cell">` by the renderer.

## Built-in patterns

| `pattern:` value   | Mock                                                                         |
| ------------------ | ---------------------------------------------------------------------------- |
| `data_table`       | 3-row x 2-col mock table with header row                                     |
| `status_badge`     | inline pill with token-driven background and foreground                      |
| `card`             | bordered box with title + body lines                                         |
| `form`             | label + input rectangle + submit pill                                        |
| `empty_state`      | centered icon-placeholder + caption                                          |
| `confirm_dialog`   | bordered box with title + two action pills                                   |
| `generic`          | small swatch + variant/state caption (default fallback)                      |

Unknown patterns fall back to `generic`.

## Variant / state styling hooks

The renderer applies cosmetic hints based on common variant/state names so
the grid visually communicates the differences without consuming the
component library:

- variant lowercase contains `compact` -> tighter padding
- variant lowercase contains `outlined` / `secondary` -> background becomes
  surface, border emphasized
- state lowercase contains `loading` -> opacity + skeleton stripe
- state lowercase contains `empty` -> dashed border, italic caption
- state lowercase contains `error` -> error token used for border/text
- state lowercase contains `disabled` -> opacity 0.5, cursor not-allowed
  (visual only)

These are best-effort low-fi hints. Add new patterns by extending
`scripts/render_component_html.PATTERN_MOCKS` and documenting them here.
