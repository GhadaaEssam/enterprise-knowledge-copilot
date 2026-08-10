# src/monitoring/tracker.py

import uuid
from datetime import datetime, timezone

from src.monitoring.database import MonitoringDatabase


class MonitoringTracker:

    def __init__(
        self,
        db_path: str = "data/monitoring/monitoring.db",
    ):
        self.db = MonitoringDatabase(db_path)

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    def start_request(
        self,
        question: str,
        model: str,
    ) -> str:

        request_id = str(uuid.uuid4())

        with self.db._connect() as conn:
            conn.execute(
                """
                INSERT INTO requests (
                    id,
                    timestamp,
                    question,
                    model,
                    status
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    self._timestamp(),
                    question,
                    model,
                    "running",
                ),
            )

            conn.commit()

        return request_id

    def record_llm_call(
        self,
        request_id: str,
        iteration: int,
        model: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        duration_ms: float,
        estimated_cost: float,
    ):

        with self.db._connect() as conn:
            conn.execute(
                """
                INSERT INTO llm_calls (
                    request_id,
                    timestamp,
                    iteration,
                    model,
                    input_tokens,
                    output_tokens,
                    total_tokens,
                    duration_ms,
                    estimated_cost
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    self._timestamp(),
                    iteration,
                    model,
                    input_tokens,
                    output_tokens,
                    total_tokens,
                    duration_ms,
                    estimated_cost,
                ),
            )

            conn.commit()

    def record_tool_call(
        self,
        request_id: str,
        iteration: int,
        tool_name: str,
        query: str,
        duration_ms: float,
        success: bool,
        result_size: int,
    ):

        with self.db._connect() as conn:
            conn.execute(
                """
                INSERT INTO tool_calls (
                    request_id,
                    iteration,
                    tool_name,
                    query,
                    duration_ms,
                    success,
                    result_size
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    iteration,
                    tool_name,
                    query,
                    duration_ms,
                    int(success),
                    result_size,
                ),
            )

            conn.commit()

    def record_feedback(
        self,
        request_id: str,
        feedback: str,
    ):
        with self.db._connect() as conn:
            conn.execute(
                """
                INSERT INTO feedback (
                    request_id,
                    feedback,
                    timestamp
                )
                VALUES (?, ?, ?)
                """,
                (
                    request_id,
                    feedback,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            conn.commit()

    def finish_request(
        self,
        request_id: str,
        answer: str,
        response_time_ms: float,
        iterations: int,
        stop_reason: str,
        status: str,
        total_input_tokens: int,
        total_output_tokens: int,
        total_tokens: int,
        estimated_cost: float,
    ):

        with self.db._connect() as conn:
            conn.execute(
                """
                UPDATE requests
                SET
                    answer = ?,
                    response_time_ms = ?,
                    iterations = ?,
                    stop_reason = ?,
                    status = ?,
                    total_input_tokens = ?,
                    total_output_tokens = ?,
                    total_tokens = ?,
                    estimated_cost = ?
                WHERE id = ?
                """,
                (
                    answer,
                    response_time_ms,
                    iterations,
                    stop_reason,
                    status,
                    total_input_tokens,
                    total_output_tokens,
                    total_tokens,
                    estimated_cost,
                    request_id,
                ),
            )

            conn.commit()