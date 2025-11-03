// e.g., src/components/MapIbese.tsx
import { useEffect } from "react";
import L from "leaflet";
import type { FeatureCollection } from "geojson";
import { useMap } from "react-leaflet";

export default function MapIbese() {
  const map = useMap();

  useEffect(() => {
    (async () => {
      const res = await fetch("/data/ibese_perimeter_wgs84_corrected.geojson");
      const gj: FeatureCollection = await res.json();

      // Fit bounds once it loads
      const layer = L.geoJSON(gj);
      map.fitBounds(layer.getBounds());
    })();
  }, [map]);

  return null;
}
