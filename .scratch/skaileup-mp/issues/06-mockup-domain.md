# 06: Mockup domain — 17 skills to ~6

**Type:** grilling
**Blocked by:** 04 (resolved)
**Status:** ready

## Question

The three mockup domains are 17 skills and 6,597 lines — 26% of all prose in the collection —
and they are the part explicitly worth keeping, since Storybook is how the app gets built
incrementally. Settled in principle: one `mockup` domain of ~6 skills, with the renderer
choice becoming a **parameter** rather than five sibling skills. Work out the detail.

Today:

- `05_mockup-walkthrough/`: `00_migrate-elements` + renderers `text` · `static-html` · `astro`
  · `lit` · `framework` (the last three are 1,133 / 1,248 / 973 lines).
- `06_mockup-component/`: `isolated-html` + Storybook `setup` · `components` · `pages` ·
  `journeys` · `types` · `orchestrator`.
- `07_mockup-feedback/`: `annotate` → `triage` → `patch` → `apply`.

**What ticket 03's astro port showed, before you re-litigate the 17 → 6 count.** The
1,133-line skill ports to **110 lines** — under mp's 140 ceiling — with `references/scaffold/`
(the 7 file bodies as real files it copies) and `references/specs-json.md` beside it. So
length alone does not force the collapse; **duplication** does. Two specifics:

- ~200 lines of the astro skill's STEP 2 were restating `contracts/walkthrough_renderer.md`
  § Target resolution, § Auto-slug fallback and § Spec reference panel almost verbatim. Five
  renderers × that duplication is most of the 4,540 lines, and it is why they drift.
- The **`items[]` id-derivation rule belongs in the shared contract, not in each renderer.**
  The astro skill spends ~30 lines deriving it and says outright that it "follows directly
  from" the contract's `data-spec-*` table. Every renderer needs it and every renderer must
  agree on it. Move it into `walkthrough_renderer.md` and it stops being written five times.

This sharpens the renderer-parameter question rather than answering it: if what differs
between renderers is only the scaffold and a handful of resolution rules, the difference may
be a `references/<renderer>/` directory rather than a parameter or a skill.

Decide:

- The ~6 surviving skills and their names (proposed: `setup` · `components` · `pages` ·
  `journeys` · `walkthrough` · `feedback`).
- How the renderer parameter works: which renderers survive at all, whether the differences
  are genuinely parametric or whether one is a `references/` file per renderer.
- Whether the 4-step feedback chain (annotate → triage → patch → apply) collapses. `triage`
  is deterministic and non-LLM; `apply` writes commits — do those want to stay separate?
- What `00_migrate-elements` and the `elements:` block contract become.
- Where Storybook sits relative to `impl-build` — it is both a mockup surface and a real
  build artifact, and today that's split across two domains.

## Answer

_(pending)_
