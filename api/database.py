"""
SQLite база данных через aiosqlite.
Хранит проекты, источники шума, расчётные точки, результаты.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import aiosqlite

DB_PATH = Path.home() / ".acoustik" / "projects.db"

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS calc_points (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    data JSON NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS screens (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    data JSON NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    point_id TEXT NOT NULL,
    period TEXT NOT NULL,
    data JSON NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
"""


async def get_db() -> aiosqlite.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON")
    return db


async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES)
        await db.commit()


async def get_sources(project_id: str) -> list[dict]:
    async with await get_db() as db:
        cursor = await db.execute(
            "SELECT data FROM sources WHERE project_id = ?", (project_id,)
        )
        rows = await cursor.fetchall()
        return [json.loads(row["data"]) for row in rows]


async def save_source(project_id: str, source_data: dict) -> None:
    async with await get_db() as db:
        await db.execute(
            "INSERT OR REPLACE INTO sources (id, project_id, data) VALUES (?, ?, ?)",
            (source_data["id"], project_id, json.dumps(source_data))
        )
        await db.commit()


async def save_result(project_id: str, result_data: dict) -> None:
    async with await get_db() as db:
        await db.execute(
            """INSERT INTO results (project_id, point_id, period, data)
               VALUES (?, ?, ?, ?)""",
            (project_id, result_data["point_id"], result_data["period"],
             json.dumps(result_data))
        )
        await db.commit()


async def get_results(project_id: str) -> list[dict]:
    async with await get_db() as db:
        cursor = await db.execute(
            """SELECT data FROM results
               WHERE project_id = ?
               ORDER BY calculated_at DESC""",
            (project_id,)
        )
        rows = await cursor.fetchall()
        return [json.loads(row["data"]) for row in rows]
