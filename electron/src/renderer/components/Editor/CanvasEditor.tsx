/**
 * Главный графический редактор на Konva.js.
 * 5 слоёв: DXF-фон, экраны, источники, расчётные точки, изолинии.
 */
import React, { useRef, useState, useCallback } from "react";
import { Stage, Layer, Circle, Line, Text, Group } from "react-konva";
import Konva from "konva";
import { useProjectStore } from "../../store/projectStore";
import type { NoiseSource, CalcPoint, Screen } from "../../types/acoustic";
import { SourceForm } from "../Forms/SourceForm";
import { PointForm } from "../Forms/PointForm";

const ISOLINE_COLORS: Record<number, string> = {
  30: "#2196F3",
  35: "#1976D2",
  40: "#4CAF50",
  45: "#8BC34A",
  50: "#CDDC39",
  55: "#FFC107",
  60: "#FF7043",
  65: "#F44336",
  70: "#B71C1C",
  75: "#880E4F",
  80: "#4A148C",
};

function isoColor(level: number): string {
  const keys = Object.keys(ISOLINE_COLORS).map(Number).sort((a, b) => a - b);
  const found = keys.reverse().find(k => level >= k);
  return found ? ISOLINE_COLORS[found] : "#9E9E9E";
}

interface PendingForm {
  type: "source" | "point";
  x: number;
  y: number;
}

export function CanvasEditor() {
  const {
    sources, calcPoints, screens, results, dxfLayers,
    activeTool, zoom, offsetX, offsetY,
    addSource, addCalcPoint, addScreen,
    setZoom, setOffset, setSelected,
    runCalculation, isCalculating,
  } = useProjectStore();

  const stageRef = useRef<Konva.Stage>(null);
  const [pendingForm, setPendingForm] = useState<PendingForm | null>(null);
  const [screenStart, setScreenStart] = useState<{x: number; y: number} | null>(null);

  const stageWidth  = window.innerWidth  - 320;  // 320 = ширина боковой панели
  const stageHeight = window.innerHeight - 100;   // 100 = тулбар + строка статуса

  // Преобразование экранных координат в мировые
  const screenToWorld = (sx: number, sy: number) => ({
    x: (sx - offsetX) / zoom,
    y: -(sy - offsetY) / zoom,   // инверсия Y: canvas Y↓, мир Y↑
  });

  const handleStageClick = useCallback((e: Konva.KonvaEventObject<MouseEvent>) => {
    const stage = stageRef.current;
    if (!stage) return;
    const pos = stage.getPointerPosition();
    if (!pos) return;
    const world = screenToWorld(pos.x, pos.y);

    if (activeTool === "add_source") {
      setPendingForm({ type: "source", x: world.x, y: world.y });
    } else if (activeTool === "add_point") {
      setPendingForm({ type: "point", x: world.x, y: world.y });
    } else if (activeTool === "add_screen") {
      if (!screenStart) {
        setScreenStart({ x: world.x, y: world.y });
      } else {
        addScreen({
          id: `scr_${Date.now()}`,
          x1: screenStart.x, y1: screenStart.y,
          x2: world.x, y2: world.y,
          height: 3.0,
          absorption: 0,
        });
        setScreenStart(null);
      }
    }
  }, [activeTool, screenStart, offsetX, offsetY, zoom]);

  const handleWheel = (e: Konva.KonvaEventObject<WheelEvent>) => {
    e.evt.preventDefault();
    const stage = stageRef.current;
    if (!stage) return;
    const oldZoom = zoom;
    const pointer = stage.getPointerPosition()!;
    const zoomFactor = e.evt.deltaY < 0 ? 1.1 : 0.9;
    const newZoom = Math.max(0.05, Math.min(20, oldZoom * zoomFactor));
    // Зум к указателю
    const mousePointTo = {
      x: (pointer.x - offsetX) / oldZoom,
      y: (pointer.y - offsetY) / oldZoom,
    };
    setZoom(newZoom);
    setOffset(
      pointer.x - mousePointTo.x * newZoom,
      pointer.y - mousePointTo.y * newZoom,
    );
  };

  // Изолинии из результатов
  const isolines = results?.isolines ?? [];

  return (
    <div style={{ position: "relative" }}>
      <Stage
        ref={stageRef}
        width={stageWidth}
        height={stageHeight}
        onClick={handleStageClick}
        onWheel={handleWheel}
        draggable={activeTool === "pan"}
        onDragEnd={(e) => {
          setOffset(e.target.x(), e.target.y());
        }}
        x={offsetX}
        y={offsetY}
        scaleX={zoom}
        scaleY={zoom}
        style={{ background: "#f5f5f5", cursor: activeTool === "pan" ? "grab" : "crosshair" }}
      >
        {/* Слой 1: Изолинии (за остальными объектами) */}
        <Layer>
          {isolines.map((iso, i) => {
            const pts = iso.coordinates.flatMap(([cx, cy]) => [cx, -cy]);
            return (
              <Line key={i} points={pts}
                    stroke={isoColor(iso.level_dba)}
                    strokeWidth={1.5 / zoom}
                    opacity={0.7} />
            );
          })}
        </Layer>

        {/* Слой 2: DXF-фон (здания, дороги) */}
        <Layer opacity={0.6}>
          {dxfLayers.flatMap((layer, li) =>
            layer.visible ? (layer.shapes as any[]).map((shape: any, si: number) => (
              <Line key={`${li}-${si}`}
                    points={shape.points ?? []}
                    stroke={shape.stroke ?? "#9E9E9E"}
                    strokeWidth={(shape.strokeWidth ?? 1) / zoom} />
            )) : []
          )}
        </Layer>

        {/* Слой 3: Экраны */}
        <Layer>
          {screens.map(scr => (
            <Group key={scr.id}>
              <Line points={[scr.x1, -scr.y1, scr.x2, -scr.y2]}
                    stroke="#795548" strokeWidth={3 / zoom}
                    onClick={() => setSelected(scr.id, "screen")} />
              <Text x={(scr.x1 + scr.x2) / 2} y={-(scr.y1 + scr.y2) / 2 - 12 / zoom}
                    text={`${scr.height}м`}
                    fontSize={11 / zoom} fill="#795548" />
            </Group>
          ))}
        </Layer>

        {/* Слой 4: Источники шума */}
        <Layer>
          {sources.map(src => (
            <Group key={src.id}
                   onClick={() => setSelected(src.id, "source")}
                   draggable>
              <Circle x={src.x} y={-src.y}
                      radius={8 / zoom}
                      fill="#E53935" stroke="white" strokeWidth={2 / zoom} />
              <Text x={src.x + 10 / zoom} y={-src.y - 8 / zoom}
                    text={src.description || src.id}
                    fontSize={10 / zoom} fill="#B71C1C" />
            </Group>
          ))}
        </Layer>

        {/* Слой 5: Расчётные точки */}
        <Layer>
          {calcPoints.map(pt => {
            const dayResult = results?.results.find(
              r => r.point_id === pt.id && r.period === "day"
            );
            const exceeded = dayResult?.exceeded;
            const level = dayResult?.l_a_eq;
            return (
              <Group key={pt.id}
                     onClick={() => setSelected(pt.id, "point")}
                     draggable>
                <Circle x={pt.x} y={-pt.y}
                        radius={6 / zoom}
                        fill={exceeded === undefined ? "#1565C0" : exceeded ? "#C62828" : "#2E7D32"}
                        stroke="white" strokeWidth={2 / zoom} />
                <Text x={pt.x + 8 / zoom} y={-pt.y - 8 / zoom}
                      text={level !== undefined ? `${pt.id}: ${level.toFixed(0)}дБА` : pt.id}
                      fontSize={10 / zoom}
                      fill={exceeded ? "#C62828" : "#1565C0"} />
              </Group>
            );
          })}
        </Layer>
      </Stage>

      {/* Модальные формы */}
      {pendingForm && (
        <div className="modal-overlay" onClick={() => setPendingForm(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            {pendingForm.type === "source" ? (
              <SourceForm
                initialX={pendingForm.x}
                initialY={pendingForm.y}
                onSave={src => { addSource(src); setPendingForm(null); }}
                onCancel={() => setPendingForm(null)}
              />
            ) : (
              <PointForm
                initialX={pendingForm.x}
                initialY={pendingForm.y}
                onSave={pt => { addCalcPoint(pt); setPendingForm(null); }}
                onCancel={() => setPendingForm(null)}
              />
            )}
          </div>
        </div>
      )}

      {/* Кнопка расчёта */}
      <button
        className="calc-button"
        onClick={runCalculation}
        disabled={isCalculating || !sources.length || !calcPoints.length}
        style={{
          position: "absolute", bottom: 20, right: 20,
          background: "#1565C0", color: "white",
          border: "none", borderRadius: 4, padding: "10px 20px",
          fontSize: 14, cursor: "pointer", fontWeight: "bold",
        }}
      >
        {isCalculating ? "Расчёт..." : "Рассчитать"}
      </button>

      {/* Подсказка при рисовании экрана */}
      {activeTool === "add_screen" && screenStart && (
        <div style={{
          position: "absolute", top: 10, left: "50%", transform: "translateX(-50%)",
          background: "#795548", color: "white", padding: "4px 12px", borderRadius: 4,
        }}>
          Кликните для второй точки экрана
        </div>
      )}
    </div>
  );
}
