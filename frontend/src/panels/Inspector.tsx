import React, { useMemo, useId } from "react";
import Button from "../components/Button";
import { useStore } from "../store";

export default function Inspector() {
  const selectedId = useStore((s) => s.selectedId ?? null);
  const nodes = useStore((s) => s.nodes ?? []);
  const crops = useStore((s) => s.crops ?? {});
  const upsertNode = useStore((s) => s.upsertNode);
  const setCrop = useStore((s) => s.setCrop);
  const removeNode = useStore((s) => s.removeNode);

  const node = useMemo(() => {
    if (selectedId) return nodes.find((n) => n.id === selectedId) ?? null;
    return nodes[0] ?? null;
  }, [nodes, selectedId]);

  const rid = useId();
  const base = node?.id ?? rid;
  const idNode = `timeline-${base}-id`;
  const idLabel = `timeline-${base}-label`;
  const idArea = `timeline-${base}-area`;
  const idCrop = `timeline-${base}-crop`;

  const cropGroups = useMemo(() => Object.entries(crops ?? {}), [crops]);
  const allCrops = useMemo(() => cropGroups.flatMap(([, arr]) => arr), [cropGroups]);

  if (!node) {
    return <div className="card">No selection yet.</div>;
  }

  const onLabelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    upsertNode({ ...node, name: e.target.value });
  };
  const onAreaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    if (!Number.isNaN(val) && val > 0) upsertNode({ ...node, area_ha: val });
  };
  const onCropChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    if (value && (allCrops.length === 0 || allCrops.includes(value))) {
      setCrop(value);
      upsertNode({ ...node, crop: value });
    }
  };

  const canDelete = nodes.length > 1;
  const handleDelete = () => {
    if (!node || !canDelete) return;
    const confirmed = window.confirm(`Remove ${node.name || "this node"}?`);
    if (confirmed) {
      removeNode?.(node.id);
    }
  };

  return (
    <div className="card" role="region" aria-labelledby="inspector-title">
      <h3 id="inspector-title">Node Summary</h3>

      <div style={{ display: "grid", gap: 10 }}>
        <div>
          <label htmlFor={idNode} style={{ display: "block", opacity: 0.7 }}>
            ID
          </label>
          <input id={idNode} value={node.id} readOnly style={{ width: "100%" }} />
        </div>

        <div>
          <label htmlFor={idLabel} style={{ display: "block" }}>
            Label
          </label>
          <input
            id={idLabel}
            value={node.name ?? ""}
            onChange={onLabelChange}
            placeholder="Name this item"
            style={{ width: "100%" }}
          />
        </div>

        <div>
          <label htmlFor={idArea} style={{ display: "block" }}>
            Area (ha)
          </label>
          <input
            id={idArea}
            type="number"
            min={0.1}
            step={0.1}
            value={typeof node.area_ha === "number" ? node.area_ha : 1}
            onChange={onAreaChange}
            style={{ width: "100%" }}
          />
        </div>

        <div>
          <label htmlFor={idCrop} style={{ display: "block" }}>
            Crop
          </label>

          {cropGroups.length > 0 ? (
            <select
              id={idCrop}
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
            <select id={idCrop} value={node.crop ?? ""} onChange={onCropChange} style={{ width: "100%" }}>
              <option value="" disabled>
                — choose —
              </option>
            </select>
          )}
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 12 }}>
        <Button variant="ghost" onClick={handleDelete} disabled={!canDelete}>
          Remove node
        </Button>
      </div>
    </div>
  );
}
