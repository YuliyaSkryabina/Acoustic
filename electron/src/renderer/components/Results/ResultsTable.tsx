/**
 * Таблица результатов расчёта с цветовым кодированием превышений ПДУ.
 */
import React from "react";
import type { PointResult } from "../../types/acoustic";
import { OCTAVE_FREQS } from "../../types/acoustic";

interface ResultsTableProps {
  results: PointResult[];
}

function getRowColor(exceedance: number): string {
  if (exceedance < -5)  return "#e8f5e9";  // зелёный
  if (exceedance < 0)   return "#f1f8e9";  // светло-зелёный
  if (exceedance < 5)   return "#fff8e1";  // жёлтый
  if (exceedance < 10)  return "#fbe9e7";  // оранжевый
  return "#ffebee";                         // красный
}

function getExceedanceColor(exceedance: number): string {
  if (exceedance <= 0)  return "#2e7d32";  // зелёный
  if (exceedance < 5)   return "#f57f17";  // жёлто-оранжевый
  return "#c62828";                         // красный
}

export function ResultsTable({ results }: ResultsTableProps) {
  if (!results.length) return null;

  return (
    <div className="results-table-wrapper">
      <table className="results-table">
        <thead>
          <tr>
            <th>РТ</th>
            <th>Период</th>
            {OCTAVE_FREQS.map(f => <th key={f}>{f}</th>)}
            <th>Lэкв, дБА</th>
            <th>ПДУ, дБА</th>
            <th>Δ, дБА</th>
            <th>Оценка</th>
          </tr>
        </thead>
        <tbody>
          {results.map(r => (
            <tr key={`${r.point_id}-${r.period}`}
                style={{ backgroundColor: getRowColor(r.exceedance_eq) }}>
              <td>{r.point_id}</td>
              <td>{r.period === "day" ? "День" : "Ночь"}</td>
              {r.l_octave.map((l, i) => (
                <td key={i}>{l.toFixed(1)}</td>
              ))}
              <td><strong>{r.l_a_eq.toFixed(1)}</strong></td>
              <td>{r.pdu_eq}</td>
              <td style={{
                fontWeight: "bold",
                color: getExceedanceColor(r.exceedance_eq),
              }}>
                {r.exceedance_eq > 0 ? "+" : ""}{r.exceedance_eq.toFixed(1)}
              </td>
              <td style={{ color: r.exceeded ? "#c62828" : "#2e7d32", fontWeight: "bold" }}>
                {r.exceeded ? "ПРЕВЫШЕНИЕ" : "Норма"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
