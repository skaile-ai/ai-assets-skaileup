---
title: "lab-validate"
description: "Execute test cases from a skill's test manifest in Docker containers and produce a validation report"
sidebar:
  label: "lab-validate"
---

:::note[Skill manifest]
**Name:** `lab-validate`
**Stage:** — · **Version:** —
**Tags:** —
**Source:** [`ai-assets/lab/validate/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/ai-assets/lab/validate/SKILL.md)
:::


# Lab Validate

You are validating a skill's test cases. Follow this process exactly:

1. **Load the test manifest** from the skill's `test-manifest.yaml`
2. **For each test case:**
   a. Resolve the Docker Compose stack (check `stack_override`, fall back to `defaults.stack`)
   b. Start the container (`docker compose -p lab-<skill>-<case-id> up`)
   c. Copy scaffold to workspace
   d. If the case has a `recipe`, load it and use it as the implementation prompt
   e. If the case has a `prompt`, use that directly
   f. Execute the skill in the container (via DockerProxyDriver)
   g. Run all metrics specified (defaults + case overrides)
   h. Short-circuit on gate failure
   i. Teardown the container
3. **Aggregate results** into a ValidationReport
4. **Flag regressions** by comparing against previous results
5. **Output the report** as structured YAML

Cases sharing the same stack can run in parallel. Cases needing different stacks run sequentially.

Always use the tiered metric system: gates first (must pass), then quality metrics (scored 0-100).

