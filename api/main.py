"""
FastAPI приложение — главный API-сервер Акустик.
Порт: 8765
MCP endpoint: http://localhost:8765/mcp/sse (SSE transport)
"""
from __future__ import annotations

import sys
import os
from contextlib import asynccontextmanager
from pathlib import Path

# Добавить корневую директорию проекта в sys.path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import init_db
from api.routers import calculate, sources, export, report


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Акустик API",
    description="API для акустических расчётов по СП 51.13330.2011 / ГОСТ 31295.2-2005",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # только localhost в production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST маршруты
app.include_router(calculate.router)
app.include_router(sources.router)
app.include_router(export.router)
app.include_router(report.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "acoustik-api", "version": "1.0.0"}


# MCP сервер (монтируется только если mcp установлен)
def _setup_mcp() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
        from api.mcp_tools import register_mcp_tools

        mcp = FastMCP("acoustik")
        register_mcp_tools(mcp)
        # Монтировать MCP как SSE endpoint
        mcp_app = mcp.get_asgi_app()
        app.mount("/mcp", mcp_app)
        print("[Акустик] MCP сервер запущен: http://localhost:8765/mcp/sse")
    except ImportError:
        print("[Акустик] MCP SDK не установлен — агентный режим недоступен")
    except Exception as e:
        print(f"[Акустик] Ошибка настройки MCP: {e}")


_setup_mcp()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
