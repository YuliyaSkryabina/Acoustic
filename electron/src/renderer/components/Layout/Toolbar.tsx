/**
 * Панель инструментов.
 */
import React, { useRef } from "react";
import { useProjectStore } from "../../store/projectStore";
import { parseDxfFile } from "../Editor/DxfLoader";
import type { ActiveTool } from "../../types/acoustic";

const TOOLS: { id: ActiveTool; label: string; title: string }[] = [
  { id: "select",     label: "↖",  title: "Выбор объекта" },
  { id: "pan",        label: "✋",  title: "Перемещение вида" },
  { id: "add_source", label: "🔴", title: "Добавить источник шума" },
  { id: "add_point",  label: "🔵", title: "Добавить расчётную точку" },
  { id: "add_screen", label: "▬",  title: "Добавить экран-барьер" },
];

export function Toolbar() {
  const { activeTool, setActiveTool, setDxfLayers, newProject, runCalculation, isCalculating,
          sources, calcPoints } = useProjectStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDxfLoad = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const content = await file.text();
    const layers = await parseDxfFile(content);
    setDxfLayers(layers);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="toolbar">
      <span className="toolbar-title">Акустик</span>

      <div className="toolbar-separator" />

      {/* Инструменты */}
      {TOOLS.map(tool => (
        <button
          key={tool.id}
          title={tool.title}
          className={`toolbar-btn ${activeTool === tool.id ? "active" : ""}`}
          onClick={() => setActiveTool(tool.id)}
        >
          {tool.label}
        </button>
      ))}

      <div className="toolbar-separator" />

      {/* Загрузка DXF */}
      <button title="Загрузить DXF план" className="toolbar-btn"
              onClick={() => fileInputRef.current?.click()}>
        📂 DXF
      </button>
      <input ref={fileInputRef} type="file" accept=".dxf"
             style={{ display: "none" }} onChange={handleDxfLoad} />

      <div className="toolbar-separator" />

      {/* Расчёт */}
      <button
        title="Выполнить акустический расчёт"
        className="toolbar-btn btn-calculate"
        onClick={runCalculation}
        disabled={isCalculating || !sources.length || !calcPoints.length}
      >
        {isCalculating ? "⏳ Расчёт..." : "⚡ Рассчитать"}
      </button>

      <div className="toolbar-separator" />

      {/* Новый проект */}
      <button title="Новый проект" className="toolbar-btn"
              onClick={() => { if (confirm("Создать новый проект? Текущие данные будут потеряны.")) newProject(); }}>
        ✨ Новый
      </button>
    </div>
  );
}
