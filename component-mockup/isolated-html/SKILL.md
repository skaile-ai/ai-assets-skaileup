---
name: component-mockup-isolated-html
description: "Use when components are specced and an mvp/simple-app team needs a quick visual reference without a Storybook build. Renders one standalone HTML file per component showing all variants × states in a token-driven grid; no JS, no framework, openable via file://."
metadata:
  version: '1.0.0'
  tags:
    - 'components'
    - 'mockup'
    - 'isolated'
    - 'static-html'
    - 'tokens'
    - 'no-build'
    - 'low-fidelity'
    - 'simple-app'
  stage: alpha
  source: NEW
  parameters:
    depth:
      type: enum
      values: [none, light, medium, max]
      default: medium
  prerequisites:
    files:
      - path: '_concept/experience/screens/components'
        gate: hard
        description: 'Component specs required — one HTML output per component spec.'
        min_entries: 1
      - path: '_concept/discovery/brand/tokens.json'
        gate: hard
        description: 'Design tokens required to embed CSS variables inline.'
    produces:
      - path: '_concept/component-mockup/isolated-html'
        description: 'One standalone HTML file per component, openable via file://.'
---
