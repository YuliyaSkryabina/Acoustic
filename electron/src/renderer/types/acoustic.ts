/**
 * TypeScript типы — зеркало Pydantic моделей Python.
 */

export type SourceType = "point" | "line";

export type TerritoryType =
  | "residential"
  | "school"
  | "hospital"
  | "recreation"
  | "industrial"
  | "office";

export interface NoiseSource {
  id: string;
  source_type: SourceType;
  description: string;
  is_permanent: boolean;
  lw_octave: [number, number, number, number, number, number, number, number];
  x: number;
  y: number;
  z: number;
  x2?: number;
  y2?: number;
  duration_day: number;
  duration_night: number;
  directionality: number;
}

export interface CalcPoint {
  id: string;
  x: number;
  y: number;
  z: number;
  territory_type: TerritoryType;
  description: string;
}

export interface Screen {
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  height: number;
  absorption: number;
}

export interface CalcRequest {
  sources: NoiseSource[];
  points: CalcPoint[];
  screens: Screen[];
  temperature: number;
  humidity: number;
  ground_type: number;
}

export interface PointResult {
  point_id: string;
  period: "day" | "night";
  l_octave: [number, number, number, number, number, number, number, number];
  l_a_eq: number;
  l_a_max: number;
  pdu_eq: number;
  pdu_max: number;
  exceeded: boolean;
  exceedance_eq: number;
}

export interface IsolineFeature {
  level_dba: number;
  coordinates: [number, number][];
}

export interface CalcResponse {
  results: PointResult[];
  isolines: IsolineFeature[];
  metadata: Record<string, unknown>;
}

export type ActiveTool = "select" | "pan" | "add_source" | "add_point" | "add_screen";

export interface DxfLayer {
  name: string;
  visible: boolean;
  shapes: unknown[];  // Konva shape configs
}

export const TERRITORY_LABELS: Record<TerritoryType, string> = {
  residential: "Жилая застройка",
  school: "Школа / детский сад",
  hospital: "Больница",
  recreation: "Рекреационная зона",
  industrial: "Промышленная территория",
  office: "Административно-офисная",
};

export const OCTAVE_FREQS = [63, 125, 250, 500, 1000, 2000, 4000, 8000] as const;
