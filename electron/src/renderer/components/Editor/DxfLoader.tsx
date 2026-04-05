/**
 * Загрузчик DXF файлов.
 * Парсит DXF через dxf-parser и конвертирует в Konva-совместимые конфиги.
 * ВАЖНО: инверсия Y-оси (DXF Y↑, canvas Y↓).
 */
import type { DxfLayer } from "../../types/acoustic";

interface DxfEntity {
  type: string;
  layer?: string;
  vertices?: Array<{ x: number; y: number }>;
  center?: { x: number; y: number };
  radius?: number;
  startPoint?: { x: number; y: number };
  endPoint?: { x: number; y: number };
  closed?: boolean;
}

interface DxfData {
  entities: DxfEntity[];
  tables?: { layer?: { layers: Record<string, { color?: number }> } };
}

function dxfColorToHex(colorNum?: number): string {
  // ACI цвета AutoCAD (упрощённая таблица)
  const ACI: Record<number, string> = {
    0: "#000000",
    1: "#FF0000",
    2: "#FFFF00",
    3: "#00FF00",
    4: "#00FFFF",
    5: "#0000FF",
    6: "#FF00FF",
    7: "#FFFFFF",
    8: "#808080",
    9: "#C0C0C0",
  };
  if (!colorNum) return "#9E9E9E";
  return ACI[colorNum] ?? "#9E9E9E";
}

export async function parseDxfFile(content: string): Promise<DxfLayer[]> {
  // Динамический импорт для уменьшения bundle size
  const { default: DxfParser } = await import("dxf-parser");
  const parser = new DxfParser();

  let dxf: DxfData;
  try {
    dxf = parser.parseSync(content) as DxfData;
  } catch (err) {
    console.error("Ошибка парсинга DXF:", err);
    return [];
  }

  const layerMap = new Map<string, { shapes: object[]; color: string }>();

  const getOrCreateLayer = (name: string) => {
    if (!layerMap.has(name)) {
      const layerDef = dxf.tables?.layer?.layers?.[name];
      layerMap.set(name, {
        shapes: [],
        color: dxfColorToHex(layerDef?.color),
      });
    }
    return layerMap.get(name)!;
  };

  for (const entity of dxf.entities ?? []) {
    const layerName = entity.layer ?? "0";
    const layer = getOrCreateLayer(layerName);

    switch (entity.type) {
      case "LINE": {
        if (!entity.vertices || entity.vertices.length < 2) break;
        const [v0, v1] = entity.vertices;
        layer.shapes.push({
          type: "line",
          points: [v0.x, -v0.y, v1.x, -v1.y],   // инверсия Y
          stroke: layer.color,
          strokeWidth: 1,
        });
        break;
      }
      case "LWPOLYLINE":
      case "POLYLINE": {
        if (!entity.vertices?.length) break;
        const pts = entity.vertices.flatMap(v => [v.x, -v.y]);
        layer.shapes.push({
          type: "line",
          points: pts,
          stroke: layer.color,
          strokeWidth: 1,
          closed: entity.closed ?? false,
        });
        break;
      }
      case "CIRCLE": {
        if (!entity.center) break;
        layer.shapes.push({
          type: "circle",
          x: entity.center.x,
          y: -entity.center.y,
          radius: entity.radius ?? 1,
          stroke: layer.color,
          strokeWidth: 1,
          fill: "transparent",
        });
        break;
      }
      case "ARC": {
        // Упрощение: дуга → отрезок (TODO: параметрическая дуга)
        break;
      }
    }
  }

  return Array.from(layerMap.entries()).map(([name, data]) => ({
    name,
    visible: true,
    shapes: data.shapes,
  }));
}
