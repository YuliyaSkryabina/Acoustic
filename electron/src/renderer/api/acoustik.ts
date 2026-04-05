/**
 * HTTP клиент к Python API (для использования напрямую без IPC).
 * В Electron используется через window.acoustik (IPC).
 */
const API_BASE = "http://127.0.0.1:8765";

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
