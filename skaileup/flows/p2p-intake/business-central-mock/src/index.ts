#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createServer } from "./server.js";

/**
 * Standalone/dev entry for the mock Business Central MCP server. Speaks MCP over
 * stdio. stdout is the protocol channel — all logs go to stderr.
 */
async function main(): Promise<void> {
  const server = createServer();
  await server.connect(new StdioServerTransport());
  process.stderr.write("business-central-mock: MCP server ready on stdio\n");
}

main().catch((err) => {
  console.error("business-central-mock failed to start:", err);
  process.exit(1);
});
