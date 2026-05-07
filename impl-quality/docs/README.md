# quality

This domain contains quality assurance skills: static audit, end-to-end testing, readiness gates, and test generation.

## Skills

| Skill                           | Path                                  | Sources   | Purpose                                                          |
| ------------------------------- | ------------------------------------- | --------- | ---------------------------------------------------------------- |
| **impl-quality-audit**              | `skills/impl-quality-audit/`              | CF + Saxe | Static code analysis + concept structure audit                   |
| **impl-quality-test-e2e**                | `skills/impl-quality-test-e2e/`                | CF + Saxe | End-to-end browser tests                                         |
| **impl-quality-ready**              | `skills/impl-quality-ready/`              | CF + Saxe | Pre-flight readiness gate before next pipeline step              |
| **ops-sync**               | `skills/ops-sync/`               | CF only   | Cross-reference repair (features ↔ screens, model → features)    |
| **impl-quality-test-unit**          | `skills/impl-quality-test-unit/`          | CF only   | Unit test generation                                             |
| **impl-quality-test-integration**   | `skills/impl-quality-test-integration/`   | CF only   | Integration test generation                                      |
| **impl-quality-test-plan**          | `skills/impl-quality-test-plan/`          | CF only   | Test plan document → `08_testing/test_plan.md`                   |
| **lab-compile-validators** | `skills/lab-compile-validators/` | Saxe only | Compile all `validator.py` files into a unified validation suite |

## Notable Patterns

- **Saxe audit**: Uses 3 parallel sub-agents (structure + code + dependency analysis simultaneously)
- **Saxe e2e**: Adds screenshot diffing and database state validation
- **compile-validators**: A compelling Saxe pattern — gather all skill validators and run them as a suite. Candidate for adoption across all skills.

## CF vs Saxe Variants

`audit/`, `e2e/`, `ready/` each have `cf/` and `saxe/` subdirectories.
