/**
 * IPC обработчики: мост между Renderer и Python API.
 */
import { ipcMain } from "electron";
import { API_BASE } from "./python-bridge";

async function apiPost(endpoint: string, body: unknown): Promise<unknown> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ошибка ${res.status}: ${text}`);
  }
  return res.json();
}

async function apiGet(endpoint: string): Promise<unknown> {
  const res = await fetch(`${API_BASE}${endpoint}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ошибка ${res.status}: ${text}`);
  }
  return res.json();
}

export function registerIpcHandlers(): void {
  // Главный расчётный вызов
  ipcMain.handle("acoustik:calculate", async (_event, request: unknown) => {
    return apiPost("/calculate_noise/", request);
  });

  // Управление источниками
  ipcMain.handle("acoustik:getSources", async (_event, projectId: string) => {
    return apiGet(`/sources/?project_id=${encodeURIComponent(projectId)}`);
  });

  ipcMain.handle(
    "acoustik:addSource",
    async (_event, projectId: string, source: unknown) => {
      return apiPost(`/sources/?project_id=${encodeURIComponent(projectId)}`, source);
    }
  );

  // Экспорт в QGIS
  ipcMain.handle("acoustik:exportToQgis", async (_event, projectId: string) => {
    return apiPost(`/export_to_qgis/?project_id=${encodeURIComponent(projectId)}`, {});
  });

  // Отчёт
  ipcMain.handle(
    "acoustik:getReport",
    async (_event, projectId: string, format = "json") => {
      return apiGet(
        `/report/?project_id=${encodeURIComponent(projectId)}&format=${format}`
      );
    }
  );

  // Health check
  ipcMain.handle("acoustik:health", async () => {
    return apiGet("/health");
  });
}
