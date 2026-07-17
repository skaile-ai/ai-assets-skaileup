/**
 * In-memory store for the mock Business Central MCP server.
 *
 * DEMO-GRADE. Backs the Getec p2p-intake demo flow with just enough state to
 * resolve suppliers, hold PO drafts, and post them. No persistence: state lives
 * for the lifetime of the process. In production, Getec's SAP BTP MCP layer
 * exposes the same three-tool surface over the real Business Central.
 */

export interface Supplier {
  id: string;
  legal_name: string;
  tax_id: string;
  payment_terms: string;
  currency: string;
  blocked: boolean;
  /** lower-cased aliases used for fuzzy name resolution */
  aliases: string[];
}

export interface PoLine {
  description: string;
  qty: number;
  unit_price: number;
}

export interface PoDraft {
  po_number: string;
  supplier_id: string;
  currency: string;
  cost_center: string | null;
  lines: PoLine[];
  total: number;
  status: "pending_approval" | "posted";
  created_at: string;
  posted_at: string | null;
}

const SEED_SUPPLIERS: Supplier[] = [
  {
    id: "BC-SUP-1001",
    legal_name: "Nordwind Energie GmbH",
    tax_id: "DE811234567",
    payment_terms: "NET30",
    currency: "EUR",
    blocked: false,
    aliases: ["nordwind", "nordwind energie", "nordwind energie gmbh"],
  },
  {
    id: "BC-SUP-1002",
    legal_name: "Rheinmetall Buero & IT AG",
    tax_id: "DE811987654",
    payment_terms: "NET14",
    currency: "EUR",
    blocked: false,
    aliases: ["rheinmetall buero", "rheinmetall", "rheinmetall buero & it"],
  },
  {
    id: "BC-SUP-1003",
    legal_name: "Sued Facility Services GmbH",
    tax_id: "DE811222333",
    payment_terms: "NET30",
    currency: "EUR",
    blocked: true,
    aliases: ["sued facility", "sued facility services", "facility services"],
  },
];

export class BusinessCentralStore {
  private suppliers = new Map<string, Supplier>();
  private drafts = new Map<string, PoDraft>();
  private seq = 0;

  constructor() {
    for (const s of SEED_SUPPLIERS) this.suppliers.set(s.id, s);
  }

  /** Resolve a supplier by BC id, exact legal name, or a known alias (case-insensitive). */
  getSupplier(query: string): Supplier | null {
    const q = query.trim().toLowerCase();
    for (const s of this.suppliers.values()) {
      if (s.id.toLowerCase() === q) return s;
      if (s.legal_name.toLowerCase() === q) return s;
      if (s.aliases.some((a) => a === q || q.includes(a) || a.includes(q))) return s;
    }
    return null;
  }

  createPoDraft(input: {
    supplier_id: string;
    currency?: string;
    cost_center?: string | null;
    lines: PoLine[];
  }): PoDraft {
    const supplier = this.suppliers.get(input.supplier_id);
    if (!supplier) throw new Error(`unknown-supplier: ${input.supplier_id}`);
    if (supplier.blocked) throw new Error(`supplier-blocked: ${input.supplier_id}`);
    if (!input.lines || input.lines.length === 0) throw new Error("empty-po: at least one line required");

    this.seq += 1;
    const po_number = `PO-${String(this.seq).padStart(5, "0")}`;
    const total = input.lines.reduce((sum, l) => sum + l.qty * l.unit_price, 0);
    const draft: PoDraft = {
      po_number,
      supplier_id: input.supplier_id,
      currency: input.currency ?? supplier.currency,
      cost_center: input.cost_center ?? null,
      lines: input.lines,
      total: Math.round(total * 100) / 100,
      status: "pending_approval",
      created_at: new Date().toISOString(),
      posted_at: null,
    };
    this.drafts.set(po_number, draft);
    return draft;
  }

  postPo(po_number: string): PoDraft {
    const draft = this.drafts.get(po_number);
    if (!draft) throw new Error(`unknown-po: ${po_number}`);
    if (draft.status === "posted") throw new Error(`already-posted: ${po_number}`);
    draft.status = "posted";
    draft.posted_at = new Date().toISOString();
    return draft;
  }
}
