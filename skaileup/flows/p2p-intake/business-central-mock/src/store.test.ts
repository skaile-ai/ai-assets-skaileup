import { describe, expect, test } from "bun:test";
import { BusinessCentralStore } from "./store.js";

describe("BusinessCentralStore", () => {
  test("resolves a seeded supplier by alias", () => {
    const store = new BusinessCentralStore();
    const s = store.getSupplier("nordwind");
    expect(s?.id).toBe("BC-SUP-1001");
    expect(s?.currency).toBe("EUR");
  });

  test("returns null for an unknown supplier", () => {
    const store = new BusinessCentralStore();
    expect(store.getSupplier("does-not-exist")).toBeNull();
  });

  test("create_po_draft -> post_po happy path", () => {
    const store = new BusinessCentralStore();
    const draft = store.createPoDraft({
      supplier_id: "BC-SUP-1001",
      cost_center: "CC-42",
      lines: [{ description: "Smart meters", qty: 10, unit_price: 45.5 }],
    });
    expect(draft.status).toBe("pending_approval");
    expect(draft.total).toBe(455);
    expect(draft.po_number).toMatch(/^PO-\d{5}$/);

    const posted = store.postPo(draft.po_number);
    expect(posted.status).toBe("posted");
    expect(posted.posted_at).not.toBeNull();
  });

  test("rejects a blocked supplier", () => {
    const store = new BusinessCentralStore();
    expect(() =>
      store.createPoDraft({
        supplier_id: "BC-SUP-1003",
        lines: [{ description: "x", qty: 1, unit_price: 1 }],
      }),
    ).toThrow(/supplier-blocked/);
  });

  test("rejects double-posting", () => {
    const store = new BusinessCentralStore();
    const draft = store.createPoDraft({
      supplier_id: "BC-SUP-1002",
      lines: [{ description: "Laptops", qty: 2, unit_price: 1200 }],
    });
    store.postPo(draft.po_number);
    expect(() => store.postPo(draft.po_number)).toThrow(/already-posted/);
  });
});
