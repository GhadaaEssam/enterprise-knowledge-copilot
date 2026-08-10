# src/monitoring/database.py

import sqlite3
from pathlib import Path


class MonitoringDatabase:

    def __init__(
        self,
        db_path: str = "data/monitoring/monitoring.db",
    ):
        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _initialize(self):

        with self._connect() as conn:

            # --------------------------------------------------
            # Requests
            # --------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT,
                    model TEXT,
                    response_time_ms REAL,
                    iterations INTEGER,
                    stop_reason TEXT,
                    status TEXT,
                    total_input_tokens INTEGER DEFAULT 0,
                    total_output_tokens INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    estimated_cost REAL DEFAULT 0
                )
                """
            )

            # --------------------------------------------------
            # LLM calls
            # --------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    iteration INTEGER,
                    model TEXT,
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    duration_ms REAL,
                    estimated_cost REAL DEFAULT 0,

                    FOREIGN KEY (request_id)
                        REFERENCES requests(id)
                )
                """
            )

            # --------------------------------------------------
            # Tool calls
            # --------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    iteration INTEGER,
                    tool_name TEXT,
                    query TEXT,
                    duration_ms REAL,
                    success INTEGER,
                    result_size INTEGER,

                    FOREIGN KEY (request_id)
                        REFERENCES requests(id)
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    feedback TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (request_id)
                        REFERENCES requests(id)
                )
                """
            )

            conn.commit()