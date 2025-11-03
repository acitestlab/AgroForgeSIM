// src/components/IbeseLayer.tsx
import { useEffect, useState } from "react";
import { GeoJSON, useMap } from "react-leaflet";
import type { FeatureCollection } from "geojson";

export default function IbeseLayer() {
  const [data, setData] = useState<FeatureCollection | null>(null);
  const map = useMap();

  useEffect(() => {
    (async () => {
      const res = await fetch("/data/ibese_perimeter_wgs84_corrected.geojson");
      const gj = (await res.json()) as FeatureCollection;
      setData(gj);
      // Fit map once the data arrives
      // (temporary Leaflet layer to compute bounds)
      // @ts-ignore
      const temp = L.geoJSON(gj);
      map.fitBounds(temp.getBounds(), { padding: [24, 24] });
    })();
  }, [map]);

  return data ? (
    <GeoJSON
      data={data}
      style={{ color: "#16a34a", weight: 2, fillColor: "#f59e0b", fillOpacity: 0.25 }}
    />
  ) : null;
}
