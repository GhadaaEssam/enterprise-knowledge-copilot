# app/components/monitoring.py

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# Configuration
# ============================================================

MONITORING_DB = Path("data/monitoring/monitoring.db")


# ============================================================
# Database helpers
# ============================================================

@st.cache_data(ttl=2)
def load_table(table_name: str) -> pd.DataFrame:
    """Load a monitoring table from SQLite."""

    if not MONITORING_DB.exists():
        return pd.DataFrame()

    try:
        with sqlite3.connect(MONITORING_DB) as conn:
            return pd.read_sql_query(
                f'SELECT * FROM "{table_name}"',
                conn,
            )
    except Exception:
        return pd.DataFrame()


def get_tables() -> list[str]:
    """Return available tables in the monitoring database."""

    if not MONITORING_DB.exists():
        return []

    try:
        with sqlite3.connect(MONITORING_DB) as conn:
            rows = conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()

        return [row[0] for row in rows]

    except Exception:
        return []


def find_column(
    df: pd.DataFrame,
    candidates: list[str],
) -> str | None:
    """Find the first matching column from a list of candidates."""

    if df.empty:
        return None

    lower_columns = {
        column.lower(): column
        for column in df.columns
    }

    for candidate in candidates:
        if candidate.lower() in lower_columns:
            return lower_columns[candidate.lower()]

    return None


def numeric_column(
    df: pd.DataFrame,
    candidates: list[str],
) -> str | None:
    """Find a numeric column from candidate names."""

    column = find_column(df, candidates)

    if column is None:
        return None

    try:
        pd.to_numeric(df[column])
        return column
    except Exception:
        return None


# ============================================================
# Data preparation
# ============================================================

def prepare_requests(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize request-level monitoring data."""

    if df.empty:
        return df

    df = df.copy()

    timestamp = find_column(
        df,
        [
            "timestamp",
            "created_at",
            "started_at",
            "request_time",
            "time",
        ],
    )

    if timestamp:
        df["timestamp"] = pd.to_datetime(
            df[timestamp],
            errors="coerce",
        )

    latency = numeric_column(
        df,
        [
            "latency_ms",
            "response_time_ms",
            "duration_ms",
            "total_latency_ms",
            "latency",
        ],
    )

    if latency:
        df["latency_ms"] = pd.to_numeric(
            df[latency],
            errors="coerce",
        )

    tokens = numeric_column(
        df,
        [
            "total_tokens",
            "tokens",
        ],
    )

    if tokens:
        df["total_tokens"] = pd.to_numeric(
            df[tokens],
            errors="coerce",
        )

    iterations = numeric_column(
        df,
        [
            "iterations",
            "iteration_count",
        ],
    )

    if iterations:
        df["iterations"] = pd.to_numeric(
            df[iterations],
            errors="coerce",
        )

    return df


def prepare_llm_calls(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize LLM call monitoring data."""

    if df.empty:
        return df

    df = df.copy()

    timestamp = find_column(
        df,
        [
            "timestamp",
            "created_at",
            "started_at",
            "time",
        ],
    )

    if timestamp:
        df["timestamp"] = pd.to_datetime(
            df[timestamp],
            errors="coerce",
        )

    input_tokens = numeric_column(
        df,
        [
            "input_tokens",
            "prompt_tokens",
        ],
    )

    output_tokens = numeric_column(
        df,
        [
            "output_tokens",
            "completion_tokens",
        ],
    )

    total_tokens = numeric_column(
        df,
        [
            "total_tokens",
            "tokens",
        ],
    )

    latency = numeric_column(
        df,
        [
            "latency_ms",
            "response_time_ms",
            "duration_ms",
        ],
    )

    cost = numeric_column(
        df,
        [
            "cost",
            "estimated_cost",
            "cost_usd",
        ],
    )

    if input_tokens:
        df["input_tokens"] = pd.to_numeric(
            df[input_tokens],
            errors="coerce",
        )

    if output_tokens:
        df["output_tokens"] = pd.to_numeric(
            df[output_tokens],
            errors="coerce",
        )

    if total_tokens:
        df["total_tokens"] = pd.to_numeric(
            df[total_tokens],
            errors="coerce",
        )
    elif input_tokens and output_tokens:
        df["total_tokens"] = (
            df["input_tokens"].fillna(0)
            + df["output_tokens"].fillna(0)
        )

    if latency:
        df["latency_ms"] = pd.to_numeric(
            df[latency],
            errors="coerce",
        )

    if cost:
        df["cost"] = pd.to_numeric(
            df[cost],
            errors="coerce",
        )

    return df


def prepare_tools(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize tool-call monitoring data."""

    if df.empty:
        return df

    df = df.copy()

    timestamp = find_column(
        df,
        [
            "timestamp",
            "created_at",
            "started_at",
            "time",
        ],
    )

    if timestamp:
        df["timestamp"] = pd.to_datetime(
            df[timestamp],
            errors="coerce",
        )

    tool_name = find_column(
        df,
        [
            "tool_name",
            "name",
            "tool",
        ],
    )

    if tool_name:
        df["tool_name"] = df[tool_name].astype(str)

    latency = numeric_column(
        df,
        [
            "latency_ms",
            "duration_ms",
            "response_time_ms",
        ],
    )

    if latency:
        df["latency_ms"] = pd.to_numeric(
            df[latency],
            errors="coerce",
        )

    return df


# ============================================================
# KPI helpers
# ============================================================

def safe_mean(df: pd.DataFrame, column: str) -> float | None:
    if column not in df.columns:
        return None

    values = pd.to_numeric(
        df[column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return None

    return float(values.mean())


def format_number(value) -> str:
    if value is None:
        return "N/A"

    return f"{value:,.0f}"


def format_ms(value) -> str:
    if value is None:
        return "N/A"

    if value >= 1000:
        return f"{value / 1000:.2f}s"

    return f"{value:.0f} ms"


def format_cost(value) -> str:
    if value is None:
        return "N/A"

    return f"${value:.4f}"


# ============================================================
# Main dashboard
# ============================================================

def render_monitoring():

    st.title("📈 Monitoring")

    st.caption(
        "Operational monitoring of the Enterprise Knowledge Copilot."
    )

    # --------------------------------------------------------
    # Check database
    # --------------------------------------------------------

    if not MONITORING_DB.exists():

        st.warning(
            f"Monitoring database not found: "
            f"`{MONITORING_DB}`"
        )

        st.info(
            "Run the Streamlit application and send a few "
            "queries first so monitoring data can be collected."
        )

        return

    tables = get_tables()

    if not tables:

        st.warning(
            "The monitoring database exists but contains no tables."
        )

        return

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    requests = prepare_requests(
        load_table("requests")
    )

    llm_calls = prepare_llm_calls(
        load_table("llm_calls")
    )

    tool_calls = prepare_tools(
        load_table("tool_calls")
    )

    # --------------------------------------------------------
    # Refresh
    # --------------------------------------------------------

    col_refresh, col_info = st.columns([1, 5])

    with col_refresh:

        if st.button("🔄 Refresh"):

            st.cache_data.clear()
            st.rerun()


    # --------------------------------------------------------
    # Global KPIs
    # --------------------------------------------------------

    request_count = len(requests)

    avg_latency = safe_mean(
        requests,
        "latency_ms",
    )

    total_tokens = None

    if "total_tokens" in llm_calls.columns:
        total_tokens = pd.to_numeric(
            llm_calls["total_tokens"],
            errors="coerce",
        ).sum()

    total_cost = None

    if "cost" in llm_calls.columns:
        total_cost = pd.to_numeric(
            llm_calls["cost"],
            errors="coerce",
        ).sum()

    avg_iterations = safe_mean(
        requests,
        "iterations",
    )

    st.subheader("Overview")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Requests",
            f"{request_count:,}",
        )

    with c2:
        st.metric(
            "Avg Latency",
            format_ms(avg_latency),
        )

    with c3:
        st.metric(
            "Total Tokens",
            format_number(total_tokens),
        )

    with c4:
        st.metric(
            "Estimated Cost",
            format_cost(total_cost),
        )

    with c5:
        st.metric(
            "Avg Iterations",
            f"{avg_iterations:.2f}"
            if avg_iterations is not None
            else "N/A",
        )

    st.divider()

    # ========================================================
    # feedback table
    # ========================================================


    feedback = load_table("feedback")

    st.subheader("👍 User Feedback")

    if not feedback.empty:

        likes = (feedback["feedback"] == "like").sum()
        dislikes = (feedback["feedback"] == "dislike").sum()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Feedback", len(feedback))

        with col2:
            st.metric("👍 Likes", likes)

        with col3:
            st.metric("👎 Dislikes", dislikes)

        feedback_counts = (
            feedback["feedback"]
            .value_counts()
            .rename("count")
        )

        st.bar_chart(feedback_counts)

    else:
        st.info("No user feedback yet.")

    st.subheader("Recent Feedback")

    st.dataframe(
        feedback.sort_values(
            "timestamp",
            ascending=False,
        ).head(20),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ========================================================
    # Chart 1 — Requests over time
    # ========================================================

    st.subheader("📊 Request Activity")

    if (
        not requests.empty
        and "timestamp" in requests.columns
        and requests["timestamp"].notna().any()
    ):

        request_time = (
            requests.dropna(subset=["timestamp"])
            .set_index("timestamp")
            .resample("h")
            .size()
            .rename("requests")
        )

        st.line_chart(
            request_time,
            use_container_width=True,
        )

    else:

        st.info(
            "Timestamp data is not available for request activity."
        )

    # ========================================================
    # Chart 2 — Latency over time
    # ========================================================

    st.subheader("⏱️ Response Latency")

    if (
        not requests.empty
        and "timestamp" in requests.columns
        and "latency_ms" in requests.columns
    ):

        latency_data = (
            requests.dropna(
                subset=[
                    "timestamp",
                    "latency_ms",
                ]
            )
            .set_index("timestamp")["latency_ms"]
            .resample("h")
            .mean()
        )

        st.line_chart(
            latency_data,
            use_container_width=True,
        )

        if len(latency_data.dropna()) >= 2:

            p50 = latency_data.quantile(0.50)
            p95 = latency_data.quantile(0.95)

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "P50 Latency",
                    format_ms(p50),
                )

            with c2:
                st.metric(
                    "P95 Latency",
                    format_ms(p95),
                )

    else:

        st.info(
            "Latency data is not available."
        )

    # ========================================================
    # Chart 3 — Token usage
    # ========================================================

    st.subheader("🔤 Token Usage")

    if (
        not llm_calls.empty
        and "timestamp" in llm_calls.columns
        and "total_tokens" in llm_calls.columns
    ):

        token_data = (
            llm_calls.dropna(
                subset=[
                    "timestamp",
                    "total_tokens",
                ]
            )
            .set_index("timestamp")["total_tokens"]
            .resample("h")
            .sum()
        )

        st.bar_chart(
            token_data,
            use_container_width=True,
        )

    else:

        st.info(
            "Token usage data is not available."
        )

    # ========================================================
    # Chart 4 — Input vs Output Tokens
    # ========================================================

    st.subheader("📥 Input vs Output Tokens")

    if (
        not llm_calls.empty
        and "input_tokens" in llm_calls.columns
        and "output_tokens" in llm_calls.columns
    ):

        token_comparison = llm_calls[
            [
                "input_tokens",
                "output_tokens",
            ]
        ].sum()

        st.bar_chart(
            token_comparison,
            use_container_width=True,
        )

    else:

        st.info(
            "Input/output token data is not available."
        )

    # ========================================================
    # Chart 5 — Tool usage
    # ========================================================

    st.subheader("🛠️ Tool Usage")

    if (
        not tool_calls.empty
        and "tool_name" in tool_calls.columns
    ):

        tool_usage = (
            tool_calls["tool_name"]
            .value_counts()
            .rename("calls")
        )

        st.bar_chart(
            tool_usage,
            use_container_width=True,
        )

    else:

        st.info(
            "Tool usage data is not available."
        )

    # ========================================================
    # Chart 6 — Tool latency
    # ========================================================

    st.subheader("⚡ Tool Performance")

    if (
        not tool_calls.empty
        and "tool_name" in tool_calls.columns
        and "latency_ms" in tool_calls.columns
    ):

        tool_latency = (
            tool_calls.groupby("tool_name")["latency_ms"]
            .mean()
            .sort_values(
                ascending=False
            )
        )

        st.bar_chart(
            tool_latency,
            use_container_width=True,
        )

    else:

        st.info(
            "Tool latency data is not available."
        )

    # ========================================================
    # Chart 7 — LLM model usage
    # ========================================================

    st.subheader("🤖 Model Usage")

    model_column = find_column(
        llm_calls,
        [
            "model",
            "model_name",
        ],
    )

    if model_column:

        model_usage = (
            llm_calls[model_column]
            .astype(str)
            .value_counts()
            .rename("calls")
        )

        st.bar_chart(
            model_usage,
            use_container_width=True,
        )

    else:

        st.info(
            "Model information is not available."
        )

    # ========================================================
    # Cost
    # ========================================================

    st.subheader("💰 Cost")

    if (
        not llm_calls.empty
        and "timestamp" in llm_calls.columns
        and "cost" in llm_calls.columns
    ):

        cost_data = (
            llm_calls.dropna(
                subset=[
                    "timestamp",
                    "cost",
                ]
            )
            .set_index("timestamp")["cost"]
            .resample("h")
            .sum()
        )

        st.line_chart(
            cost_data,
            use_container_width=True,
        )

    else:

        st.info(
            "Cost data is not available."
        )

    # ========================================================
    # Recent Requests
    # ========================================================

    st.divider()

    st.subheader("🧾 Recent Requests")

    if not requests.empty:

        display = requests.copy()

        # Find question column
        question_column = find_column(
            display,
            [
                "question",
                "query",
                "user_question",
                "prompt",
            ],
        )

        columns = []

        if "timestamp" in display.columns:
            columns.append("timestamp")

        if question_column:
            columns.append(question_column)

        if "latency_ms" in display.columns:
            columns.append("latency_ms")

        if "iterations" in display.columns:
            columns.append("iterations")

        if columns:

            recent = (
                display[columns]
                .sort_values(
                    "timestamp",
                    ascending=False,
                )
                .head(20)
            )

            st.dataframe(
                recent,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.dataframe(
                display.head(20),
                use_container_width=True,
                hide_index=True,
            )

    else:

        st.info(
            "No requests have been recorded yet."
        )