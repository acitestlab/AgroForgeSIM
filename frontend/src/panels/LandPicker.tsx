import React, { useEffect, useMemo, useRef, useState, useId } from 'react'
import {
  MapContainer,
  TileLayer,
  Polygon as RLPolygon,
  Polyline,
  Marker,
  Tooltip,
  useMap,
  useMapEvents,
} from 'react-leaflet'
import * as turf from '@turf/turf'
import type { Feature, Polygon as GeoJSONPolygon, MultiPolygon } from 'geojson'
import { useStore, type Field } from "../store";
import type { Geometry } from "geojson";

/** ---------------- Geo helpers ---------------- **/
function gjToLeafletLatLngs(geom?: GeoJSON.Geometry): number[][][] {
  if (!geom) return []
  if (geom.type === 'Polygon') {
    const rings = geom.coordinates as number[][][]
    return rings.map((ring) => ring.map(([lon, lat]) => [lat, lon]))
  }
  if (geom.type === 'MultiPolygon') {
    const firstPolyRings = (geom.coordinates as number[][][][])[0] as number[][][]
    return firstPolyRings.map((ring) => ring.map(([lon, lat]) => [lat, lon]))
  }
  return []
}
function latLngsToRing(coords: number[][]): number[][] { return coords.map(([lat, lon]) => [lon, lat]) }
function metersToDeg(lat: number, dx_m: number, dy_m: number) {
  const m_per_deg_lat = 111_320
  const m_per_deg_lon = 111_320 * Math.cos((lat * Math.PI) / 180)
  return { dLon: dx_m / m_per_deg_lon, dLat: dy_m / m_per_deg_lat }
}
function snapToGrid(lat: number, lon: number, grid_m: number) {
  const { dLon, dLat } = metersToDeg(lat, grid_m, grid_m)
  const latSnap = Math.round(lat / dLat) * dLat
  const lonSnap = Math.round(lon / dLon) * dLon
  return [latSnap, lonSnap] as [number, number]
}
function segMetrics(a: number[], b: number[]) {
  const p1 = turf.point([a[1], a[0]])
  const p2 = turf.point([b[1], b[0]])
  const km = turf.distance(p1, p2, { units: 'kilometers' })
  const brg = turf.bearing(p1, p2)
  return { meters: km * 1000, bearing: (brg + 360) % 360 }
}

/** ---------------- Grid Overlay ---------------- **/
function GridOverlay({ enabled, gridM }: { enabled: boolean; gridM: number }) {
  const map = useMap()
  const [lines, setLines] = useState<number[][][]>([])
  useEffect(() => {
    if (!enabled) { setLines([]); return }
    function update() {
      const b = map.getBounds()
      const sw = b.getSouthWest(); const ne = b.getNorthEast()
      const latMin = sw.lat; const lonMin = sw.lng; const latMax = ne.lat; const lonMax = ne.lng
      const midLat = (latMin + latMax) / 2
      const { dLat, dLon } = metersToDeg(midLat, gridM, gridM)
      if (!isFinite(dLat) || !isFinite(dLon) || dLat <= 0 || dLon <= 0) { setLines([]); return }
      const latLines: number[][][] = []; const lonLines: number[][][] = []
      const startLat = Math.floor(latMin / dLat) * dLat
      for (let lat = startLat; lat <= latMax; lat += dLat) {
        latLines.push([[lat, lonMin],[lat, lonMax]].map(([la, lo]) => [la, lo])); if (latLines.length > 400) break
      }
      const startLon = Math.floor(lonMin / dLon) * dLon
      for (let lon = startLon; lon <= lonMax; lon += dLon) {
        lonLines.push([[latMin, lon],[latMax, lon]].map(([la, lo]) => [la, lo])); if (lonLines.length > 400) break
      }
      setLines([...latLines, ...lonLines])
    }
    update()
    map.on('moveend', update); map.on('zoomend', update)
    return () => { map.off('moveend', update); map.off('zoomend', update) }
  }, [enabled, gridM, map])

  if (!enabled) return null
  return <>{lines.map((ll, i) => (<Polyline key={i} positions={ll as any} pathOptions={{ color: '#e5e7eb', weight: 1 }} />))}</>
}

/** ---------------- Map capture (click, freehand) ---------------- **/
function ClickAndDraw({
  drawingPolygon, drawingFree, addVertex, pushFreehand, finishFreehand,
}: {
  drawingPolygon: boolean; drawingFree: boolean;
  addVertex: (lat: number, lon: number) => void;
  pushFreehand: (lat: number, lon: number) => void;
  finishFreehand: () => void;
}) {
  const isDown = useRef(false)
  useMapEvents({
    click(e) { if (drawingPolygon) addVertex(e.latlng.lat, e.latlng.lng) },
    mousedown(e) { if (drawingFree) { isDown.current = true; pushFreehand(e.latlng.lat, e.latlng.lng) } },
    mousemove(e) { if (drawingFree && isDown.current) { pushFreehand(e.latlng.lat, e.latlng.lng) } },
    mouseup() { if (drawingFree && isDown.current) { isDown.current = false; finishFreehand() } },
  })
  return null
}

/** ---------------- Component ---------------- **/
export default function LandPicker() {
  const fields = useStore((s) => s.fields)
  const updateField = useStore((s) => s.updateField)
  const addField = useStore((s) => s.addField)

  const [sel, setSel] = useState<string>("");
  useEffect(() => {
    if (fields.length === 0) { const id = addField("Field A"); setSel(id) }
    else if (!sel) { setSel(fields[0].id) }
  }, [fields.length]) // eslint-disable-line

  const field = useMemo(() => fields.find((f) => f.id === sel), [fields, sel])

  // Rectangle parameters
  const [rect, setRect] = useState({ centerLat: 6.5, centerLon: 3.3, length_m: 200, width_m: 100, bearing_deg: 0 })

  // Modes & options
  const [drawingPoly, setDrawingPoly] = useState(false)
  const [freehand, setFreehand] = useState(false)
  const [snap, setSnap] = useState(true)
  const [gridM, setGridM] = useState(5)
  const [showGrid, setShowGrid] = useState(true)
  const [snapBearing, setSnapBearing] = useState(true)
  const [bearingStep, setBearingStep] = useState(15)
  const [bearingBase, setBearingBase] = useState(0)
  const [concavityM, setConcavityM] = useState(50)
  const [simplifyM, setSimplifyM] = useState(0.5)

  // Editor vertices
  const [points, setPoints] = useState<number[][]>([])
  const freeStream = useRef<number[][]>([])

  /** -------- Upload / Rectangle -------- **/
  function onUploadGeoJSON(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]; if (!f) return
    const reader = new FileReader()
    reader.onload = () => {
      try {
        const gj = JSON.parse(reader.result as string)
        let geom: GeoJSONPolygon | MultiPolygon | null = null
        if (gj.type === 'Feature') {
          const g = (gj as Feature).geometry
          if (g?.type === 'Polygon' || g?.type === 'MultiPolygon') geom = g as GeoJSONPolygon | MultiPolygon
        } else if (gj.type === 'FeatureCollection') {
          const g = (gj as GeoJSON.FeatureCollection).features?.[0]?.geometry
          if (g?.type === 'Polygon' || g?.type === 'MultiPolygon') geom = g as GeoJSONPolygon | MultiPolygon
        } else if (gj.type === 'Polygon' || gj.type === 'MultiPolygon') {
          geom = gj as GeoJSONPolygon | MultiPolygon
        }
        if (!geom) { alert('No Polygon/MultiPolygon geometry found in file.'); return }
        const area_ha = turf.area(geom) / 10000.0
        if (!sel) { alert('Select a field first.'); return }
        updateField(sel, { geometry: geom, area_ha: Number(area_ha.toFixed(3)) })
        const ll = gjToLeafletLatLngs(geom); if (ll.length > 0) setPoints(ll[0])
      } catch (err: any) { alert('Invalid GeoJSON: ' + err.message) }
    }
    reader.readAsText(f)
  }

  function createRectangle() {
    try {
      const { centerLat, centerLon, length_m, width_m, bearing_deg } = rect
      const center = turf.point([centerLon, centerLat])
      const halfL = length_m / 2; const halfW = width_m / 2
      const p1 = turf.destination(center, halfL / 1000, bearing_deg, { units: 'kilometers' })
      const p2 = turf.destination(center, halfL / 1000, bearing_deg + 180, { units: 'kilometers' })
      const left = bearing_deg - 90; const right = bearing_deg + 90
      const p1L = turf.destination(p1, halfW / 1000, left, { units: 'kilometers' })
      const p1R = turf.destination(p1, halfW / 1000, right, { units: 'kilometers' })
      const p2L = turf.destination(p2, halfW / 1000, left, { units: 'kilometers' })
      const p2R = turf.destination(p2, halfW / 1000, right, { units: 'kilometers' })
      const coords = [p1L.geometry.coordinates, p1R.geometry.coordinates, p2R.geometry.coordinates, p2L.geometry.coordinates, p1L.geometry.coordinates]
      const poly = turf.polygon([coords], { name: 'generated-rect' })
      const area_ha = turf.area(poly) / 10000.0
      if (!sel) { alert('Select a field first.'); return }
      updateField(sel, { geometry: poly.geometry as GeoJSONPolygon, area_ha: Number(area_ha.toFixed(3)) })
      setPoints(gjToLeafletLatLngs(poly.geometry)[0])
    } catch (e: any) { alert('Could not create rectangle: ' + e.message) }
  }

  /** -------- Bearing snapping -------- **/
  function snapToBearing(prev: number[], candidate: number[]) {
    if (!prev) return candidate
    const p1 = turf.point([prev[1], prev[0]]); const p2 = turf.point([candidate[1], candidate[0]])
    let brg = turf.bearing(p1, p2); brg = (brg + 360) % 360
    const step = Math.max(1, bearingStep)
    const base = ((bearingBase % 360) + 360) % 360
    const snapped = Math.round((brg - base) / step) * step + base
    const km = turf.distance(p1, p2, { units: 'kilometers' })
    const pSnapped = turf.destination(p1, km, snapped, { units: 'kilometers' })
    return [pSnapped.geometry.coordinates[1], pSnapped.geometry.coordinates[0]]
  }

  /** -------- Polygon editing -------- **/
  function addVertex(lat: number, lon: number) {
    let [la, lo] = snap ? snapToGrid(lat, lon, gridM) : [lat, lon]
    if (snapBearing && points.length >= 1) {
      ;[la, lo] = snapToBearing(points[points.length - 1], [la, lo]); if (snap) [la, lo] = snapToGrid(la, lo, gridM)
    }
    setPoints((prev) => [...prev, [la, lo]])
  }
  function finishPolygonFromPoints(pts: number[][]) {
    if (pts.length < 3) { alert('Need at least 3 vertices.'); return }
    const ring = latLngsToRing(pts)
    const closed = ring[0][0] === ring[ring.length - 1][0] && ring[0][1] === ring[ring.length - 1][1] ? ring : [...ring, ring[0]]
    let poly: Feature<GeoJSONPolygon> | null = turf.polygon([closed]) as Feature<GeoJSONPolygon>
    try {
      const unk = turf.unkinkPolygon(poly as any)
      if ((unk as any).features?.length) poly = (unk as any).features[0] as Feature<GeoJSONPolygon>
    } catch {}
    const area_ha = turf.area(poly as any) / 10000.0
    if (!sel) { alert('Select a field first.'); return }
    updateField(sel, { geometry: (poly as Feature<GeoJSONPolygon>).geometry, area_ha: Number(area_ha.toFixed(3)) })
  }
  function finishPolygon() { finishPolygonFromPoints(points); setDrawingPoly(false); setFreehand(false) }
  function onDragVertex(i: number, lat: number, lon: number) {
    let [la, lo] = snap ? snapToGrid(lat, lon, gridM) : [lat, lon]
    if (snapBearing) {
      const prev = points[(i - 1 + points.length) % points.length] ?? points[i - 1]
      if (prev) { ;[la, lo] = snapToBearing(prev, [la, lo]) }
      if (snap) [la, lo] = snapToGrid(la, lo, gridM)
    }
    setPoints((prev) => prev.map((p, idx) => (idx === i ? [la, lo] : p)))
  }
  function deleteVertex(i: number) { setPoints((prev) => prev.filter((_, idx) => idx !== i)) }

  /** -------- Freehand (concave hull) -------- **/
  function pushFreehand(lat: number, lon: number) {
    const last = freeStream.current[freeStream.current.length - 1]
    if (last) {
      const d = turf.distance(turf.point([last[1], last[0]]), turf.point([lon, lat]), { units: 'kilometers' })
      if (d < 0.0005) return
    }
    freeStream.current.push([lat, lon])
  }
  function finishFreehand() {
    if (freeStream.current.length < 3) { freeStream.current = []; return }
    const midLat = freeStream.current[Math.floor(freeStream.current.length / 2)][0]
    const { dLat, dLon } = metersToDeg(midLat, simplifyM, simplifyM)
    const tolDeg = Math.min(dLat, dLon)
    const line = turf.lineString(freeStream.current.map(([lat, lon]) => [lon, lat]))
    const simp = turf.simplify(line, { tolerance: tolDeg, highQuality: true })
    const pts = turf.featureCollection((simp.geometry.coordinates as number[][]).map(([lon, lat]) => turf.point([lon, lat])))
    let poly: Feature<GeoJSONPolygon> | null = null
    try { poly = turf.concave(pts, { maxEdge: concavityM / 1000, units: 'kilometers' }) as unknown as Feature<GeoJSONPolygon> } catch {}
    if (!poly) { const hull = turf.convex(pts); if (hull) poly = hull as unknown as Feature<GeoJSONPolygon> }
    if (!poly) { const coords = [...(simp.geometry.coordinates as number[][])]; coords.push(coords[0]); poly = turf.polygon([coords]) as Feature<GeoJSONPolygon> }
    let ll = gjToLeafletLatLngs((poly as Feature<GeoJSONPolygon>).geometry)[0]
    if (snapBearing && ll.length > 1) {
      const snappedLine: number[][] = [ll[0]]
      for (let i = 1; i < ll.length; i++) { const s = snapToBearing(snappedLine[i - 1], ll[i]); snappedLine.push(s) }
      ll = snappedLine
    }
    if (snap) ll = ll.map(([lat, lon]) => snapToGrid(lat, lon, gridM))
    setPoints(ll)
    finishPolygonFromPoints(ll)
    freeStream.current = []
  }

  /** -------- Metrics & display -------- **/
  const geom = (field?.geometry ?? undefined) as Geometry | undefined;
  const latlngsSaved = useMemo(() => gjToLeafletLatLngs(geom), [geom])
  const mapCenter = useMemo(() => {
    if (field?.geometry) {
      try { const c = turf.center(field.geometry).geometry.coordinates; return [c[1], c[0]] } catch {}
    }
    return [rect.centerLat, rect.centerLon]
  }, [field?.geometry, rect.centerLat, rect.centerLon])
  const metrics = useMemo(() => {
    if (points.length < 2) return { areaHa: 0, segments: [] as any[] }
    const ring = latLngsToRing(points)
    const closed = ring[0][0] === ring[ring.length - 1][0] && ring[0][1] === ring[ring.length - 1][1] ? ring : [...ring, ring[0]]
    const poly = turf.polygon([closed])
    let areaHa = 0; try { areaHa = turf.area(poly) / 10000.0 } catch { areaHa = 0 }
    const segs: any[] = []
    for (let i = 0; i < points.length; i++) {
      const a = points[i]; const b = points[(i + 1) % points.length]; if (!a || !b) continue
      const { meters, bearing } = segMetrics(a, b); segs.push({ mid: [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], meters, bearing })
    }
    return { areaHa, segments: segs }
  }, [points])

  /** -------- Unique ids for labels/inputs -------- **/
  const rid = useId()
  const idSel = `landpicker-${rid}-field`
  const idUpload = `landpicker-${rid}-upload`
  const idLat = `landpicker-${rid}-center-lat`
  const idLon = `landpicker-${rid}-center-lon`
  const idLen = `landpicker-${rid}-length`
  const idWid = `landpicker-${rid}-width`
  const idBrg = `landpicker-${rid}-bearing`

  /** -------- UI -------- **/
  return (
    <div className="card">
      <h3>Land Picker</h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 6, alignItems: 'center' }}>
        <label htmlFor={idSel}>Field</label>
        <select id={idSel} value={sel} onChange={(e) => setSel(e.target.value)}>
          {fields.map((f: Field) => (
            <option key={f.id} value={f.id}>
              {f.name} ({f.id})
            </option>
          ))}
        </select>

        <label htmlFor={idUpload}>Upload survey (GeoJSON)</label>
        <input id={idUpload} type="file" accept=".geojson,application/geo+json,application/json" onChange={onUploadGeoJSON} />
      </div>

      <h4 style={{ marginTop: 10 }}>Generate rectangle</h4>
      <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr auto 1fr', gap: 6, alignItems: 'center' }}>
        <label htmlFor={idLat}>Center Lat</label>
        <input
          id={idLat}
          type="number"
          value={rect.centerLat}
          onChange={(e) => setRect({ ...rect, centerLat: Number(e.target.value) })}
        />
        <label htmlFor={idLon}>Center Lon</label>
        <input
          id={idLon}
          type="number"
          value={rect.centerLon}
          onChange={(e) => setRect({ ...rect, centerLon: Number(e.target.value) })}
        />
        <label htmlFor={idLen}>Length (m)</label>
        <input
          id={idLen}
          type="number"
          value={rect.length_m}
          onChange={(e) => setRect({ ...rect, length_m: Number(e.target.value) })}
        />
        <label htmlFor={idWid}>Width (m)</label>
        <input
          id={idWid}
          type="number"
          value={rect.width_m}
          onChange={(e) => setRect({ ...rect, width_m: Number(e.target.value) })}
        />
        <label htmlFor={idBrg}>Bearing (°)</label>
        <input
          id={idBrg}
          type="number"
          value={rect.bearing_deg}
          onChange={(e) => setRect({ ...rect, bearing_deg: Number(e.target.value) })}
        />
      </div>
      <button onClick={createRectangle} style={{ marginTop: 8 }}>
        Create Plot
      </button>

      <h4 style={{ marginTop: 10 }}>Manual editing</h4>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
        <button onClick={() => { setDrawingPoly((s) => !s); setFreehand(false) }} style={{ minWidth: 140 }}>
          {drawingPoly ? 'Stop Polygon' : 'Draw Polygon'}
        </button>
        <button onClick={() => { setFreehand((s) => !s); setDrawingPoly(false); freeStream.current = [] }} style={{ minWidth: 140 }}>
          {freehand ? 'Stop Freehand' : 'Freehand Sketch'}
        </button>
        <button onClick={finishPolygon} disabled={points.length < 3}>Finish / Save</button>
        <button onClick={() => setPoints([])} disabled={points.length === 0}>Clear Points</button>

        {/* Labels below wrap inputs, so htmlFor is not required */}
        <label style={{ marginLeft: 12 }}>
          <input type="checkbox" checked={snap} onChange={(e) => setSnap(e.target.checked)} /> Snap to grid
        </label>
        <label>
          Grid (m)
          <input
            type="number" min={1} step={1} value={gridM}
            onChange={(e) => setGridM(Math.max(1, Number(e.target.value) || 1))}
            style={{ width: 70, marginLeft: 6 }}
          />
        </label>
        <label style={{ marginLeft: 12 }}>
          <input type="checkbox" checked={showGrid} onChange={(e) => setShowGrid(e.target.checked)} /> Show grid
        </label>
        <label style={{ marginLeft: 12 }}>
          <input type="checkbox" checked={snapBearing} onChange={(e) => setSnapBearing(e.target.checked)} /> Snap bearing
        </label>
        <label>
          Step (°)
          <input
            type="number" min={1} step={1} value={bearingStep}
            onChange={(e) => setBearingStep(Math.max(1, Number(e.target.value) || 1))}
            style={{ width: 60, marginLeft: 6 }}
          />
        </label>
        <label>
          Base (°)
          <input
            type="number" min={0} max={359} step={1} value={bearingBase}
            onChange={(e) => setBearingBase(((Number(e.target.value) || 0) % 360 + 360) % 360)}
            style={{ width: 60, marginLeft: 6 }}
          />
        </label>
        <label style={{ marginLeft: 12 }}>
          Concavity (m)
          <input
            type="number" min={5} step={1} value={concavityM}
            onChange={(e) => setConcavityM(Math.max(5, Number(e.target.value) || 50))}
            style={{ width: 90, marginLeft: 6 }}
          />
        </label>
        <label>
          Simplify (m)
          <input
            type="number" min={0} step={0.1} value={simplifyM}
            onChange={(e) => setSimplifyM(Math.max(0, Number(e.target.value) || 0.5))}
            style={{ width: 90, marginLeft: 6 }}
          />
        </label>
      </div>

      <div style={{ height: 420, marginTop: 8, border: '1px solid #eee', borderRadius: 8, overflow: 'hidden', position: 'relative' }}>
        <MapContainer
          center={mapCenter as any}
          zoom={16}
          style={{ height: '100%', width: '100%', cursor: drawingPoly || freehand ? 'crosshair' : 'default' }}
          doubleClickZoom={false}
        >
          <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <GridOverlay enabled={showGrid} gridM={gridM} />
          {latlngsSaved.length > 0 && (
            <RLPolygon positions={latlngsSaved as unknown as [number, number][][]} pathOptions={{ color: '#2e7d32', weight: 2 }} />
          )}
          {points.length >= 1 && (
            <>
              <Polyline positions={points as any} pathOptions={{ color: '#1976d2', weight: 2, dashArray: '4 4' }} />
              {points.map((p, idx) => (
                <Marker key={idx} position={p as any} draggable
                  eventHandlers={{
                    dragend: (e: any) => { const lat = e.target.getLatLng().lat; const lon = e.target.getLatLng().lng; onDragVertex(idx, lat, lon) },
                    contextmenu: () => deleteVertex(idx),
                  }}>
                  <Tooltip direction="top" offset={[0, -10]} opacity={0.9}>
                    <div>Vertex {idx + 1}</div><div>Lat {p[0].toFixed(6)}</div><div>Lon {p[1].toFixed(6)}</div>
                  </Tooltip>
                </Marker>
              ))}
              {metrics.segments.map((s: any, i: number) => (
                <Marker key={`seg-${i}`} position={s.mid as any} interactive={false} opacity={0}>
                  <Tooltip permanent direction="right" offset={[8, 0]} opacity={0.85} className="seg-label">
                    {(s.meters >= 1000 ? (s.meters / 1000).toFixed(3) + ' km' : s.meters.toFixed(1) + ' m') + ' • ' + s.bearing.toFixed(1) + '°'}
                  </Tooltip>
                </Marker>
              ))}
            </>
          )}
          <ClickAndDraw drawingPolygon={drawingPoly} drawingFree={freehand} addVertex={addVertex} pushFreehand={pushFreehand} finishFreehand={finishFreehand} />
        </MapContainer>

        <div style={{ position: 'absolute', right: 10, bottom: 10, background: 'rgba(255,255,255,0.9)', border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 10px', fontSize: 12 }}>
          Area (live): <strong>{metrics.areaHa.toFixed(4)} ha</strong>
        </div>
      </div>

      <p style={{ marginTop: 8 }}>
        {field?.geometry ? <>Saved area: <strong>{(field.area_ha ?? metrics.areaHa).toFixed(3)} ha</strong></> : 'No geometry saved yet.'}
      </p>
      <p style={{ fontSize: 12, color: '#555' }}>
        Bearing snap aligns edges to a {bearingStep}° grid (base {bearingBase}°). Right-click a vertex to delete it.
        Grid snapping is geodesic-aware via local meters→degrees. Segment labels show length and azimuth.
      </p>
    </div>
  )
}
