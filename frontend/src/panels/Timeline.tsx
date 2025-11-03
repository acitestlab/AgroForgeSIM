import React, { useMemo } from "react";
import Button from "../components/Button";
import { useStore, type Task } from "../store";

function parseDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function formatDateLabel(task: Task) {
  const parsed = parseDate(task.date);
  if (!parsed) return task.date;
  return parsed.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function formatLongDate(value: string) {
  const parsed = parseDate(value);
  if (!parsed) return value;
  return parsed.toLocaleDateString(undefined, {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

export default function Timeline() {
  const plan = useStore((s) => (Array.isArray(s.result?.plan) ? (s.result!.plan as Task[]) : []));
  const loading = useStore((s) => !!s.loading?.sim);
  const runSim = useStore((s) => s.runSim);
  const nodes = useStore((s) => s.nodes ?? []);
  const selectedId = useStore((s) => s.selectedId);

  const selectedName = useMemo(() => {
    if (selectedId) {
      const found = nodes.find((n) => n.id === selectedId);
      if (found) return found.name ?? found.label ?? "Selected field";
    }
    const first = nodes[0];
    return first?.name ?? first?.label ?? "Selected field";
  }, [nodes, selectedId]);

  const sortedPlan = useMemo(() => {
    const items = Array.isArray(plan) ? [...plan] : [];
    items.sort((a, b) => {
      const da = parseDate(a.date)?.getTime() ?? Number.MAX_SAFE_INTEGER;
      const db = parseDate(b.date)?.getTime() ?? Number.MAX_SAFE_INTEGER;
      return da - db;
    });
    return items;
  }, [plan]);

  return (
    <div className="card" role="region" aria-labelledby="timeline-title" style={{ display: "grid", gap: 12 }}>
      <header style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div>
          <h3 id="timeline-title" style={{ margin: 0 }}>
            Field timeline
          </h3>
          <small style={{ opacity: 0.75 }}>Operations for {selectedName}</small>
        </div>
        <Button
          variant="secondary"
          onClick={() => runSim?.()}
          disabled={loading}
          style={{ marginLeft: "auto" }}
        >
          Refresh plan
        </Button>
      </header>

      {loading && <p aria-live="polite">Fetching the latest plan…</p>}

      {!loading && sortedPlan.length === 0 && (
        <div>
          <p style={{ margin: "8px 0" }}>No scheduled operations yet.</p>
          <Button onClick={() => runSim?.()}>Generate timeline</Button>
        </div>
      )}

      {!loading && sortedPlan.length > 0 && (
        <ol
          className="timeline-list"
          style={{
            listStyle: "none",
            padding: 0,
            margin: 0,
            display: "grid",
            gap: 10,
            maxHeight: 260,
            overflowY: "auto",
          }}
        >
          {sortedPlan.map((task, idx) => (
            <li
              key={`${task.date}-${task.op}-${idx}`}
              style={{
                display: "grid",
                gridTemplateColumns: "120px 1fr",
                gap: 12,
                alignItems: "start",
                padding: "10px 12px",
                borderRadius: 10,
                background: "rgba(15, 23, 42, 0.35)",
                border: "1px solid rgba(148, 163, 184, 0.18)",
                boxShadow: "0 4px 12px rgba(15, 23, 42, 0.25)",
              }}
            >
              <div>
                <div style={{ fontWeight: 700 }}>{formatDateLabel(task)}</div>
                <div style={{ fontSize: 12, opacity: 0.7 }}>{formatLongDate(task.date)}</div>
              </div>
              <div>
                <div style={{ fontWeight: 600 }}>{task.op}</div>
                <div style={{ fontSize: 13, opacity: 0.85 }}>{task.notes || "-"}</div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
