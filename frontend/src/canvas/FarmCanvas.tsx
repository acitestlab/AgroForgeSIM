import React, { useEffect, useMemo, useRef } from "react";
import { useStore } from "../store";

const clamp = (value: number, min: number, max: number) =>
  Math.min(max, Math.max(min, value));

const FRUIT_CROPS = new Set([
  "mango",
  "apple",
  "orange",
  "banana",
  "pineapple",
  "guava",
  "papaya",
  "lemon",
  "grapes",
]);

const ROOT_CROPS = new Set(["cassava", "yams", "carrot", "beet"]);
const GRAIN_CROPS = new Set(["maize", "rice", "sorghum"]);
const LEGUME_CROPS = new Set([
  "beans",
  "cowpea",
  "chickpea",
  "lentils",
  "fava beans",
  "mung bean",
]);
const LEAFY_CROPS = new Set([
  "spinach",
  "amaranth",
  "cabbage",
  "pepper",
  "tomato",
  "okra",
  "broccoli",
  "cucumber",
]);

type Palette = {
  stem: string;
  highlight: string;
  canopy: string;
  bloom: string;
};

const paletteForCrop = (crop: string): Palette => {
  const c = crop.toLowerCase();
  if (FRUIT_CROPS.has(c)) {
    return {
      stem: "#8e24aa",
      highlight: "#f06292",
      canopy: "#f8bbd0",
      bloom: "#ff80ab",
    };
  }
  if (ROOT_CROPS.has(c)) {
    return {
      stem: "#6d4c41",
      highlight: "#d7ccc8",
      canopy: "#ffccbc",
      bloom: "#ffab91",
    };
  }
  if (GRAIN_CROPS.has(c)) {
    return {
      stem: "#2e7d32",
      highlight: "#aee571",
      canopy: "#dcedc8",
      bloom: "#ffe082",
    };
  }
  if (LEGUME_CROPS.has(c)) {
    return {
      stem: "#558b2f",
      highlight: "#a5d6a7",
      canopy: "#c5e1a5",
      bloom: "#dcedc1",
    };
  }
  if (LEAFY_CROPS.has(c)) {
    return {
      stem: "#1b5e20",
      highlight: "#66bb6a",
      canopy: "#b2ff9e",
      bloom: "#a7ffeb",
    };
  }
  return {
    stem: "#2e7d32",
    highlight: "#9ccc65",
    canopy: "#c8e6c9",
    bloom: "#f1f8e9",
  };
};

const formatNumber = (value: number | null | undefined, digits = 1) => {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return Number(value).toFixed(digits);
};

export default function FarmCanvas() {
  const selectedId = useStore((s) => s.selectedId ?? null);
  const nodes = useStore((s) => s.nodes ?? []);
  const sim = useStore((s) => s.result);

  const containerRef = useRef<HTMLDivElement | null>(null);
  const sceneRef = useRef<HTMLDivElement | null>(null);

  const node = useMemo(
    () => (selectedId ? nodes.find((n) => n.id === selectedId) ?? null : nodes[0] ?? null),
    [nodes, selectedId],
  );

  const crop = (node?.crop ?? (sim as any)?.crop ?? "maize").toLowerCase();

  const areaHa = useMemo(() => {
    if (typeof node?.area_ha === "number") return node.area_ha;
    if (typeof (sim as any)?.area_ha === "number") return (sim as any).area_ha;
    return 1;
  }, [node, sim]);

  const yieldTonnes = useMemo(() => {
    if (typeof (sim as any)?.yield_t === "number") return (sim as any).yield_t;
    const nested = (sim as any)?.yield_estimate;
    if (typeof nested?.expected_yield_tonnes === "number") return nested.expected_yield_tonnes;
    return null;
  }, [sim]);

  const cycleDays = useMemo(() => {
    if (typeof (sim as any)?.cycle_days === "number") return (sim as any).cycle_days;
    const nested = (sim as any)?.yield_estimate;
    if (typeof nested?.cycle_days === "number") return nested.cycle_days;
    return 90;
  }, [sim]);

  const avgTemp = useMemo(() => {
    if (typeof (sim as any)?.weather_summary?.avg_temp === "number") {
      return (sim as any).weather_summary.avg_temp;
    }
    return null;
  }, [sim]);

  const avgPrecip = useMemo(() => {
    if (typeof (sim as any)?.weather_summary?.avg_precip === "number") {
      return (sim as any).weather_summary.avg_precip;
    }
    return null;
  }, [sim]);

  const maturity = useMemo(() => {
    const horizonDays = 180; // matches runSim horizon
    return clamp(horizonDays / (cycleDays || horizonDays), 0, 1);
  }, [cycleDays]);

  const waterAdequacy = useMemo(() => {
    if (typeof avgPrecip !== "number") return 0.75;
    if (avgPrecip < 0.5) return 0.35;
    if (avgPrecip > 5) return 0.9;
    return 0.75;
  }, [avgPrecip]);

  const palette = useMemo(() => paletteForCrop(crop), [crop]);

  const stemHeight = useMemo(() => 130 + maturity * 120, [maturity]);
  const canopySize = useMemo(() => 90 + maturity * 80, [maturity]);
  const canopyLift = useMemo(() => 60 + maturity * 40, [maturity]);
  const waterScale = useMemo(() => 0.45 + clamp(waterAdequacy, 0.1, 1) * 0.55, [waterAdequacy]);
  const hydration = clamp(waterAdequacy, 0, 1);

  const soilColorA = useMemo(() => {
    const hue = 30 - hydration * 6;
    const lightness = 32 + hydration * 12;
    return `hsl(${hue}deg 55% ${lightness}%)`;
  }, [hydration]);

  const soilColorB = useMemo(() => {
    const hue = 24 - hydration * 4;
    const lightness = 24 + hydration * 10;
    return `hsl(${hue}deg 50% ${lightness}%)`;
  }, [hydration]);

  const canopyColor = useMemo(() => {
    const base = palette.canopy.replace("#", "");
    if (base.length !== 6) return `${palette.canopy}bf`;
    const alpha = Math.round((0.68 + maturity * 0.22) * 255);
    const hexAlpha = alpha.toString(16).padStart(2, "0");
    return `#${base}${hexAlpha}`;
  }, [maturity, palette.canopy]);

  const yieldIndex = useMemo(() => {
    if (!yieldTonnes || !areaHa) return 0;
    const perHa = yieldTonnes / areaHa;
    return clamp(perHa / 6, 0, 1); // assume 6t/ha as optimistic benchmark
  }, [yieldTonnes, areaHa]);

  const fieldSize = useMemo(() => 260 + Math.min(140, areaHa * 26), [areaHa]);

  const cssVars = useMemo(
    () =>
      ({
        "--stem-height": `${stemHeight}px`,
        "--canopy-size": `${canopySize}px`,
        "--canopy-lift": `${canopyLift}px`,
        "--crop-stem": palette.stem,
        "--crop-highlight": palette.highlight,
        "--crop-canopy": palette.canopy,
        "--crop-bloom": palette.bloom,
        "--soil-color-a": soilColorA,
        "--soil-color-b": soilColorB,
        "--water-scale": String(waterScale),
        "--sparkle-opacity": String(0.25 + yieldIndex * 0.55),
        "--field-size": `${fieldSize}px`,
        "--hydration": String(hydration),
        "--canopy-color": canopyColor,
      }) as React.CSSProperties,
    [canopyColor, canopyLift, canopySize, fieldSize, hydration, palette, soilColorA, soilColorB, stemHeight, waterScale, yieldIndex],
  );

  useEffect(() => {
    const container = containerRef.current;
    const scene = sceneRef.current;
    if (!container || !scene) return;

    let frame = 0;
    let current = -35;
    let target = current;
    let tick = 0;
    let auto = true;

    const animate = () => {
      tick += 1;
      if (auto) {
        target = -35 + Math.sin(tick / 140) * 38;
      }
      current += (target - current) * 0.08;
      scene.style.transform = `rotateX(32deg) rotateY(${current}deg)`;
      frame = requestAnimationFrame(animate);
    };

    const handleMove = (event: PointerEvent) => {
      const rect = container.getBoundingClientRect();
      const ratio = clamp((event.clientX - rect.left) / rect.width, 0, 1);
      target = -60 + ratio * 100;
      auto = false;
    };

    const handleLeave = () => {
      auto = true;
    };

    container.addEventListener("pointermove", handleMove);
    container.addEventListener("pointerleave", handleLeave);
    animate();

    return () => {
      cancelAnimationFrame(frame);
      container.removeEventListener("pointermove", handleMove);
      container.removeEventListener("pointerleave", handleLeave);
    };
  }, []);

  const growthLabel = maturity < 1 ? (maturity < 0.5 ? "Growing" : "Ripening") : "Harvest Ready";
  const hydrationLabel = hydration < 0.5 ? "Irrigation Needed" : hydration < 0.7 ? "Watch Moisture" : "Hydrated";

  return (
    <div
      ref={containerRef}
      className="farm3d"
      style={cssVars}
      role="img"
      aria-label={`3D field visualization for ${crop}`}
    >
      <div className="farm3d-inner">
        <div ref={sceneRef} className="farm3d-scene">
          <div className="farm3d-field">
            <div className="farm3d-ground" />
            <div className="farm3d-shadow" />
            <div className="farm3d-ring" />
            <div className="farm3d-water" />
            <div className="farm3d-plant">
              <div className="farm3d-stem" />
              <div className="farm3d-node" />
              <div className="farm3d-leaf leaf-left" />
              <div className="farm3d-leaf leaf-right" />
              <div className="farm3d-canopy" />
              <div className="farm3d-bloom" />
            </div>
            <div className="farm3d-sparkles" aria-hidden />
            <div className="farm3d-cloud cloud-a" aria-hidden />
            <div className="farm3d-cloud cloud-b" aria-hidden />
            <div className="farm3d-sun" aria-hidden />
          </div>
        </div>
      </div>

      <div className="farm3d-hud" role="presentation">
        <header>
          <div>
            <h2>{crop.toUpperCase()}</h2>
            <p>
              {growthLabel} · {hydrationLabel}
            </p>
          </div>
          <div className="farm3d-yield-chip">
            <span>{formatNumber(yieldTonnes, 2)}</span>
            <small>t expected</small>
          </div>
        </header>

        <section className="farm3d-stats">
          <article>
            <h3>Growth Cycle</h3>
            <div className="farm3d-bar" aria-label={`Growth ${Math.round(maturity * 100)} percent`}>
              <div style={{ width: `${Math.round(maturity * 100)}%` }} />
            </div>
            <footer>
              <span>{Math.round(maturity * 100)}%</span>
              <span>{cycleDays} days</span>
            </footer>
          </article>

          <article>
            <h3>Water Balance</h3>
            <div className="farm3d-bar" aria-label={`Hydration ${Math.round(hydration * 100)} percent`}>
              <div style={{ width: `${Math.round(hydration * 100)}%` }} />
            </div>
            <footer>
              <span>{Math.round(hydration * 100)}%</span>
              <span>{formatNumber(avgPrecip, 1)} mm</span>
            </footer>
          </article>

          <article>
            <h3>Field Scale</h3>
            <div className="farm3d-bar" aria-label={`Area ${Math.round(areaHa * 10) / 10} hectares`}>
              <div style={{ width: `${clamp(areaHa / 6, 0, 1) * 100}%` }} />
            </div>
            <footer>
              <span>{formatNumber(areaHa, 1)} ha</span>
              <span>{formatNumber(avgTemp, 1)} °C</span>
            </footer>
          </article>
        </section>
      </div>
    </div>
  );
}
