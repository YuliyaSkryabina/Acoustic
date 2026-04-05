/**
 * Форма добавления/редактирования источника шума.
 */
import React, { useState } from "react";
import type { NoiseSource, SourceType, TerritoryType } from "../../types/acoustic";
import { OCTAVE_FREQS } from "../../types/acoustic";

interface SourceFormProps {
  initialX?: number;
  initialY?: number;
  source?: NoiseSource;
  onSave: (src: NoiseSource) => void;
  onCancel: () => void;
}

const defaultLw = (): [number,number,number,number,number,number,number,number] =>
  [75, 75, 75, 75, 75, 75, 75, 75];

export function SourceForm({ initialX = 0, initialY = 0, source, onSave, onCancel }: SourceFormProps) {
  const [id] = useState(source?.id ?? `src_${Date.now()}`);
  const [description, setDescription] = useState(source?.description ?? "");
  const [sourceType, setSourceType] = useState<SourceType>(source?.source_type ?? "point");
  const [isPermanent, setIsPermanent] = useState(source?.is_permanent ?? true);
  const [lw, setLw] = useState<number[]>(source?.lw_octave ?? defaultLw());
  const [x, setX] = useState(source?.x ?? initialX);
  const [y, setY] = useState(source?.y ?? initialY);
  const [z, setZ] = useState(source?.z ?? 1.0);
  const [durationDay, setDurationDay] = useState(source?.duration_day ?? 16);
  const [durationNight, setDurationNight] = useState(source?.duration_night ?? 8);
  const [directionality, setDirectionality] = useState(source?.directionality ?? 0);

  const handleLwChange = (idx: number, val: string) => {
    const newLw = [...lw];
    newLw[idx] = parseFloat(val) || 0;
    setLw(newLw);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      id,
      description,
      source_type: sourceType,
      is_permanent: isPermanent,
      lw_octave: lw as [number,number,number,number,number,number,number,number],
      x,
      y,
      z,
      duration_day: durationDay,
      duration_night: durationNight,
      directionality,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="acoustik-form">
      <h3>Источник шума</h3>

      <label>Описание
        <input value={description} onChange={e => setDescription(e.target.value)}
               placeholder="Насос, компрессор, вентилятор..." />
      </label>

      <label>Тип ИШ
        <select value={sourceType} onChange={e => setSourceType(e.target.value as SourceType)}>
          <option value="point">Точечный</option>
          <option value="line">Линейный (дорога)</option>
        </select>
      </label>

      <div className="coord-row">
        <label>X, м<input type="number" step="0.1" value={x} onChange={e => setX(+e.target.value)} /></label>
        <label>Y, м<input type="number" step="0.1" value={y} onChange={e => setY(+e.target.value)} /></label>
        <label>Z, м<input type="number" step="0.1" value={z} onChange={e => setZ(+e.target.value)} /></label>
      </div>

      <fieldset>
        <legend>Lw по октавным полосам [дБ]</legend>
        <div className="octave-grid">
          {OCTAVE_FREQS.map((freq, idx) => (
            <label key={freq}>{freq} Гц
              <input type="number" step="0.5" min="0" max="160"
                     value={lw[idx]}
                     onChange={e => handleLwChange(idx, e.target.value)} />
            </label>
          ))}
        </div>
      </fieldset>

      <label>
        <input type="checkbox" checked={isPermanent}
               onChange={e => setIsPermanent(e.target.checked)} />
        &nbsp;Постоянный режим работы
      </label>

      {!isPermanent && (
        <div className="duration-row">
          <label>Работа днём, ч
            <input type="number" min="0" max="16" step="0.5"
                   value={durationDay} onChange={e => setDurationDay(+e.target.value)} />
          </label>
          <label>Работа ночью, ч
            <input type="number" min="0" max="8" step="0.5"
                   value={durationNight} onChange={e => setDurationNight(+e.target.value)} />
          </label>
        </div>
      )}

      <label>Направленность ΔLф, дБ
        <input type="number" step="0.5" value={directionality}
               onChange={e => setDirectionality(+e.target.value)} />
      </label>

      <div className="form-actions">
        <button type="submit" className="btn-primary">Сохранить</button>
        <button type="button" className="btn-secondary" onClick={onCancel}>Отмена</button>
      </div>
    </form>
  );
}
