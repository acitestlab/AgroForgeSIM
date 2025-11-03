// src/panels/HarvestPlan.tsx
import React, { useMemo } from "react";
import { useStore, type Task } from "../store"; // Task is exported in the merged store

/* ------------------------ Local helpers (safe stubs) ------------------------ */
/* If you already have real implementations, replace these with imports:
   import { allocateIrrigationFromTopology } from "@/lib/irrigation";
   import { computeStorageAndMarket } from "@/lib/econ";
*/

type IrrigationPlan = { events: { day: number; mm: number; note?: string }[]; water_mm: number };
function allocateIrrigationFromTopology(_topology: unknown, params: { mmPerEvent?: number; count?: number } = {}): IrrigationPlan {
  const mm = params.mmPerEvent ?? 20;
  const count = params.count ?? 2;
  return {
    events: Array.from({ length: count }, (_, i) => ({ day: 30 + i * 30, mm, note: "Irrigation (stub)" })),
    water_mm: mm * count,
  };
}

type EconOut = { kept_t: number; loss_t: number; revenue: number };
function computeStorageAndMarket(yield_t: number, opts: { price_per_t?: number; loss_rate?: number } = {}): EconOut {
  const price = opts.price_per_t ?? 120_000; // NGN per tonne (example)
  const loss = Math.max(0, Math.min(1, opts.loss_rate ?? 0.05));
  const loss_t = +(yield_t * loss).toFixed(2);
  const kept_t = +(yield_t - loss_t).toFixed(2);
  const revenue = +(kept_t * price).toFixed(2);
  return { kept_t, loss_t, revenue };
}

/* -------------------------------- Component -------------------------------- */

export default function HarvestPlan() {
  // Pull what we need from the store – with SAFE defaults
  const sim = useStore((s) => s.result);                    // was simResult
  const simLoading = useStore((s) => !!s.loading?.sim);     // was loading.simulate
  const selectedId = useStore((s) => s.selectedId ?? null); // was selected
  const nodes = useStore((s) => s.nodes ?? []);
  const fields = useStore((s) => s.fields ?? []);

  // Selected name (for the sidebar header)
  const selectedName = useMemo(() => {
    const n = (selectedId && nodes.find((x) => x.id === selectedId)) || nodes[0];
    const f = (selectedId && fields.find((x) => x.id === selectedId)) || fields[0];
    return n?.name || f?.name || "Selected Plot";
  }, [selectedId, nodes, fields]);

  // Simulation plan & yield – keep types tight to avoid "unknown" warnings
  const plan: Task[] = useMemo(() => (Array.isArray(sim?.plan) ? (sim!.plan as Task[]) : []), [sim]);
  const yield_t = typeof sim?.yield_t === "number" ? sim!.yield_t : undefined;

  // Example derived bits (optional)
  const irrigation = useMemo(() => allocateIrrigationFromTopology(null, { mmPerEvent: 20, count: 2 }), []);
  const econ = useMemo(() => (typeof yield_t === "number" ? computeStorageAndMarket(yield_t) : null), [yield_t]);

  /* --------------------------------- Render -------------------------------- */
  return (
    <div className="panel" style={{ minHeight: 280 }}>
      <h3 style={{ marginTop: 0 }}>Yield &amp; Harvest Plan</h3>

      {simLoading && <p>Running simulation…</p>}

      {!simLoading && !yield_t && (
        <>
          <p>Run a simulation to view harvest plan and yield.</p>
          <div style={{ display: "flex", gap: 8 }}>
            <ExportPlanCSVButton plan={plan} />
            <ExportResultJSONButton result={sim} />
          </div>
        </>
      )}

      {!simLoading && typeof yield_t === "number" && (
        <>
          <div style={{ margin: "8px 0 12px" }}>
            <strong>Field:</strong> {selectedName}
            <br />
            <strong>Projected yield:</strong> {yield_t.toFixed(2)} t
            {econ && (
              <>
                <br />
                <strong>Post-harvest kept:</strong> {econ.kept_t.toFixed(2)} t &nbsp;·&nbsp;
                <strong>Loss:</strong> {econ.loss_t.toFixed(2)} t &nbsp;·&nbsp;
                <strong>Revenue (est):</strong> ₦{econ.revenue.toLocaleString()}
              </>
            )}
          </div>

          {plan.length > 0 ? (
            <div style={{ maxHeight: 280, overflow: "auto", border: "1px solid rgba(0,0,0,0.08)", borderRadius: 8 }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
                <thead>
                  <tr style={{ background: "#f1f5f9" }}>
                    <th style={{ textAlign: "left", padding: "8px 10px" }}>Date</th>
                    <th style={{ textAlign: "left", padding: "8px 10px" }}>Operation</th>
                    <th style={{ textAlign: "left", padding: "8px 10px" }}>Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {plan.map((t, i) => (
                    <tr key={i} style={{ borderTop: "1px solid rgba(0,0,0,0.06)" }}>
                      <td style={{ padding: "8px 10px" }}>{t.date}</td>
                      <td style={{ padding: "8px 10px" }}>{t.op}</td>
                      <td style={{ padding: "8px 10px" }}>{t.notes || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No operations in the current plan.</p>
          )}

          <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
            <ExportPlanCSVButton plan={plan} />
            <ExportResultJSONButton result={sim} />
          </div>

          {/* Small irrigation hint so the panel doesn't crash if some code expects it */}
          <div style={{ marginTop: 8, color: "#475569", fontSize: 12 }}>
            Irrigation (stub): {irrigation.events.length} events · total {irrigation.water_mm} mm
          </div>
        </>
      )}
    </div>
  );
}

/* ------------------------------ Export buttons ----------------------------- */

function ExportPlanCSVButton({ plan }: { plan: Task[] }) {
  const csv = useMemo(() => {
    const header = "date,operation,notes";
    const rows = plan.map((t) =>
      [t.date, t.op, (t.notes || "").replace(/(\r\n|\n|\r|,)/g, " ")].map(escapeCsv).join(",")
    );
    return [header, ...rows].join("\n");
  }, [plan]);

  const onClick = () => {
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "harvest_plan.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <button className="btn secondary" onClick={onClick} disabled={plan.length === 0}>
      Export Plan (CSV)
    </button>
  );
}

function ExportResultJSONButton({ result }: { result: unknown }) {
  const onClick = () => {
    const blob = new Blob([JSON.stringify(result ?? {}, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "simulation_result.json";
    a.click();
    URL.revokeObjectURL(url);
  };
  return (
    <button className="btn secondary" onClick={onClick} disabled={!result}>
      Export Result (JSON)
    </button>
  );
}

/* --------------------------------- utils ---------------------------------- */

function escapeCsv(s: string) {
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}
