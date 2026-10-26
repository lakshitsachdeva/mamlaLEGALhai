"""Small, dependency-free SQLite store for analyses and review decisions."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _database_path() -> Path:
    configured = os.getenv("REGULATRACE_DB_PATH")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[1] / ".regulatrace" / "regulatrace.db"


def _connect() -> sqlite3.Connection:
    path = _database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            source_title TEXT NOT NULL,
            authority TEXT NOT NULL,
            jurisdiction TEXT NOT NULL,
            record_count INTEGER NOT NULL,
            unresolved_count INTEGER NOT NULL,
            reviewed_count INTEGER NOT NULL DEFAULT 0,
            payload TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT NOT NULL,
            record_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            note TEXT,
            reviewer TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
        );
        """
    )
    return connection


def save_analysis(payload: dict[str, Any]) -> str:
    analysis_id = f"AN-{uuid4().hex[:12].upper()}"
    payload["analysisId"] = analysis_id
    source = payload.get("source") or {}
    summary = payload.get("summary") or {}
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO analyses (
                id, created_at, source_title, authority, jurisdiction,
                record_count, unresolved_count, reviewed_count, payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (
                analysis_id,
                payload.get("analyzedAt") or _utc_now(),
                source.get("title") or source.get("section") or "Untitled regulatory source",
                source.get("authority") or "Unknown authority",
                source.get("jurisdiction") or "Unknown",
                len(payload.get("records") or []),
                int(summary.get("unresolvedCount") or 0),
                json.dumps(payload, ensure_ascii=False),
            ),
        )
    return analysis_id


def get_analysis(analysis_id: str) -> dict[str, Any] | None:
    with _connect() as connection:
        row = connection.execute("SELECT payload FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    return json.loads(row["payload"]) if row else None


def list_analyses(limit: int = 12) -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, source_title, authority, jurisdiction,
                   record_count, unresolved_count, reviewed_count
            FROM analyses ORDER BY created_at DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "analysisId": row["id"],
            "createdAt": row["created_at"],
            "sourceTitle": row["source_title"],
            "authority": row["authority"],
            "jurisdiction": row["jurisdiction"],
            "recordCount": row["record_count"],
            "unresolvedCount": row["unresolved_count"],
            "reviewedCount": row["reviewed_count"],
        }
        for row in rows
    ]


def record_review(
    analysis_id: str,
    record_id: str,
    decision: str,
    note: str | None,
    reviewer: str,
) -> dict[str, Any] | None:
    payload = get_analysis(analysis_id)
    if payload is None:
        return None
    located = False
    for collection_name in ("records", "normative"):
        for record in payload.get(collection_name) or []:
            if record.get("id") == record_id:
                record["reviewState"] = decision
                located = True
    if not located:
        return None
    reviewed_count = sum(1 for record in payload.get("records") or [] if record.get("reviewState") != "UNREVIEWED")
    created_at = _utc_now()
    with _connect() as connection:
        connection.execute(
            "UPDATE analyses SET reviewed_count = ?, payload = ? WHERE id = ?",
            (reviewed_count, json.dumps(payload, ensure_ascii=False), analysis_id),
        )
        connection.execute(
            """
            INSERT INTO audit_events (analysis_id, record_id, decision, note, reviewer, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (analysis_id, record_id, decision, note, reviewer, created_at),
        )
    return {
        "analysisId": analysis_id,
        "recordId": record_id,
        "decision": decision,
        "reviewer": reviewer,
        "note": note,
        "createdAt": created_at,
        "reviewedCount": reviewed_count,
    }


def audit_trail(analysis_id: str, limit: int = 100) -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT record_id, decision, note, reviewer, created_at
            FROM audit_events WHERE analysis_id = ? ORDER BY id DESC LIMIT ?
            """,
            (analysis_id, limit),
        ).fetchall()
    return [
        {
            "recordId": row["record_id"],
            "decision": row["decision"],
            "note": row["note"],
            "reviewer": row["reviewer"],
            "createdAt": row["created_at"],
        }
        for row in rows
    ]


def dashboard() -> dict[str, Any]:
    with _connect() as connection:
        totals = connection.execute(
            """
            SELECT COUNT(*) AS analyses,
                   COALESCE(SUM(record_count), 0) AS records,
                   COALESCE(SUM(unresolved_count), 0) AS unresolved,
                   COALESCE(SUM(reviewed_count), 0) AS reviewed
            FROM analyses
            """
        ).fetchone()
        decisions = connection.execute(
            "SELECT decision, COUNT(*) AS count FROM audit_events GROUP BY decision"
        ).fetchall()
    return {
        "analyses": totals["analyses"],
        "records": totals["records"],
        "unresolved": totals["unresolved"],
        "reviewed": totals["reviewed"],
        "decisions": {row["decision"]: row["count"] for row in decisions},
        "database": str(_database_path()),
    }
