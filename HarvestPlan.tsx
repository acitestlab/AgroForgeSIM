import React, { useState, useMemo } from "react";
import { motion } from "framer-motion";

/* ============================================================
   🌾 TYPES
============================================================ */
interface HarvestRow {
  field_id: string;
  crop: string;
  planned_date: string;
  expected_yield_t: number;
  grade: string;
  maturity_ratio: number;
  ripe_color: string;
}

/* ============================================================
   🎨 COLOR & STATUS LOGIC
============================================================ */
const getCropColor = (maturity: number, stress?: number): string => {
  let base = "#66bb6a"; // green
  if (maturity < 0.3) base = "#66bb6a"; // young
  else if (maturity < 0.7) base = "#fbc02d"; // yellow (intermediate)
  else base = "#e53935"; // red (ripe)
  if (stress !== undefined && stress < 0.6) base = "#8b4513"; // stressed
  return base;
};

const getReadiness = (m: number): string =>
  m < 0.3 ? "Not ready" : m < 0.7 ? "Mid-growth" : "Ready";

/* ============================================================
   🧭 HARVEST PLAN PANEL
============================================================ */
export default function HarvestPlan({ plan }: { plan: HarvestRow[] }) {
  const [sortField, setSortField] = useState<keyof HarvestRow>("planned_date");
  const [filterCrop, setFilterCrop] = useState<string>("all");
  const [selected, setSelected] = useState<string | null>(null);

  const sortedPlan = useMemo(() => {
    const filtered = filterCrop === "all" ? plan : plan.filter(p => p.crop.toLowerCase() === filterCrop.toLowerCase());
    return [...filtered].sort((a, b) =>
      sortField === "planned_date"
        ? new Date(a.planned_date).getTime() - new Date(b.planned_date).getTime()
        : (a as any)[sortField] > (b as any)[sortField] ? 1 : -1
    );
  }, [plan, sortField, filterCrop]);

  const crops = Array.from(new Set(plan.map(p => p.crop))).sort();

  /* ============================================================
     🧱 UI
  ============================================================ */
  return (
    <div className="card shadow-lg rounded-2xl bg-white p-4 w-full overflow-hidden">
      <h3 className="text-lg font-bold text-gray-700 mb-2">🌾 Harvest Plan</h3>

      {/* Controls */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex gap-2 items-center">
          <label className="text-sm text-gray-600">Filter crop:</label>
          <select
            className="border rounded px-2 py-1 text-sm"
            value={filterCrop}
            onChange={(e) => setFilterCrop(e.target.value)}
          >
            <option value="all">All</option>
            {crops.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <div className="flex gap-2 items-center">
          <label className="text-sm text-gray-600">Sort by:</label>
          <select
            className="border rounded px-2 py-1 text-sm"
            value={sortField}
            onChange={(e) => setSortField(e.target.value as keyof HarvestRow)}
          >
            <option value="planned_date">Date</option>
            <option value="expected_yield_t">Yield</option>
            <option value="grade">Grade</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-y-auto max-h-[400px] border rounded-md">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 text-gray-700 sticky top-0">
            <tr>
              <th className="text-left p-2">Field</th>
              <th className="text-left p-2">Crop</th>
              <th className="text-left p-2">Date</th>
              <th className="text-right p-2">Yield (t/ha)</th>
              <th className="text-center p-2">Grade</th>
              <th className="text-center p-2">Maturity</th>
              <th className="text-center p-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {sortedPlan.map((r, i) => (
              <motion.tr
                key={r.field_id}
                layout
                whileHover={{ backgroundColor: "#f9fafb" }}
                onClick={() => setSelected(r.field_id)}
                className={`cursor-pointer ${
                  selected === r.field_id ? "bg-blue-50" : ""
                }`}
              >
                <td className="p-2 font-medium text-gray-800">{r.field_id}</td>
                <td className="p-2 text-gray-700 capitalize">{r.crop}</td>
                <td className="p-2 text-gray-600">
                  {new Date(r.planned_date).toLocaleDateString()}
                </td>
                <td className="p-2 text-right text-gray-800 font-semibold">
                  {r.expected_yield_t.toFixed(2)}
                </td>
                <td className="p-2 text-center">
                  <span
                    className={`px-2 py-1 rounded text-white text-xs ${
                      r.grade === "A"
                        ? "bg-green-500"
                        : r.grade === "B"
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    }`}
                  >
                    {r.grade}
                  </span>
                </td>
                <td className="p-2 text-center">
                  <div className="w-24 h-3 bg-gray-200 rounded-full overflow-hidden mx-auto">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${(r.maturity_ratio * 100).toFixed(0)}%`,
                        backgroundColor: getCropColor(r.maturity_ratio),
                      }}
                    ></div>
                  </div>
                </td>
                <td className="p-2 text-center text-sm" style={{ color: getCropColor(r.maturity_ratio) }}>
                  {getReadiness(r.maturity_ratio)}
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Inspector panel */}
      {selected && (
        <div className="mt-4 border-t pt-3 text-sm">
          <h4 className="font-semibold text-gray-700 mb-2">Field Details</h4>
          {(() => {
            const sel = sortedPlan.find((x) => x.field_id === selected);
            if (!sel) return null;
            return (
              <motion.div
                layout
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-2 bg-gray-50 rounded border text-gray-700"
              >
                <p>
                  <b>Crop:</b> {sel.crop}
                </p>
                <p>
                  <b>Expected Yield:</b> {sel.expected_yield_t.toFixed(2)} t/ha
                </p>
                <p>
                  <b>Maturity:</b>{" "}
                  {(sel.maturity_ratio * 100).toFixed(1)}%
                </p>
                <p>
                  <b>Harvest Date:</b>{" "}
                  {new Date(sel.planned_date).toLocaleDateString()}
                </p>
                <p>
                  <b>Grade:</b>{" "}
                  <span
                    className={`px-2 py-1 rounded text-white text-xs ${
                      sel.grade === "A"
                        ? "bg-green-600"
                        : sel.grade === "B"
                        ? "bg-yellow-600"
                        : "bg-red-600"
                    }`}
                  >
                    {sel.grade}
                  </span>
                </p>
              </motion.div>
            );
          })()}
        </div>
      )}
    </div>
  );
}
