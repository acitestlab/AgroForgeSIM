// src/App.tsx
import React, { useEffect, useMemo, useState, useId } from "react";
import { useStore } from "./store";
import FarmCanvas from "./canvas/FarmCanvas";
import Inspector from "./panels/Inspector";
import Timeline from "./panels/Timeline";
import HarvestPlan from "./components/HarvestPlan";
import LandPicker from "./panels/LandPicker";
import Button from "./components/Button";
import ApiHealth from "./components/ApiHealth";

type CropMap = Record<string, string[]>;

const STORAGE_KEY = "agroforge:lastCrop";
const FALLBACK_CROPS: CropMap = {
  Cereals: ["maize", "rice", "sorghum"],
  "Root and Tuber Crops": ["cassava", "yams"],
  Vegetables: [
    "spinach",
    "cucumber",
    "broccoli",
    "tomato",
    "onion",
    "okra",
    "cabbage",
    "pepper",
    "amaranth",
    "garlic",
    "carrot",
  ],
  Fruits: [
    "mango",
    "apple",
    "orange",
    "banana",
    "pineapple",
    "guava",
    "papaya",
    "lemon",
    "grapes",
  ],
  Legumes: ["beans", "cowpea", "chickpea", "lentils", "fava beans", "mung bean"],
};

function CropToolbar() {
  const cropsFromStore = useStore((s) => s.crops);
  const loading = useStore((s) => s.loading?.crops);
  const error = useStore((s) => s.error);
  const setCropInStore = useStore((s) => s.setCrop);
  const runSim = useStore((s) => s.runSim);

  const cropCategories: CropMap =
    cropsFromStore && Object.keys(cropsFromStore).length > 0
      ? (cropsFromStore as CropMap)
      : FALLBACK_CROPS;

  const [crop, setCrop] = useState<string>(
    () => localStorage.getItem(STORAGE_KEY) || "maize"
  );

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, crop);
    setCropInStore?.(crop);
  }, [crop, setCropInStore]);

  const allCrops = useMemo(
    () => Object.values(cropCategories).flat(),
    [cropCategories]
  );
  const canRun = allCrops.includes(crop) && !loading;

  // unique id so label ↔ select always match
  const cropSelectId = useId();

  return (
    <div
      style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}
    >
      {loading ? (
        // While loading there is no <select>, so don't render a <label htmlFor>.
        <>
          <span style={{ fontWeight: 600 }}>Crop</span>
          <span className="loader" aria-label="Loading crops" />
        </>
      ) : (
        <>
          <label htmlFor={cropSelectId} style={{ fontWeight: 600 }}>
            Crop
          </label>
          <select
            id={cropSelectId}
            className="btn secondary"
            value={crop}
            onChange={(e) => setCrop(e.target.value)}
            style={{ padding: "6px 10px", minWidth: 120 }}
            aria-label="Select crop"
          >
            {Object.entries(cropCategories).map(([group, list]) => (
              <optgroup label={group} key={group}>
                {list.map((c) => (
                  <option value={c} key={c}>
                    {c.charAt(0).toUpperCase() + c.slice(1)}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </>
      )}

      <Button
        onClick={() => runSim?.()}
        disabled={!canRun}
        title="Run simulation for the selected node"
      >
        Run Simulation
      </Button>

      {error && (
        <small
          role="status"
          aria-live="polite"
          style={{ marginLeft: 8, opacity: 0.85 }}
        >
          {error.includes("crop") ? error : "Note: using fallback crop list."}
        </small>
      )}
    </div>
  );
}

export default function App() {
  const init = useStore((s) => s.init);
  const [tab, setTab] = useState<"canvas" | "land">("canvas");

  useEffect(() => {
    init?.();
  }, [init]);

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 340px",
        gap: 12,
        height: "100vh",
        padding: 12,
      }}
    >
      {/* Left column */}
      <div
        className="panel"
        style={{ display: "grid", gridTemplateRows: "auto auto auto 1fr 240px", gap: 12 }}
      >
        {/* Tabs */}
        <div style={{ display: "flex", gap: 8 }}>
          <Button
            variant={tab === "canvas" ? "primary" : "secondary"}
            onClick={() => setTab("canvas")}
          >
            Canvas
          </Button>
          <Button
            variant={tab === "land" ? "primary" : "secondary"}
            onClick={() => setTab("land")}
          >
            Land
          </Button>
        </div>

        {/* API status */}
        <div aria-live="polite">
          <ApiHealth />
        </div>

        {/* Crop Toolbar */}
        <CropToolbar />

        {/* Main area per tab */}
        {tab === "canvas" ? <FarmCanvas /> : <LandPicker />}

        {/* Timeline */}
        <Timeline />
      </div>

      {/* Right column */}
      <div className="panel" style={{ display: "grid", gridTemplateRows: "1fr 280px", gap: 12 }}>
        <Inspector />
        <HarvestPlan />
      </div>
    </div>
  );
}
