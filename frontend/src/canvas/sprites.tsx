import React, { useMemo } from "react";
import { Group, Rect, Line, Path, Circle, Ellipse, Text, Image as KonvaImage } from "react-konva";
import { useKonvaImage } from "./sprite-utils";

/* ----------------------------- Basic components ---------------------------- */

export function NutrientBars({ x, y, N, P, K }: { x: number; y: number; N: number; P: number; K: number }) {
  return (
    <Group x={x} y={y}>
      <Text text={`N: ${N}`} x={0} y={0} fontSize={14} fill="green" />
      <Text text={`P: ${P}`} x={0} y={20} fontSize={14} fill="blue" />
      <Text text={`K: ${K}`} x={0} y={40} fontSize={14} fill="orange" />
    </Group>
  );
}

export const SoilBlock: React.FC<{ x: number; y: number; width: number; height: number; moisture: number }> = ({
  x,
  y,
  width,
  height,
  moisture,
}) => {
  const waterH = Math.max(0, Math.min(height, height * (moisture / 200)));
  return (
    <Group x={x} y={y}>
      <Rect width={width} height={height} fill="#8B5A2B" cornerRadius={6} />
      <Rect y={height - waterH} width={width} height={waterH} fill="#4aa3df" opacity={0.35} />
    </Group>
  );
};

export const Roots: React.FC<{ x: number; y: number; depth: number; width: number }> = ({ x, y, depth, width }) => (
  <Group x={x} y={y}>
    <Line points={[0, 0, width * 0.2, depth * 0.4, width * 0.1, depth]} stroke="#6b3f1d" strokeWidth={2} />
    <Line points={[width * 0.3, 0, width * 0.5, depth * 0.5, width * 0.35, depth]} stroke="#6b3f1d" strokeWidth={2} />
    <Line points={[width * 0.6, 0, width * 0.75, depth * 0.6, width * 0.65, depth]} stroke="#6b3f1d" strokeWidth={2} />
  </Group>
);

export const Leaf: React.FC<{ x: number; y: number; scale?: number; color?: string; rotation?: number }> = ({
  x,
  y,
  scale = 1,
  color = "#2e8b57",
  rotation = 0,
}) => (
  <Path
    x={x}
    y={y}
    rotation={rotation}
    scale={{ x: scale, y: scale }}
    data="M10 60 C 10 20, 60 10, 80 40 C 60 50, 40 70, 10 60 Z"
    fill={color}
    stroke="#1f6a43"
    strokeWidth={1}
  />
);

/* --------------------------- Family glyph fallbacks -------------------------- */

export const FruitSymbol: React.FC<{ x: number; y: number; size?: number; color?: string }> = ({
  x,
  y,
  size = 1,
  color = "#ff9800",
}) => (
  <Group x={x} y={y} scale={{ x: size, y: size }}>
    <Circle radius={10} fill={color} stroke="#795548" strokeWidth={1.5} />
    <Leaf x={0} y={-10} scale={0.3} rotation={-20} />
    <Leaf x={2} y={-10} scale={0.3} rotation={20} />
  </Group>
);

export const BulbSymbol: React.FC<{ x: number; y: number; size?: number; color?: string }> = ({
  x,
  y,
  size = 1,
  color = "#d7b49e",
}) => (
  <Group x={x} y={y} scale={{ x: size, y: size }}>
    <Path data="M0 0 C 10 -15, 20 -15, 25 0 C 25 20, -5 20, 0 0 Z" fill={color} stroke="#8d6e63" strokeWidth={1.2} />
    <Line points={[10, -15, 12, -25]} stroke="#6a8a2f" strokeWidth={2} />
  </Group>
);

export const RootSymbol: React.FC<{ x: number; y: number; size?: number; color?: string }> = ({
  x,
  y,
  size = 1,
  color = "#d8b48a",
}) => (
  <Group x={x} y={y} scale={{ x: size, y: size }}>
    <Path data="M0 0 C 12 10, 18 30, 6 40 C -6 30, -12 10, 0 0 Z" fill={color} stroke="#a67c52" strokeWidth={1.2} />
    <Line points={[0, 0, 0, -8]} stroke="#6a8a2f" strokeWidth={2} />
  </Group>
);

export const GrainSymbol: React.FC<{ x: number; y: number; size?: number; color?: string }> = ({
  x,
  y,
  size = 1,
  color = "#ffd54f",
}) => (
  <Group x={x} y={y} scale={{ x: size, y: size }}>
    <Line points={[0, 0, 0, -20]} stroke="#8bc34a" strokeWidth={2} />
    <Ellipse x={0} y={-25} radiusX={6} radiusY={10} fill={color} stroke="#fbc02d" />
    <Ellipse x={-3} y={-20} radiusX={6} radiusY={10} fill={color} stroke="#fbc02d" />
    <Ellipse x={3} y={-20} radiusX={6} radiusY={10} fill={color} stroke="#fbc02d" />
  </Group>
);

export const LegumeSymbol: React.FC<{ x: number; y: number; size?: number; color?: string }> = ({
  x,
  y,
  size = 1,
  color = "#9ccc65",
}) => (
  <Group x={x} y={y} scale={{ x: size, y: size }}>
    <Path data="M0 0 C 20 0, 25 10, 15 15 C 10 18, -5 15, 0 0 Z" fill={color} stroke="#558b2f" strokeWidth={1.2} />
    <Circle x={5} y={6} radius={2} fill="#7cb342" />
    <Circle x={10} y={6} radius={2} fill="#7cb342" />
  </Group>
);

export const VegLeafySymbol: React.FC<{ x: number; y: number; size?: number; color?: string }> = ({
  x,
  y,
  size = 1,
  color = "#66bb6a",
}) => (
  <Group x={x} y={y} scale={{ x: size, y: size }}>
    <Leaf x={0} y={0} scale={1} color={color} />
  </Group>
);

/* ------------------------------- Bitmap sprite ------------------------------ */

export const CropSprite: React.FC<{
  cropName: string;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  opacity?: number;
  anchor?: "top-left" | "center";
}> = ({ cropName, x = 0, y = 0, width, height, opacity = 1, anchor = "top-left" }) => {
  const lower = (cropName || "").toLowerCase();
  const src = useMemo(() => `/assets/crops/${lower}.png`, [lower]);
  const img = useKonvaImage(src, "anonymous");

  // family-based vector fallback while loading/missing
  const Fallback = useMemo(() => {
    if (["mango", "apple", "orange", "banana", "pineapple", "guava", "papaya", "lemon", "grapes"].includes(lower))
      return <FruitSymbol x={x} y={y} size={1} />;
    if (["onion", "garlic"].includes(lower)) return <BulbSymbol x={x} y={y} size={1} />;
    if (["cassava", "yams", "carrot", "beet"].includes(lower)) return <RootSymbol x={x} y={y} size={1} />;
    if (["maize", "rice", "sorghum"].includes(lower)) return <GrainSymbol x={x} y={y} size={1} />;
    if (["beans", "cowpea", "chickpea", "lentils", "fava beans", "mung bean"].includes(lower))
      return <LegumeSymbol x={x} y={y} size={1} />;
    return <VegLeafySymbol x={x} y={y} size={1} />;
  }, [lower, x, y]);

  if (!img) return <Group>{Fallback}</Group>;

  const w = width ?? img.width;
  const h = height ?? img.height;
  const offset = anchor === "center" ? { x: w / 2, y: h / 2 } : { x: 0, y: 0 };

  return (
    <KonvaImage
      image={img}
      x={x}
      y={y}
      width={w}
      height={h}
      opacity={opacity}
      offsetX={offset.x}
      offsetY={offset.y}
      listening={false}
    />
  );
};
