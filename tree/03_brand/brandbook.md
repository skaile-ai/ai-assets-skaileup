---
path: _concept/03_brand/brandbook.html
summary: self-contained visual reference for the brand
writers: [design-brand]
---

# _concept/03_brand/brandbook.html

The brand shown rather than described, for the user and stakeholders to judge by eye before anything is rendered. Nothing machine-reads it; it is the page the user approves the look from.

## Format

One HTML file that stands alone: inline CSS, Google Fonts `<link>`s as the only external reference, under 50 KB. It demonstrates the brand rather than listing it: swatches, type in use, spacing, elevation, and live button, card, input and nav previews, all drawn with the brand's own tokens from `tree/03_brand/tokens.md`.

## Writing it

Write it last, from the finished `tokens.json`, in `tree/03_brand/README.md § Writing it` step 5.

## Checks

The file opens offline apart from the fonts, is under 50 KB, and shows every colour in `tokens.json`.
