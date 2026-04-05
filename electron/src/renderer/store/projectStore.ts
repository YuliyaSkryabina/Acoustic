/**
 * Zustand store — главное состояние проекта.
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  NoiseSource,
  CalcPoint,
  Screen,
  CalcResponse,
  DxfLayer,
  ActiveTool,
} from "../types/acoustic";

interface ProjectState {
  projectId: string;
  projectName: string;
  sources: NoiseSource[];
  calcPoints: CalcPoint[];
  screens: Screen[];
  results: CalcResponse | null;
  dxfLayers: DxfLayer[];
  isDirty: boolean;
  isCalculating: boolean;
  error: string | null;

  // UI
  activeTool: ActiveTool;
  zoom: number;
  offsetX: number;
  offsetY: number;

  // Выбранный объект
  selectedId: string | null;
  selectedType: "source" | "point" | "screen" | null;

  // Действия
  addSource: (src: NoiseSource) => void;
  updateSource: (id: string, patch: Partial<NoiseSource>) => void;
  removeSource: (id: string) => void;
  addCalcPoint: (pt: CalcPoint) => void;
  updateCalcPoint: (id: string, patch: Partial<CalcPoint>) => void;
  removeCalcPoint: (id: string) => void;
  addScreen: (screen: Screen) => void;
  removeScreen: (id: string) => void;
  setDxfLayers: (layers: DxfLayer[]) => void;
  setResults: (res: CalcResponse) => void;
  setActiveTool: (tool: ActiveTool) => void;
  setZoom: (zoom: number) => void;
  setOffset: (x: number, y: number) => void;
  setSelected: (id: string | null, type: "source" | "point" | "screen" | null) => void;
  runCalculation: () => Promise<void>;
  clearResults: () => void;
  newProject: () => void;
}

const defaultProjectId = () => `project_${Date.now()}`;

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      projectId: defaultProjectId(),
      projectName: "Новый проект",
      sources: [],
      calcPoints: [],
      screens: [],
      results: null,
      dxfLayers: [],
      isDirty: false,
      isCalculating: false,
      error: null,
      activeTool: "select",
      zoom: 1,
      offsetX: 0,
      offsetY: 0,
      selectedId: null,
      selectedType: null,

      addSource: (src) =>
        set((state) => ({ sources: [...state.sources, src], isDirty: true })),

      updateSource: (id, patch) =>
        set((state) => ({
          sources: state.sources.map((s) =>
            s.id === id ? { ...s, ...patch } : s
          ),
          isDirty: true,
        })),

      removeSource: (id) =>
        set((state) => ({
          sources: state.sources.filter((s) => s.id !== id),
          isDirty: true,
        })),

      addCalcPoint: (pt) =>
        set((state) => ({ calcPoints: [...state.calcPoints, pt], isDirty: true })),

      updateCalcPoint: (id, patch) =>
        set((state) => ({
          calcPoints: state.calcPoints.map((p) =>
            p.id === id ? { ...p, ...patch } : p
          ),
          isDirty: true,
        })),

      removeCalcPoint: (id) =>
        set((state) => ({
          calcPoints: state.calcPoints.filter((p) => p.id !== id),
          isDirty: true,
        })),

      addScreen: (screen) =>
        set((state) => ({ screens: [...state.screens, screen], isDirty: true })),

      removeScreen: (id) =>
        set((state) => ({
          screens: state.screens.filter((s) => s.id !== id),
          isDirty: true,
        })),

      setDxfLayers: (layers) => set({ dxfLayers: layers }),

      setResults: (res) => set({ results: res, isDirty: false }),

      setActiveTool: (tool) => set({ activeTool: tool }),

      setZoom: (zoom) => set({ zoom: Math.max(0.05, Math.min(20, zoom)) }),

      setOffset: (x, y) => set({ offsetX: x, offsetY: y }),

      setSelected: (id, type) => set({ selectedId: id, selectedType: type }),

      runCalculation: async () => {
        const { sources, calcPoints, screens } = get();
        if (!sources.length || !calcPoints.length) {
          set({ error: "Необходимо добавить хотя бы один источник и одну расчётную точку" });
          return;
        }
        set({ isCalculating: true, error: null });
        try {
          const request = {
            sources,
            points: calcPoints,
            screens,
            temperature: 20,
            humidity: 70,
            ground_type: 0,
          };
          const results = await (window as any).acoustik.calculate(request) as CalcResponse;
          set({ results, isDirty: false });
        } catch (err) {
          set({ error: String(err) });
        } finally {
          set({ isCalculating: false });
        }
      },

      clearResults: () => set({ results: null }),

      newProject: () =>
        set({
          projectId: defaultProjectId(),
          projectName: "Новый проект",
          sources: [],
          calcPoints: [],
          screens: [],
          results: null,
          dxfLayers: [],
          isDirty: false,
          error: null,
        }),
    }),
    {
      name: "acoustik-project",
      partialize: (state) => ({
        projectId: state.projectId,
        projectName: state.projectName,
        sources: state.sources,
        calcPoints: state.calcPoints,
        screens: state.screens,
      }),
    }
  )
);
