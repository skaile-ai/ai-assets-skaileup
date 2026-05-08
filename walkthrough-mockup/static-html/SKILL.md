---
name: walkthrough-mockup-static-html
description: "Use when stakeholders need a clickable static HTML walkthrough of the application — zero build, no JS framework, openable directly in a browser. Generates one HTML file per screen and per journey, plus a manifest.json that the mockup-feedback cluster reads to resolve clicks back to source artefacts. Best for simple-app tier."
metadata:
  version: "0.1.0"
  tags:
    - walkthrough
    - mockup
    - static-html
    - zero-build
    - simple-app
    - frontend
    - prototype
    - data-spec
  stage: alpha
  prerequisites:
    files:
      - path: "experience/screens"
        gate: hard
        description: "Screen specs are the primary input — one file rendered per screen"
        min_entries: 1
      - path: "experience/journeys/stories.json"
        gate: hard
        description: "Journey definitions drive the journey/<id>.html sequencing"
      - path: "design/tokens.json"
        gate: hard
        description: "Brand tokens injected as CSS variables in the rendered shell"
      - path: "product-spec/features"
        gate: soft
        description: "Feature files are linked from manifest.json for traceability; absence is recorded as a warning, not a failure"
        min_entries: 1
    reads:
      - path: "experience/screens/00_layout/shell.md"
        description: "Optional shared layout reference; if present, used as the wrapping shell for every screen"
    produces:
      - path: "_concept/walkthrough-mockup/static-html"
        description: "Generated static site: index.html, screen/<group>/<name>.html, journey/<id>.html, manifest.json"
---

# Walkthrough Mockup — Static HTML

## Overview

## Renderer Contract

## Inputs

## Outputs

## ROLE / READS / WRITES / REFERENCES

## STEP 1: Read inputs

## STEP 2: Render screens

## STEP 3: Render journeys

## STEP 4: Emit index.html and manifest.json

## STEP 5: Validate

## MUST / NEVER

## CHECKLIST
