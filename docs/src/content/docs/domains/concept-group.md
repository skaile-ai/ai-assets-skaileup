---
title: "Concept group"
description: "The domains that figure out what to build — brief, design, spec, experience, and the mockup clusters."
sidebar:
  label: "Overview"
  order: 0
---

The **Concept group** is the half of the collection that figures out *what* to
build. For `mvp` and `simple-app` it runs linearly; for `standard-app` and
`complex-app` it runs a high-level pass followed by a per-feature
[`concept-slice`](../../flows/concept-slice/) loop.

## Domains

- [**concept**](./concept/) — brief · goals · comparable
- [**design**](./design/) — brand identity · tokens · voice · inspiration
- [**product-spec**](./product-spec/) — features · acceptance criteria
- [**experience**](./experience/) — journeys · behaviors · screens · components
- [**concept-slice**](./concept-slice/) — the per-feature concept loop (big apps)
- [**mockup-component**](./mockup-component/) — components in isolation (Storybook · isolated-html)
- [**mockup-walkthrough**](./mockup-walkthrough/) — clickable app (text · static-html · astro · lit · framework)
- [**mockup-feedback**](./mockup-feedback/) — annotation → patch loop

## See also

- [Mental Model](../../intro/mental-model/) — why concept and implementation share a shape
- [Implementation group](./impl-group/) — the building half
- [Flows](../../flows/) — how these domains compose per tier
