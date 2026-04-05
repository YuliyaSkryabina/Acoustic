/**
 * Строка статуса — количество объектов, активный инструмент, ошибки.
 */
import React from "react";
import { useProjectStore } from "../../store/projectStore";

export function StatusBar() {
  const { sources, calcPoints, screens, results, error, activeTool, zoom } = useProjectStore();

  const exceededCount = results?.results.filter(r => r.period === "day" && r.exceeded).length ?? 0;
  const totalDayPoints = results?.results.filter(r => r.period === "day").length ?? 0;

  return (
    <div className="status-bar">
      <span>ИШ: {sources.length}</span>
      <span>РТ: {calcPoints.length}</span>
      <span>Экранов: {screens.length}</span>

      {results && (
        <>
          <span className="separator">|</span>
          <span style={{ color: exceededCount > 0 ? "#C62828" : "#2E7D32" }}>
            Превышений: {exceededCount}/{totalDayPoints}
          </span>
        </>
      )}

      <span className="separator">|</span>
      <span>Масштаб: {Math.round(zoom * 100)}%</span>

      <span className="separator">|</span>
      <span className="active-tool">
        {{
          select: "Выбор",
          pan: "Перемещение",
          add_source: "Добавить ИШ — кликните на план",
          add_point: "Добавить РТ — кликните на план",
          add_screen: "Добавить экран — кликните два раза",
        }[activeTool]}
      </span>

      {error && (
        <span className="error-msg" style={{ color: "#C62828", marginLeft: "auto" }}>
          ⚠ {error}
        </span>
      )}
    </div>
  );
}
