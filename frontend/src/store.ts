// src/store.ts
import { create } from "zustand";
import { devtools, persist, createJSONStorage } from "zustand/middleware";
import type { Geometry, Polygon, MultiPolygon, Feature } from "geojson";

/* ---------------------------- Types & helpers ---------------------------- */

export type Task = { date: string; op: string; notes?: string };
export type SimResult = { yield_t?: number; plan?: Task[] } & Record<string, any>;

export type Node = {
  id: string;
  name: string;
  label?: string;
  crop?: string;
  area_ha?: number;
  area_acres?: number;
  type?: "plot" | "weather" | "irrigation" | string;
};

export type Pos = { x: number; y: number };
export type Link = { id: string; from: string; to: string };

export type Field = {
  id: string;
  name: string;
  geometry?: Geometry | null; // allow Polygon | MultiPolygon | null
  area_ha?: number;
};

type Crops = Record<string, string[]>;

type LoadingFlags = { crops?: boolean; sim?: boolean; simulate?: boolean; forecast?: boolean };

type State = {
  // crop & catalog
  crop: string;
  crops?: Crops;

  // sim / ui
  loading: LoadingFlags;
  error?: string;
  result?: SimResult;

  // location used for simulation (fallback if no field geometry)
  lat: number;
  lon: number;

  // land data
  fields: Field[];
  selectedId: string | null; // selected node/field id

  // (legacy / optional) graph-ish bits some panels might read
  nodes: Node[];
  positions: Record<string, Pos>;
  links: Link[];
};

type Actions = {
  init: () => Promise<void>;
  setCrop: (c: string) => void;
  setLocation: (lat: number, lon: number) => void;

  // land / selection
  addField: (name?: string) => string; // returns new id
  updateField: (id: string, patch: Partial<Field>) => void;
  setSelected: (id: string | null) => void;

  // node convenience for canvases that expect a "nodes" list
  upsertNode: (n: Node) => void;
  addNode: (payload: Partial<Node> & { id?: string }) => string;
  updateNode: (id: string, patch: Partial<Node>) => void;
  removeNode: (id: string) => void;
  addLink: (from: string, to: string) => void;
  setPosition: (id: string, pos: Pos) => void;
  select: (id: string | null | undefined) => void;

  runSim: () => Promise<void>;
};

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function centroidLonLat(geom?: Geometry | null): [number, number] | null {
  try {
    if (!geom) return null;
    if (geom.type === "Polygon") {
      const ring = geom.coordinates[0];
      if (!ring?.length) return null;
      let sx = 0,
        sy = 0;
      for (const [lon, lat] of ring) {
        sx += lon;
        sy += lat;
      }
      return [sx / ring.length, sy / ring.length];
    }
    if (geom.type === "MultiPolygon") {
      const ring = geom.coordinates?.[0]?.[0];
      if (!ring?.length) return null;
      let sx = 0,
        sy = 0;
      for (const [lon, lat] of ring) {
        sx += lon;
        sy += lat;
      }
      return [sx / ring.length, sy / ring.length];
    }
  } catch {
    /* ignore */
  }
  return null;
}

/* ---------------------------------- Store --------------------------------- */

export const useStore = create<State & Actions>()(
  devtools(
    persist(
      (set, get) => ({
        /* -------- defaults that prevent `.find` crashes -------- */
        crop: "cassava",
        crops: undefined,
        loading: {},
        error: undefined,
        result: undefined,

        lat: 6.95,
        lon: 3.13,

        // Start with one node/field so UI has something to render
        nodes: [
          {
            id: "root",
            name: "Field A",
            label: "Field A",
            crop: "cassava",
            area_ha: 1,
            area_acres: 2.47,
            type: "plot",
          },
        ],
        fields: [{ id: "root", name: "Field A", geometry: null, area_ha: 1 }],
        selectedId: "root",
        positions: { root: { x: 160, y: 180 } },
        links: [],

        /* ----------------------------- actions ----------------------------- */
        async init() {
          try {
            set({ loading: { ...get().loading, crops: true }, error: undefined });
            const r = await fetch(`${API_BASE}/api/crops`);
            if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
            const data = (await r.json()) as { categories: Crops };
            set({ crops: data.categories });
          } catch (e: any) {
            console.error("init() failed:", e);
            set({ error: String(e?.message || e) });
          } finally {
            set({ loading: { ...get().loading, crops: false } });
          }
        },

        setCrop(c) {
          set({ crop: c });
          // mirror into selected node if exists
          const sel = get().selectedId;
          if (sel) {
            const n = get().nodes.find((x) => x.id === sel);
            if (n) get().upsertNode({ ...n, crop: c });
          }
        },

        setLocation(lat, lon) {
          set({ lat, lon });
        },

        addField(name = "") {
          const id = globalThis.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2);
          const nextName = name || `Field ${get().fields.length + 1}`;

          const field: Field = { id, name: nextName, geometry: null, area_ha: undefined };
          set({ fields: [...get().fields, field] });

          // create/align a node as well for canvases
          const node: Node = {
            id,
            name: nextName,
            label: nextName,
            crop: get().crop,
            area_ha: field.area_ha,
            type: "plot",
          };
          const others = get().nodes.filter((x) => x.id !== id);
          set({
            nodes: [...others, node],
            selectedId: id,
            positions: { ...get().positions, [id]: { x: 120 + others.length * 60, y: 160 + others.length * 20 } },
          });

          return id;
        },

        updateField(id, patch) {
          const updated = get().fields.map((f) => (f.id === id ? { ...f, ...patch } : f));
          set({ fields: updated });

          // sync area/crop/name to the mirror node if present
          const mirror = get().nodes.find((n) => n.id === id);
          if (mirror) {
            const f = updated.find((x) => x.id === id);
            if (f) {
              get().upsertNode({
                ...mirror,
                name: f.name ?? mirror.name,
                area_ha: f.area_ha ?? mirror.area_ha,
              });
            }
          }

          // if geometry updated, move lat/lon to centroid for sim
          const geom = patch.geometry ?? updated.find((f) => f.id === id)?.geometry ?? null;
          const c = centroidLonLat(geom);
          if (c) {
            const [lon, lat] = c;
            set({ lon, lat });
          }
        },

        setSelected(id) {
          set({ selectedId: id });
        },

        upsertNode(n) {
          const others = get().nodes.filter((x) => x.id !== n.id);
          set({ nodes: [...others, n] });
        },

        addNode(payload) {
          const id = payload.id ?? (globalThis.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2));
          const label = payload.label ?? payload.name ?? `Node ${get().nodes.length + 1}`;
          const areaHaFromAcres =
            typeof payload.area_acres === "number" ? Number(payload.area_acres) * 0.404686 : undefined;
          const node: Node = {
            id,
            name: label,
            label,
            crop: payload.crop ?? get().crop,
            area_ha: typeof payload.area_ha === "number" ? payload.area_ha : areaHaFromAcres,
            area_acres: payload.area_acres,
            type: payload.type ?? "plot",
          };
          const others = get().nodes.filter((x) => x.id !== id);
          set({
            nodes: [...others, node],
            selectedId: id,
            positions: { ...get().positions, [id]: get().positions[id] ?? { x: 140 + others.length * 60, y: 180 } },
          });
          return id;
        },

        updateNode(id, patch) {
          const updated = get().nodes.map((n) => (n.id === id ? { ...n, ...patch, name: patch.label ?? patch.name ?? n.name } : n));
          set({ nodes: updated });
        },

        removeNode(id) {
          set({
            nodes: get().nodes.filter((n) => n.id !== id),
            links: get().links.filter((l) => l.from !== id && l.to !== id),
          });
        },

        addLink(from, to) {
          const existing = get().links.find((l) => l.from === from && l.to === to);
          if (existing || from === to) return;
          const id = `${from}__${to}`;
          set({ links: [...get().links, { id, from, to }] });
        },

        setPosition(id, pos) {
          set({ positions: { ...get().positions, [id]: pos } });
        },

        select(id) {
          set({ selectedId: id ?? null });
        },

        async runSim() {
          const { crop, lat, lon, fields, selectedId } = get();

          // Prefer centroid of selected field if it has geometry
          const selField = fields.find((f) => f.id === selectedId) ?? fields[0] ?? null;
          const c = centroidLonLat(selField?.geometry ?? null);
          const useLat = c ? c[1] : lat;
          const useLon = c ? c[0] : lon;

          try {
            set({ loading: { ...get().loading, sim: true, simulate: true }, error: undefined });

            // Match your FastAPI /api/simulate
            const body = {
              crop,
              lat: useLat,
              lon: useLon,
              horizon_hours: 24 * 180, // ~6 months
            };

            const r = await fetch(`${API_BASE}/api/simulate`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(body),
            });

            if (!r.ok) {
              const msg = await r.text();
              throw new Error(`${r.status} ${r.statusText} :: ${msg}`);
            }

            const data = (await r.json()) as SimResult;
            set({ result: data });
            console.log("Simulation result:", data);
          } catch (e: any) {
            console.error("runSim() failed:", e);
            set({ error: String(e?.message || e) });
            alert(`Simulation failed: ${String(e?.message || e)}`);
          } finally {
            set({ loading: { ...get().loading, sim: false, simulate: false } });
          }
        },
      }),
      {
        name: "AgroForgeSIM",
        version: 3,
        storage: createJSONStorage(() => localStorage),
        // Only persist light state; heavy results will be recalculated
        partialize: (s) => ({
          crop: s.crop,
          selectedId: s.selectedId,
          fields: s.fields,
          nodes: s.nodes,
          lat: s.lat,
          lon: s.lon,
          crops: s.crops,
        }),
      }
    )
  )
);
