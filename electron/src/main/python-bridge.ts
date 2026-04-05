/**
 * Управление жизненным циклом Python API-сервера.
 * Запускает uvicorn при старте Electron, останавливает при закрытии.
 */
import { spawn, ChildProcess } from "child_process";
import { app } from "electron";
import path from "path";

let pythonProcess: ChildProcess | null = null;
const API_PORT = 8765;
export const API_BASE = `http://127.0.0.1:${API_PORT}`;

function getPythonExecutable(): string {
  if (app.isPackaged) {
    // В production: Python рядом с .exe (упакован electron-builder)
    return path.join(process.resourcesPath, "python", "python.exe");
  }
  // В development: системный python
  return process.platform === "win32" ? "python" : "python3";
}

function getProjectRoot(): string {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "app");
  }
  // В development: корень проекта (родительская директория electron/)
  return path.resolve(__dirname, "..", "..", "..", "..");
}

async function waitForServer(url: string, timeoutMs = 30_000): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(url);
      if (res.ok) return;
    } catch {
      // Сервер ещё не запустился
    }
    await new Promise((r) => setTimeout(r, 300));
  }
  throw new Error(`[Акустик] Python API не запустился за ${timeoutMs}ms`);
}

export async function startPythonServer(): Promise<void> {
  const python = getPythonExecutable();
  const cwd = getProjectRoot();

  console.log(`[Акустик] Запуск Python: ${python}`);
  console.log(`[Акустик] Рабочая директория: ${cwd}`);

  pythonProcess = spawn(
    python,
    [
      "-m", "uvicorn",
      "api.main:app",
      "--host", "127.0.0.1",
      "--port", String(API_PORT),
      "--no-access-log",
    ],
    {
      cwd,
      env: { ...process.env, PYTHONUNBUFFERED: "1" },
      stdio: ["ignore", "pipe", "pipe"],
    }
  );

  pythonProcess.stdout?.on("data", (d: Buffer) =>
    console.log("[Python]", d.toString().trim())
  );
  pythonProcess.stderr?.on("data", (d: Buffer) =>
    console.error("[Python ERR]", d.toString().trim())
  );
  pythonProcess.on("exit", (code) =>
    console.log(`[Акустик] Python завершился с кодом ${code}`)
  );

  await waitForServer(`${API_BASE}/health`);
  console.log("[Акустик] Python API сервер готов");
}

export function stopPythonServer(): void {
  if (pythonProcess) {
    console.log("[Акустик] Остановка Python сервера");
    pythonProcess.kill("SIGTERM");
    pythonProcess = null;
  }
}
