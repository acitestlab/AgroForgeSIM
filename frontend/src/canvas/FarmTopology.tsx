import { useEffect, useMemo, useRef, useState } from 'react'
import { Stage, Layer, Group, Circle, Line, Text, Rect } from 'react-konva'
import Button from '../components/Button'
import { useStore, type Pos, type Link } from '../store'
import { cropColor, growthColor } from './sprite-utils'

const rid = () =>
  (typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `id_${Math.random().toString(36).slice(2)}`)

export default function FarmTopology() {
  // ---- store wiring
  const nodes = useStore((s) => s.nodes)
  const positions = useStore((s) => s.positions)
  const links = useStore((s) => s.links)
  const addNode = useStore((s) => s.addNode)
  const updateNode = useStore((s) => s.updateNode)
  const removeNode = useStore((s) => s.removeNode)
  const addLink = useStore((s) => s.addLink)
  const setPosition = useStore((s) => s.setPosition)
  const select = useStore((s) => s.select)
  const setCrop = useStore((s) => s.setCrop)
  const loading = useStore((s) => s.loading)
  const error = useStore((s) => s.error)

  // ---- derived info
  const total = nodes.length
  const byType = useMemo(
    () =>
      nodes.reduce((acc, n) => {
        const key = n.type ?? 'plot'
        acc[key] = (acc[key] || 0) + 1
        return acc
      }, {} as Record<string, number>),
    [nodes]
  )
  const disabled = Boolean(loading.crops || loading.forecast || loading.simulate)

  // ---- selection & linking UI
  const [pendingLink, setPendingLink] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  // ---- keyboard shortcuts
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.altKey || e.ctrlKey || e.metaKey) return
      if ((e.target as HTMLElement)?.tagName === 'INPUT') return
      const k = e.key.toLowerCase()
      if (k === 'p') addPlot()
      else if (k === 'w') addWeather()
      else if (k === 'i') addIrrigation()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  // ---- add-node helpers
  const addPlot = () => {
    const id = rid()
    addNode({ id, type: 'plot', label: 'Plot', area_acres: 1 })
  }
  const addWeather = () => {
    const id = rid()
    addNode({ id, type: 'weather', label: 'Weather Station' })
  }
  const addIrrigation = () => {
    const id = rid()
    addNode({ id, type: 'irrigation', label: 'Irrigation' })
  }

  // ---- linking helpers
  const beginOrCompleteLink = (id: string) => {
    if (!pendingLink) {
      setPendingLink(id)
      return
    }
    if (pendingLink === id) {
      setPendingLink(null)
      return
    }
    addLink(pendingLink, id)
    setPendingLink(null)
  }

  // ---- Konva handlers
  const stageRef = useRef<any>(null)
  const onStageMouseDown = (e: any) => {
    if (e?.target?.getStage?.() === stageRef.current) {
      setSelectedId(null)
      select(undefined)
      setPendingLink(null)
    }
  }
  const onNodeDragMove = (id: string, e: any) => {
    const { x, y } = e.target.position()
    setPosition(id, { x, y } as Pos)
  }
  const onNodeClick = (id: string) => {
    setSelectedId(id)
    select(id)
    beginOrCompleteLink(id)
  }

  // ---- color helper
  const nodeFill = (t: string, crop?: string, maturity?: number, stress?: number) => {
    if (t === 'plot') {
      if (typeof maturity === 'number' || typeof stress === 'number') {
        return growthColor(maturity ?? 0.2, stress ?? 1.0)
      }
      return cropColor(crop ?? 'maize')
    }
    if (t === 'weather') return '#03a9f4'
    if (t === 'irrigation') return '#7cb342'
    return '#6b7280'
  }

  return (
    <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {/* Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        <Button onClick={addPlot} disabled={disabled} title="Add Plot (P)" aria-label="Add Plot">
          + Plot
        </Button>
        <Button onClick={addWeather} disabled={disabled} title="Add Weather (W)" aria-label="Add Weather">
          + Weather
        </Button>
        <Button onClick={addIrrigation} disabled={disabled} title="Add Irrigation (I)" aria-label="Add Irrigation">
          + Irrigation
        </Button>

        <div style={{ marginLeft: 'auto', display: 'flex', gap: 12, alignItems: 'center' }}>
          <small style={{ opacity: 0.85 }}>
            Nodes: <b>{total}</b> — plots: <b>{byType.plot || 0}</b>, weather: <b>{byType.weather || 0}</b>, irrigation:{' '}
            <b>{byType.irrigation || 0}</b>
          </small>
          {disabled && <span className="loader" aria-label="Working…" />}
          {error && (
            <small role="status" aria-live="polite" style={{ color: '#e53935' }}>
              {error}
            </small>
          )}
        </div>
      </div>

      {/* Canvas */}
      <div className="panel" style={{ padding: 8 }}>
        <Stage
          ref={stageRef}
          width={800}
          height={420}
          onMouseDown={onStageMouseDown}
          style={{ borderRadius: 8 }}
        >
          <Layer>
            {/* background grid */}
            <Rect x={0} y={0} width={800} height={420} fill="#121833" cornerRadius={8} />
            {gridLines(800, 420, 40)}

            {/* links */}
            {links.map((l: Link) => {
              const a = positions[l.from]
              const b = positions[l.to]
              if (!a || !b) return null
              return (
                <Line
                  key={l.id}
                  points={[a.x, a.y, b.x, b.y]}
                  stroke="#4a5568"
                  strokeWidth={2}
                />
              )
            })}

            {/* nodes */}
            {nodes.map((n) => {
              const p = positions[n.id] || { x: 120, y: 120 }
              const fill = nodeFill(n.type ?? 'plot', n.crop)
              const selected = selectedId === n.id
              return (
                <Group
                  key={n.id}
                  x={p.x}
                  y={p.y}
                  draggable
                  onDragMove={(e) => onNodeDragMove(n.id, e)}
                  onClick={() => onNodeClick(n.id)}
                >
                  <Circle
                    radius={26}
                    fill={fill}
                    stroke={selected ? '#000' : '#333'}
                    strokeWidth={selected ? 3 : 1.5}
                    shadowBlur={4}
                  />
                  <Text
                    text={n.label}
                    x={-36}
                    y={34}
                    fontSize={13}
                    fill="#eaf0ff"
                  />
                </Group>
              )
            })}

            {/* link hint */}
            {pendingLink && (
              <Text text="Click a second node to link" x={16} y={12} fontSize={14} fill="#fbc02d" />
            )}
          </Layer>
        </Stage>
      </div>

      {/* Inspector */}
      {selectedId && (
        <Inspector
          id={selectedId}
          onUpdate={(patch) => updateNode(selectedId, patch)}
          onSetCrop={(c) => setCrop(c)}
          onDelete={() => removeNode(selectedId)}
        />
      )}
    </div>
  )
}

/* ----------------------------- subcomponents ----------------------------- */

function Inspector({
  id,
  onUpdate,
  onSetCrop,
  onDelete,
}: {
  id: string
  onUpdate: (patch: Partial<{ label: string; area_acres: number }>) => void
  onSetCrop: (crop: string) => void
  onDelete: () => void
}) {
  const node = useStore((s) => s.nodes.find((n) => n.id === id))
  const crops = useStore((s) => s.crops)

  if (!node) return null

  const groups = Object.entries(crops ?? {})
  const flat = groups.flatMap(([, arr]) => arr)

  return (
    <div className="panel" style={{ display: 'grid', gap: 8, maxWidth: 360 }}>
      <b>Inspector</b>
      <small style={{ opacity: 0.75 }}>ID: {node.id}</small>
      <label>
        Label
        <input
          type="text"
          defaultValue={node.label}
          onBlur={(e) => onUpdate({ label: e.target.value })}
          style={{ width: '100%', marginTop: 4 }}
        />
      </label>

      {node.type === 'plot' && (
        <>
          <label>
            Crop
            <select
              defaultValue={node.crop || (flat[0] ?? 'maize')}
              onChange={(e) => onSetCrop(e.target.value)}
              style={{ width: '100%', marginTop: 4 }}
            >
              {groups.map(([group, list]) => (
                <optgroup key={group} label={group}>
                  {list.map((c) => (
                    <option key={c} value={c}>
                      {c.charAt(0).toUpperCase() + c.slice(1)}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </label>
          <label>
            Area (acres)
            <input
              type="number"
              min={0.1}
              step={0.1}
              defaultValue={node.area_acres ?? 1}
              onBlur={(e) => onUpdate({ area_acres: parseFloat(e.target.value || '1') })}
              style={{ width: '100%', marginTop: 4 }}
            />
          </label>
        </>
      )}

      <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
        <Button className="secondary" onClick={onDelete} aria-label="Delete node">
          Delete
        </Button>
      </div>
    </div>
  )
}

function gridLines(w: number, h: number, step = 40) {
  const lines: JSX.Element[] = []
  for (let x = 0; x < w; x += step) lines.push(<Line key={`vx${x}`} points={[x, 0, x, h]} stroke="#2b324a" strokeWidth={1} opacity={0.35} />)
  for (let y = 0; y < h; y += step) lines.push(<Line key={`hz${y}`} points={[0, y, w, y]} stroke="#2b324a" strokeWidth={1} opacity={0.35} />)
  return lines
}
