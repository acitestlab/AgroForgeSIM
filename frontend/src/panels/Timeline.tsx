// src/panels/Inspector.tsx
import React, { useMemo } from "react";
import { useStore } from "../store";

export default function Inspector() {
  // SAFELY read from the store (won’t throw on first render)
  const selectedId = useStore((s) => s.selectedId ?? null);
  const nodes = useStore((s) => s.nodes ?? []);
  const crops = useStore((s) => s.crops ?? {});
  const upsertNode = useStore((s) => s.upsertNode);
  const setCrop = useStore((s) => s.setCrop);

  // If you later add removeNode to the store, replace this with the real action
  const removeNode = (_id: string) => {
    alert("Delete not implemented yet in the store. Add `removeNode` to store.ts to enable.");
  };

  // Find the selected node; fall back to the first one if nothing is selected
  const node = useMemo(() => {
    if (selectedId) return nodes.find((n) => n.id === selectedId) ?? null;
    return nodes[0] ?? null;
  }, [nodes, selectedId]);

  // crops → groups; avoid crashing when crops is undefined/null
  const cropGroups = useMemo(() => Object.entries(crops), [crops]);
  const allCrops = useMemo(
    () => cropGroups.flatMap(([, arr]) => arr),
    [cropGroups]
  );

  if (!node) {
    return <div className="card">Select a node to inspect.</div>;
  }

  const onLabelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name = e.target.value;
    upsertNode({ ...node, name }); // store uses `name` (not `label`)
  };

  const onAreaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    if (!Number.isNaN(val) && val > 0) {
      upsertNode({ ...node, area_ha: val }); // store uses `area_ha` (not `area_acres`)
    }
  };

  const onCropChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    if (value && (allCrops.length === 0 || allCrops.includes(value))) {
      // This also mirrors into selected node via setCrop in the merged store
      setCrop(value);
      // Keep node view in sync immediately
      upsertNode({ ...node, crop: value });
    }
  };

  return (
    <div className="card" role="region" aria-labelledby="inspector-title">
      <h3 id="inspector-title" style={{ marginTop: 0 }}>
        Inspector
      </h3>

      <div style={{ display: "grid", gap: 10 }}>
        <div>
          <label htmlFor="node-id" style={{ display: "block", opacity: 0.7 }}>
            ID
          </label>
          <input id="node-id" value={node.id} readOnly style={{ width: "100%" }} />
        </div>

        <div>
          <label htmlFor="node-label" style={{ display: "block" }}>
            Label
          </label>
          <input
            id="node-label"
            value={node.name ?? ""} // store’s field name is `name`
            onChange={onLabelChange}
            placeholder="Name this item"
            style={{ width: "100%" }}
          />
        </div>

        {/* Only show area & crop for plot-like nodes (keep flexible if `type` is missing) */}
        {(node as any).type === "plot" || true ? (
          <>
            <div>
              <label htmlFor="node-area" style={{ display: "block" }}>
                Area (ha)
              </label>
              <input
                id="node-area"
                type="number"
                min={0.1}
                step={0.1}
                value={typeof node.area_ha === "number" ? node.area_ha : 1}
                onChange={onAreaChange}
                style={{ width: "100%" }}
              />
            </div>

            <div>
              <label htmlFor="node-crop" style={{ display: "block" }}>
                Crop
              </label>
              {cropGroups.length > 0 ? (
                <select
                  id="node-crop"
                  value={node.crop ?? ""}
                  onChange={onCropChange}
                  style={{ width: "100%" }}
                >
                  <option value="" disabled>
                    — choose —
                  </option>
                  {cropGroups.map(([group, list]) => (
                    <optgroup key={group} label={group}>
                      {list.map((c) => (
                        <option key={c} value={c}>
                          {c.charAt(0).toUpperCase() + c.slice(1)}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              ) : (
                <select
                  id="node-crop"
                  value={node.crop ?? ""}
                  onChange={onCropChange}
                  style={{ width: "100%" }}
                >
                  <option value="" disabled>
                    — choose —
                  </option>
                </select>
              )}
            </div>
          </>
        ) : null}

        <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
          <button
            className="btn secondary"
            onClick={() => removeNode(node.id)}
            aria-label="Delete node"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
