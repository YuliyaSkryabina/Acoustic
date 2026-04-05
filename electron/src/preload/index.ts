/**
 * Preload script — безопасный мост между main и renderer через contextBridge.
 */
import { contextBridge, ipcRenderer } from "electron";

export type AcoustikAPI = {
  calculate: (request: unknown) => Promise<unknown>;
  getSources: (projectId: string) => Promise<unknown[]>;
  addSource: (projectId: string, source: unknown) => Promise<unknown>;
  exportToQgis: (projectId: string) => Promise<unknown>;
  getReport: (projectId: string, format?: string) => Promise<unknown>;
  health: () => Promise<unknown>;
};

contextBridge.exposeInMainWorld("acoustik", {
  calculate: (request: unknown) =>
    ipcRenderer.invoke("acoustik:calculate", request),

  getSources: (projectId: string) =>
    ipcRenderer.invoke("acoustik:getSources", projectId),

  addSource: (projectId: string, source: unknown) =>
    ipcRenderer.invoke("acoustik:addSource", projectId, source),

  exportToQgis: (projectId: string) =>
    ipcRenderer.invoke("acoustik:exportToQgis", projectId),

  getReport: (projectId: string, format = "json") =>
    ipcRenderer.invoke("acoustik:getReport", projectId, format),

  health: () => ipcRenderer.invoke("acoustik:health"),
} satisfies AcoustikAPI);
