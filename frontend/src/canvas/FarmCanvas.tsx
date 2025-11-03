import React, { useMemo } from "react";
import { Stage, Layer, Group, Text, Rect, Line, Circle } from "react-konva";
// NOTE: We intentionally do NOT import CropSprite until it's fixed to use Konva <Image />
// import { SoilBlock, Roots, NutrientBars, CropSprite } from "./sprites";
import { SoilBlock, Roots, NutrientBars } from "./sprites";
import { useStore } from "../store";

export default function FarmCanvas() {
  // Store alignment: selectedId, nodes, result
  const selectedId = useStore((s) => s.selectedId ?? null);
  const nodes = useStore((s) => s.nodes ?? []);
  const sim = useStore((s) => s.result);

  // Resolve selected node safely (fallback to first)
  const node = useMemo(
    () => (selectedId ? nodes.find((n) => n.id === selectedId) ?? null : nodes[0] ?? null),
    [nodes, selectedId]
  );

  // ---- Derive display inputs (robust to missing data)
  const crop = (node?.crop ?? (sim as any)?.crop ?? "maize").toLowerCase();
  const areaHa =
    typeof node?.area_ha === "number"
      ? node.area_ha
      : typeof (sim as any)?.area_ha === "number"
      ? (sim as any).area_ha
      : 1;

  const yieldTonnes =
    typeof (sim as any)?.yield_t === "number"
      ? (sim as any).yield_t
      : (sim as any)?.yield_estimate?.expected_yield_tonnes ?? null;

  const cycleDays =
    typeof (sim as any)?.cycle_days === "number"
      ? (sim as any).cycle_days
      : (sim as any)?.yield_estimate?.cycle_days ?? 90;

  const avgTemp =
    typeof (sim as any)?.weather_summary?.avg_temp === "number"
      ? (sim as any).weather_summary.avg_temp
      : null;
  const avgPrecip =
    typeof (sim as any)?.weather_summary?.avg_precip === "number"
      ? (sim as any).weather_summary.avg_precip
      : null;

  // Heuristic maturity estimate: keep consistent with your horizon_hours if you change it
  const maturity = useMemo(() => {
    const daysRan = 180; // ~6 months if horizon_hours=24*180 in store.runSim
    return Math.max(0, Math.min(1, daysRan / (cycleDays || 180)));
  }, [cycleDays]);

  // Heuristic water "stress"
  const waterStress = useMemo<number>(() => {
    if (typeof avgPrecip !== "number") return 1.0;
    if (avgPrecip < 0.5) return 0.5;
    if (avgPrecip > 5) return 0.9;
    return 0.8;
  }, [avgPrecip]);

  // Nutrients HUD — placeholder until nutrient accounting is implemented
  const N = 40,
    P = 20,
    K = 30;

  // Growth label + color cue
  const growthLabel = maturity < 1 ? (maturity < 0.5 ? "🌱 Growing" : "🌾 Ripening") : "🍎 Ripe!";
  const growthFill = useMemo(() => {
    if (maturity < 0.3) return "#66bb6a";
    if (maturity < 0.7) return "#fbc02d";
    return "#e53935";
  }, [maturity]);

  // Layout constants
  const baseY = 380;
  const soilHeight = 180;
  const plantX = 200;
  const width = 760;

  // Crop-type placement tweaks
  const isFruit = ["mango", "apple", "orange", "banana", "pineapple", "guava", "papaya", "lemon", "grapes"].includes(
    crop
  );
  const isBulb = ["onion", "garlic"].includes(crop);
  const isRoot = ["cassava", "yams", "carrot", "beet"].includes(crop);
  const isGrain = ["maize", "rice", "sorghum"].includes(crop);
  const isLegume = ["beans", "cowpea", "chickpea", "lentils", "fava beans", "mung bean"].includes(crop);
  const isLeafy = ["spinach", "amaranth", "cabbage", "pepper", "tomato", "okra", "broccoli", "cucumber"].includes(crop);

  return (
    <Stage width={900} height={450}>
      <Layer>
        {/* Top meta */}
        <Text text={`Crop: ${crop.toUpperCase()}`} x={10} y={10} fontSize={16} fontStyle="bold" />
        <Text
          text={`Yield: ${yieldTonnes !== null ? Number(yieldTonnes).toFixed(2) : "-"} t  •  Area: ${areaHa} ha`}
          x={10}
          y={30}
          fontSize={14}
        />
        <Text
          text={`Avg Temp: ${avgTemp ?? "-"}°C  •  Avg Precip: ${avgPrecip ?? "-"} mm`}
          x={10}
          y={50}
          fontSize={14}
        />
        <Text
          text={`Growth: ${(maturity * 100).toFixed(0)}%  •  Water stress: ${(waterStress * 100).toFixed(0)}%`}
          x={10}
          y={70}
          fontSize={14}
        />

        <Group x={80} y={baseY}>
          {/* Soil and roots */}
          <SoilBlock x={0} y={-soilHeight} width={width} height={soilHeight} moisture={120 /* proxy */} />
          <Roots x={plantX - 50} y={-20} depth={130} width={160} />

          {/* ------------------------------------------------------------------
              Crop sprite placeholder (vector-only, no <img/> to avoid Konva warning)
              TODO: Once ./sprites/CropSprite renders `react-konva` <Image />*not* `<img/>`,
                    you can remove this block and restore <CropSprite cropName={crop} />.
             ------------------------------------------------------------------ */}
          <Group>
            {/* Simple plant icon made of vector shapes (safe in Konva minimal) */}
            <Line
              points={[plantX, -40, plantX, -180]}
              stroke="#2e7d32"
              strokeWidth={4}
              lineCap="round"
              lineJoin="round"
            />
            <Circle x={plantX - 16} y={-150} radius={10} fill="#43a047" />
            <Circle x={plantX + 16} y={-135} radius={12} fill="#43a047" />
            <Circle x={plantX - 10} y={-110} radius={12} fill="#43a047" />
          </Group>

          {/* If/when CropSprite is fixed:
              <Group>
                <CropSprite cropName={crop} />
              </Group>
          */}

          {/* Growth label */}
          <Group>
            <Text text={growthLabel} x={plantX - 20} y={-220} fill={growthFill} fontStyle="bold" />
          </Group>

          {/* Nutrient HUD */}
          <NutrientBars x={width - 180} y={-150} N={N} P={P} K={K} />
        </Group>

        {/* Stress alert */}
        <Text text={waterStress < 0.6 ? "⚠️ Water Stress Detected" : ""} x={640} y={10} fill="#d32f2f" fontStyle="bold" />
      </Layer>
    </Stage>
  );
}
