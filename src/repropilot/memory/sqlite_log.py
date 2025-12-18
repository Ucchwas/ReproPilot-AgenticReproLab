from __future__ import annotations
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(
  run_id TEXT PRIMARY KEY,
  created_at REAL
);

CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT,
  ts REAL,
  kind TEXT,
  payload TEXT
);
"""


@dataclass(frozen=True)
class RunLogger:
    db_path: str

    def _connect(self) -> sqlite3.Connection:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def init(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def start_run(self, run_id: str) -> None:
        self.init()
        with self._connect() as conn:
            conn.execute("INSERT OR REPLACE INTO runs(run_id, created_at) VALUES(?, ?)", (run_id, time.time()))

    def log(self, run_id: str, kind: str, payload: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO events(run_id, ts, kind, payload) VALUES(?, ?, ?, ?)",
                (run_id, time.time(), kind, payload),
            )
