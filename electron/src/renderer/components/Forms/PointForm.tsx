/**
 * Форма добавления/редактирования расчётной точки.
 */
import React, { useState } from "react";
import type { CalcPoint, TerritoryType } from "../../types/acoustic";
import { TERRITORY_LABELS } from "../../types/acoustic";

interface PointFormProps {
  initialX?: number;
  initialY?: number;
  point?: CalcPoint;
  onSave: (pt: CalcPoint) => void;
  onCancel: () => void;
}

export function PointForm({ initialX = 0, initialY = 0, point, onSave, onCancel }: PointFormProps) {
  const [id] = useState(point?.id ?? `pt_${Date.now()}`);
  const [description, setDescription] = useState(point?.description ?? "");
  const [x, setX] = useState(point?.x ?? initialX);
  const [y, setY] = useState(point?.y ?? initialY);
  const [z, setZ] = useState(point?.z ?? 1.5);
  const [territoryType, setTerritoryType] = useState<TerritoryType>(
    point?.territory_type ?? "residential"
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({ id, description, x, y, z, territory_type: territoryType });
  };

  return (
    <form onSubmit={handleSubmit} className="acoustik-form">
      <h3>Расчётная точка</h3>

      <label>Описание
        <input value={description} onChange={e => setDescription(e.target.value)}
               placeholder="Фасад дома №5, детская площадка..." />
      </label>

      <div className="coord-row">
        <label>X, м<input type="number" step="0.1" value={x} onChange={e => setX(+e.target.value)} /></label>
        <label>Y, м<input type="number" step="0.1" value={y} onChange={e => setY(+e.target.value)} /></label>
        <label>Z, м<input type="number" step="0.1" value={z} onChange={e => setZ(+e.target.value)} /></label>
      </div>

      <label>Тип территории
        <select value={territoryType}
                onChange={e => setTerritoryType(e.target.value as TerritoryType)}>
          {Object.entries(TERRITORY_LABELS).map(([val, label]) => (
            <option key={val} value={val}>{label}</option>
          ))}
        </select>
      </label>

      <div className="form-actions">
        <button type="submit" className="btn-primary">Сохранить</button>
        <button type="button" className="btn-secondary" onClick={onCancel}>Отмена</button>
      </div>
    </form>
  );
}
