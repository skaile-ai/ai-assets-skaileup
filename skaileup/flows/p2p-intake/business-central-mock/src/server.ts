import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { BusinessCentralStore } from "./store.js";

function ok(data: unknown): CallToolResult {
  return { content: [{ type: "text", text: JSON.stringify(data) }] };
}

function fail(message: string): CallToolResult {
  return { content: [{ type: "text", text: message }], isError: true };
}

function guard(fn: () => CallToolResult): CallToolResult {
  try {
    return fn();
  } catch (err) {
    return fail(err instanceof Error ? err.message : String(err));
  }
}

/**
 * Build the mock Business Central MCP server. DEMO-GRADE — backs the Getec
 * p2p-intake flow with three tools over an in-memory store:
 * `get_supplier`, `create_po_draft`, `post_po`. In production, Getec's SAP BTP
 * MCP layer exposes the same surface over the real Business Central.
 */
export function createServer(store: BusinessCentralStore = new BusinessCentralStore()): McpServer {
  const server = new McpServer({ name: "business-central-mock", version: "0.1.0" });

  server.registerTool(
    "get_supplier",
    {
      description:
        "Resolve a supplier from Business Central master data by BC id, exact legal name, " +
        "or a known alias (case-insensitive). Returns the supplier record or a not-found result.",
      inputSchema: { name: z.string().min(1) },
    },
    ({ name }) =>
      guard(() => {
        const supplier = store.getSupplier(name);
        if (!supplier) return ok({ match_status: "unresolved", query: name });
        return ok({ match_status: "resolved", supplier });
      }),
  );

  server.registerTool(
    "create_po_draft",
    {
      description:
        "Create a purchase-order draft in Business Central. Fails for an unknown or blocked " +
        "supplier or an empty line list. Returns the draft with a generated po_number and " +
        "status 'pending_approval' (never posted here).",
      inputSchema: {
        supplier_id: z.string().min(1),
        currency: z.string().optional(),
        cost_center: z.string().nullable().optional(),
        lines: z
          .array(
            z.object({
              description: z.string().min(1),
              qty: z.number().positive(),
              unit_price: z.number().nonnegative(),
            }),
          )
          .min(1),
      },
    },
    ({ supplier_id, currency, cost_center, lines }) =>
      guard(() => ok({ draft: store.createPoDraft({ supplier_id, currency, cost_center, lines }) })),
  );

  server.registerTool(
    "post_po",
    {
      description:
        "Post an approved PO draft to Business Central by po_number. Fails for an unknown or " +
        "already-posted PO. Returns the posted PO with status 'posted' and a posted_at timestamp.",
      inputSchema: { po_number: z.string().min(1) },
    },
    ({ po_number }) => guard(() => ok({ posted: store.postPo(po_number) })),
  );

  return server;
}
