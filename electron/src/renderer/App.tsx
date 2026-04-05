/**
 * Корневой компонент приложения.
 * Макет: тулбар → главная область (редактор | боковая панель) → статусбар.
 */
import React, { useState } from "react";
import { Toolbar } from "./components/Layout/Toolbar";
import { StatusBar } from "./components/Layout/StatusBar";
import { CanvasEditor } from "./components/Editor/CanvasEditor";
import { ResultsTable } from "./components/Results/ResultsTable";
import { useProjectStore } from "./store/projectStore";
import "./styles.css";

type SidePanel = "objects" | "results";

export function App() {
  const { sources, calcPoints, screens, results,
          removeSource, removeCalcPoint, removeScreen } = useProjectStore();
  const [sidePanel, setSidePanel] = useState<SidePanel>("objects");

  return (
    <div className="app-container">
      <Toolbar />

      <div className="main-area">
        {/* Редактор */}
        <div className="canvas-area">
          <CanvasEditor />
        </div>

        {/* Боковая панель */}
        <div className="side-panel">
          <div className="side-tabs">
            <button
              className={sidePanel === "objects" ? "active" : ""}
              onClick={() => setSidePanel("objects")}
            >
              Объекты
            </button>
            <button
              className={`${sidePanel === "results" ? "active" : ""} ${results ? "has-results" : ""}`}
              onClick={() => setSidePanel("results")}
            >
              Результаты {results && `(${results.results.length / 2})`}
            </button>
          </div>

          {sidePanel === "objects" && (
            <div className="objects-panel">
              <section>
                <h4>Источники шума ({sources.length})</h4>
                {sources.map(src => (
                  <div key={src.id} className="object-item">
                    <span className="obj-icon" style={{ color: "#E53935" }}>●</span>
                    <span className="obj-label">{src.description || src.id}</span>
                    <span className="obj-coords">({src.x.toFixed(0)}, {src.y.toFixed(0)})</span>
                    <button className="obj-remove" onClick={() => removeSource(src.id)}>✕</button>
                  </div>
                ))}
                {!sources.length && (
                  <p className="hint">Нет источников. Используйте инструмент "Добавить ИШ".</p>
                )}
              </section>

              <section>
                <h4>Расчётные точки ({calcPoints.length})</h4>
                {calcPoints.map(pt => (
                  <div key={pt.id} className="object-item">
                    <span className="obj-icon" style={{ color: "#1565C0" }}>●</span>
                    <span className="obj-label">{pt.description || pt.id}</span>
                    <span className="obj-coords">({pt.x.toFixed(0)}, {pt.y.toFixed(0)})</span>
                    <button className="obj-remove" onClick={() => removeCalcPoint(pt.id)}>✕</button>
                  </div>
                ))}
                {!calcPoints.length && (
                  <p className="hint">Нет расчётных точек.</p>
                )}
              </section>

              <section>
                <h4>Экраны ({screens.length})</h4>
                {screens.map(scr => (
                  <div key={scr.id} className="object-item">
                    <span className="obj-icon" style={{ color: "#795548" }}>▬</span>
                    <span className="obj-label">{scr.id}</span>
                    <span className="obj-coords">h={scr.height}м</span>
                    <button className="obj-remove" onClick={() => removeScreen(scr.id)}>✕</button>
                  </div>
                ))}
              </section>
            </div>
          )}

          {sidePanel === "results" && (
            <div className="results-panel">
              {results ? (
                <>
                  <p className="results-meta">
                    Источников: {results.metadata.sources_count as number} •
                    Точек: {results.metadata.points_count as number}
                  </p>
                  <ResultsTable results={results.results} />
                </>
              ) : (
                <p className="hint">
                  Добавьте источники и расчётные точки, затем нажмите «Рассчитать».
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      <StatusBar />
    </div>
  );
}
