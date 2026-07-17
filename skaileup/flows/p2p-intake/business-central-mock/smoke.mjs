import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({ command: "bun", args: ["run", "src/index.ts"] });
const client = new Client({ name: "smoke", version: "0.0.0" });
await client.connect(transport);

const tools = (await client.listTools()).tools.map((t) => t.name).sort();
console.log("tools:", tools.join(", "));

const sup = await client.callTool({ name: "get_supplier", arguments: { name: "nordwind" } });
console.log("get_supplier:", sup.content[0].text);

const draft = await client.callTool({
  name: "create_po_draft",
  arguments: { supplier_id: "BC-SUP-1001", cost_center: "CC-42", lines: [{ description: "Smart meters", qty: 10, unit_price: 45.5 }] },
});
const po = JSON.parse(draft.content[0].text).draft.po_number;
console.log("create_po_draft:", draft.content[0].text);

const posted = await client.callTool({ name: "post_po", arguments: { po_number: po } });
console.log("post_po:", posted.content[0].text);

await client.close();
console.log("SMOKE OK");
