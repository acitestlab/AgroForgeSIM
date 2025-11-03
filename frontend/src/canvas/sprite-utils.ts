// src/canvas/sprite-utils.ts
import { useEffect, useState } from "react";

export const CROP_COLOR_TABLE: Record<string, string> = {
  maize: "#f59e0b",
  rice: "#22c55e",
  sorghum: "#8b5cf6",
  cassava: "#a3e635",
  yams: "#84cc16",
  carrot: "#fb923c",
  beet: "#ef4444",
  spinach: "#16a34a",
  cucumber: "#10b981",
  broccoli: "#22c55e",
  tomato: "#ef4444",
  onion: "#eab308",
  garlic: "#f59e0b",
  okra: "#65a30d",
  cabbage: "#14b8a6",
  pepper: "#dc2626",
  amaranth: "#a855f7",
  mango: "#f97316",
  apple: "#ef4444",
  orange: "#f59e0b",
  banana: "#fde047",
  pineapple: "#facc15",
  guava: "#22c55e",
  papaya: "#fb923c",
  lemon: "#fde047",
  grapes: "#7c3aed",
  beans: "#15803d",
  "fava beans": "#16a34a",
  cowpea: "#166534",
  chickpea: "#a16207",
  lentils: "#ca8a04",
  "mung bean": "#22c55e",
};

export const DEFAULT_CROP_COLOR = "#6b7280";

export const cropColor = (crop?: string): string => {
  if (!crop) return DEFAULT_CROP_COLOR;
  const key = crop.trim().toLowerCase();
  return CROP_COLOR_TABLE[key] ?? DEFAULT_CROP_COLOR;
};

export const growthColor = (maturity: number, stress = 1.0): string => {
  const m = Math.max(0, Math.min(1, maturity));
  const s = Math.max(0, Math.min(1, stress));
  if (s < 0.6) return "#8b4513"; // brown
  if (m < 0.3) return "#4caf50"; // green
  if (m < 0.7) return "#fbc02d"; // yellow
  return "#e53935"; // red
};

/** Load an HTMLImageElement for use in <KonvaImage image={...}/> */
export function useKonvaImage(src: string | null, crossOrigin?: string) {
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  useEffect(() => {
    if (!src) {
      setImage(null);
      return;
    }
    const img = new Image();
    if (crossOrigin) img.crossOrigin = crossOrigin;
    img.src = src;
    const onload = () => setImage(img);
    img.onload = onload;
    return () => {
      img.onload = null;
    };
  }, [src, crossOrigin]);

  return image;
}
