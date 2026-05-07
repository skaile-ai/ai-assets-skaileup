# impl-build-implementation

This domain covers the full implementation lifecycle: project scaffolding, feature-by-feature development (TDD), and verification. Skills read from `_concept/` and write production code.

## Skill Groups

| Group                              | Path                                     | Purpose                                            |
| ---------------------------------- | ---------------------------------------- | -------------------------------------------------- |
| **impl-build-implement**             | `skills/impl-build-implement/`             | Implementation pipeline controller                 |
| **setup**                          | `skills/setup/`                          | Project scaffold, foundation setup, infrastructure |
| **impl-slice-implement**     | `skills/impl-slice-implement/`     | Per-feature implementation (TDD-first)             |
| **impl-build-docs** | `skills/impl-build-docs/` | Starlight documentation updates                    |
| **utilities**                      | `skills/utilities/`                      | Migration, seed data, code generation              |

## CF vs Saxe Variants

- `cf/` variants are stack-agnostic
- `saxe/` variants are PostXL/NestJS-specific

## Key Patterns

- **Journey-first** (Saxe): Implement features in user journey order, not technical order
- **TDD Guard** (Saxe): Write tests before implementation, enforce before proceeding
- **Brand token application** (Saxe): Foundation step applies `04_brand/tokens.json` to theme config
- **Parallel sub-agents** (Saxe audit): Audit uses 3 simultaneous sub-agents for speed

## Output

Skills write to the project codebase. The implementation structure (from Saxe) is:

```
_implementation/
├── decisions/     → ADRs and tech decisions
├── progress/      → feature completion tracking
└── issues/        → blocked items
```
