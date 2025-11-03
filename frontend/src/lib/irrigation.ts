// src/lib/irrigation.ts
export type Topology = any;
export type IrrigationParams = { mmPerEvent?: number; count?: number };

export function allocateIrrigationFromTopology(
  _topology: Topology,
  params: IrrigationParams = {}
) {
  // Minimal, safe default so UI renders
  const mm = params.mmPerEvent ?? 20;
  const count = params.count ?? 2;
  return {
    events: Array.from({ length: count }, (_, i) => ({
      day: 30 + i * 30,
      mm,
      note: "Irrigation (stub)",
    })),
    water_mm: mm * count,
  };
}
