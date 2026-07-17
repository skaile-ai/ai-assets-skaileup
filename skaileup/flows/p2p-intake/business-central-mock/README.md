# business-central-mock (MCP server)

**DEMO-GRADE.** A minimal Model Context Protocol server that mocks the slice of
Microsoft Dynamics 365 Business Central the Getec **p2p-intake** demo flow needs.
In production, Getec's **SAP BTP MCP layer** exposes the same three-tool surface
over the real Business Central; this mock lets the demo run standalone at the
August workshop.

Colocated with the flow it serves: `skaileup/flows/p2p-intake/`.

## Tool surface

| Tool | Input | Returns |
|---|---|---|
| `get_supplier` | `{ name }` | `{ match_status, supplier? }` — resolves by BC id, legal name, or alias |
| `create_po_draft` | `{ supplier_id, currency?, cost_center?, lines[] }` | `{ draft }` — status `pending_approval`, generated `po_number` |
| `post_po` | `{ po_number }` | `{ posted }` — status `posted` + `posted_at` |

State is an in-memory store (`src/store.ts`) seeded with three suppliers
(one blocked, to exercise the failure path). No persistence — state lives for the
process lifetime. `stdout` is the MCP stdio channel; all logs go to `stderr`.

## Run

```bash
bun install
bun run dev          # stdio MCP server (business-central-mock)
bun test             # store smoke tests
bun run build        # emit dist/ for `business-central-mock-mcp` bin
```

Wire it to an MCP client (e.g. the workspace runner or Claude Code) as an stdio
server pointing at `dist/index.js` (after build) or `bun run src/index.ts` (dev).

## How the flow uses it

`p2p-intake` skills call the tools in order: `enrich` -> `get_supplier`,
`po-draft` -> `create_po_draft` (draft stays `pending_approval`), then the flow's
**approval gate** pauses for a human; on approval, `post` -> `post_po`.
