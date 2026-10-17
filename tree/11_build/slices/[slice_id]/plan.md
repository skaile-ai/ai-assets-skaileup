---
path: _concept/11_build/slices/<slice_id>/plan.md
summary: one slice's scope, rows, criteria by id, tests and carry-overs
writers: [build-plan]
---

# _concept/11_build/slices/<slice_id>/plan.md

What one vertical slice builds and how it is proved. `build-implement` reads nothing else
about the work: its rows are the build order, its tests are the gate, and its criteria ids
are what the ledger is flipped against. A test decided after the slice is a seam nobody
agreed.

## Format

Frontmatter: `feature` (the feature file, `_concept/05_features/<featureset>/<feature_slug>.md`), `blocked_by` (list of `slice_id`s, empty when the slice can start immediately), `last_updated`.

Body, in this order:

1. **Scope**: one line.
2. **Rows**: the UI / logic / data rows the slice crosses, each citing the screen file (when the feature has screens), the symbol and the entity by name. Where the project grows no screens the UI row names the endpoint, command or public function.
3. **Criteria**: the acceptance criteria this slice satisfies, by id only (`AC-<story-id>-<nn>`, per `tree/04_journeys/stories.md`). The text lives in the spec and `stories.yaml`; a second copy goes stale.
4. **Checks**: the manual checks (questions for the user) and the automated tests that prove the slice, each test tagged `[unit]`, `[integration]` or `[e2e]` by the smallest reliable seam.
5. **Carry-overs**: what the slice deliberately leaves open.

```markdown
---
feature: _concept/05_features/billing/checkout.md
blocked_by: [cart-persistence]
last_updated: 2026-10-16
---

# Pay for the cart

Scope: a signed-in user pays for their cart and sees the order confirmed.

## Rows
- UI: `07_screens/checkout/payment.md` renders the cart total; submit calls `placeOrder`
- Logic: `placeOrder()` in `src/orders/place.ts`
- Data: writes `order`, `order_item`

## Criteria
- AC-checkout_flow-02
- AC-checkout_flow-03

## Checks
- Manual: pay with the seed `single_user` card and confirm the order page shows the total
- `[unit]` total rounds per line item
- `[integration]` `placeOrder` persists `order` and `order_item`

## Carry-overs
- refunds
```

## Writing it

Written by `build-plan` after the user approved the breakdown (`tree/11_build/slices/README.md § Writing it`). The slug is the slice's `slice_id`; the file lands in `_concept/11_build/slices/<slice_id>/`.

## Checks

- Every criterion id appears by id and not by text.
- Every row names its symbol and entity.
- Every test carries a level tag.
