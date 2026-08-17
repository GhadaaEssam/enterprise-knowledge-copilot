# app/components/evaluation.py

import json
from pathlib import Path

import pandas as pd
import streamlit as st


def load_evaluation_results() -> list[dict]:
    """Load evaluation results from eval_report.json."""

    root_dir = Path(__file__).resolve().parents[2]

    eval_path = (
        root_dir
        / "data"
        / "results"
        / "llm_eval_report.json"
    )

    if not eval_path.exists():
        return []

    with open(
        eval_path,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def calculate_metrics(
    results: list[dict],
) -> dict:
    """Calculate aggregate evaluation metrics."""

    n_cases = len(results)

    def score_values(axis: str) -> list[float]:
        return [
            r["scores"][axis]
            for r in results
            if r.get("scores", {}).get(axis)
            is not None
        ]

    correctness = score_values("correctness")
    groundedness = score_values("groundedness")
    context_relevance = score_values(
        "context_relevance"
    )

    tool_results = [
        r.get("tool_selection", {})
        for r in results
    ]

    tool_accuracy = [
        r.get("accuracy")
        for r in tool_results
        if r.get("accuracy") is not None
    ]

    correct_tool_count = sum(
        1
        for r in tool_results
        if r.get("correct") is True
    )

    internal_search_count = sum(
        1
        for r in tool_results
        if r.get("internal_search_used") is True
    )

    web_search_count = sum(
        1
        for r in tool_results
        if r.get("web_search_used") is True
    )

    no_tool_count = sum(
        1
        for r in tool_results
        if r.get("no_tool_called") is True
    )

    unnecessary_web_count = sum(
        1
        for r in tool_results
        if r.get("unnecessary_web_search") is True
    )

    return {
        "n_cases": n_cases,

        "correctness_mean": (
            sum(correctness) / len(correctness)
            if correctness
            else None
        ),

        "correctness_scored": len(
            correctness
        ),

        "groundedness_mean": (
            sum(groundedness) / len(groundedness)
            if groundedness
            else None
        ),

        "groundedness_scored": len(
            groundedness
        ),

        "context_relevance_mean": (
            sum(context_relevance)
            / len(context_relevance)
            if context_relevance
            else None
        ),

        "context_relevance_scored": len(
            context_relevance
        ),

        "tool_selection_accuracy": (
            sum(tool_accuracy) / len(tool_accuracy)
            if tool_accuracy
            else None
        ),

        "correct_tool_count": correct_tool_count,

        "internal_search_usage_rate": (
            internal_search_count / n_cases
            if n_cases
            else None
        ),

        "web_search_usage_rate": (
            web_search_count / n_cases
            if n_cases
            else None
        ),

        "no_tool_called_rate": (
            no_tool_count / n_cases
            if n_cases
            else None
        ),

        "unnecessary_web_search_rate": (
            unnecessary_web_count / n_cases
            if n_cases
            else None
        ),

    }


def render_metric_cards(
    metrics: dict,
):
    """Display top-level evaluation metrics."""

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Test Cases",
            metrics["n_cases"],
        )

    with col2:
        value = metrics["correctness_mean"]

        st.metric(
            "Correctness",
            (
                f"{value:.2f} / 5"
                if value is not None
                else "N/A"
            ),
        )

    with col3:
        value = metrics["groundedness_mean"]

        st.metric(
            "Groundedness",
            (
                f"{value:.2f} / 5"
                if value is not None
                else "N/A"
            ),
        )

    with col4:
        value = metrics["context_relevance_mean"]

        st.metric(
            "Context Relevance",
            (
                f"{value:.2f} / 5"
                if value is not None
                else "N/A"
            ),
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        value = metrics["tool_selection_accuracy"]

        st.metric(
            "Tool Selection",
            (
                f"{value:.2%}"
                if value is not None
                else "N/A"
            ),
        )

    with col2:
        st.metric(
            "Correct Tool Calls",
            (
                f"{metrics['correct_tool_count']}"
                f" / {metrics['n_cases']}"
            ),
        )

    with col3:
        value = metrics["internal_search_usage_rate"]

        st.metric(
            "Internal Search Usage",
            (
                f"{value:.2%}"
                if value is not None
                else "N/A"
            ),
        )

    with col4:
        value = metrics["web_search_usage_rate"]

        st.metric(
            "Web Search Usage",
            (
                f"{value:.2%}"
                if value is not None
                else "N/A"
            ),
        )


def render_score_distribution(
    results: list[dict],
):
    """Display distributions of judge scores."""

    st.subheader(
        "📈 Score Distribution"
    )

    correctness = [
        r["scores"]["correctness"]
        for r in results
        if r.get("scores", {}).get("correctness")
        is not None
    ]

    groundedness = [
        r["scores"]["groundedness"]
        for r in results
        if r.get("scores", {}).get("groundedness")
        is not None
    ]

    context_relevance = [
        r["scores"]["context_relevance"]
        for r in results
        if r.get("scores", {}).get("context_relevance")
        is not None
    ]

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            "**Correctness**"
        )

        if correctness:
            df = pd.DataFrame(
                {
                    "Score": correctness
                }
            )

            st.bar_chart(
                df["Score"]
                .value_counts()
                .sort_index()
            )

        else:
            st.info(
                "No correctness scores available."
            )

    with col2:

        st.markdown(
            "**Groundedness**"
        )

        if groundedness:
            df = pd.DataFrame(
                {
                    "Score": groundedness
                }
            )

            st.bar_chart(
                df["Score"]
                .value_counts()
                .sort_index()
            )

        else:
            st.info(
                "No groundedness scores available."
            )

    with col3:

        st.markdown(
            "**Context Relevance**"
        )

        if context_relevance:
            df = pd.DataFrame(
                {
                    "Score": context_relevance
                }
            )

            st.bar_chart(
                df["Score"]
                .value_counts()
                .sort_index()
            )

        else:
            st.info(
                "No context relevance scores available."
            )


def render_tool_selection_summary(
    metrics: dict,
):
    """Display aggregate tool-selection metrics."""

    st.subheader(
        "🧭 Tool Selection"
    )

    values = {
        "Internal search usage": (
            metrics["internal_search_usage_rate"]
        ),
        "Web search usage": (
            metrics["web_search_usage_rate"]
        ),
        "No tool called": (
            metrics["no_tool_called_rate"]
        ),
        "Unnecessary web search": (
            metrics["unnecessary_web_search_rate"]
        ),
    }

    df = pd.DataFrame(
        [
            {
                "Metric": name,
                "Rate": value,
            }
            for name, value in values.items()
            if value is not None
        ]
    )

    if df.empty:
        st.info(
            "No tool-selection metrics available."
        )
        return

    st.dataframe(
        df.assign(
            Rate=df["Rate"].map(
                lambda value: f"{value:.2%}"
            )
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_evaluation_details(
    results: list[dict],
):
    """Display per-question evaluation results."""

    st.subheader(
        "🧪 Individual Evaluations"
    )

    for index, result in enumerate(
        results,
        1,
    ):

        question = result.get(
            "question",
            f"Question {index}",
        )

        scores = result.get(
            "scores",
            {},
        )

        reasoning = result.get(
            "reasoning",
            {},
        )

        tool_selection = result.get(
            "tool_selection",
            {},
        )

        correctness = scores.get(
            "correctness"
        )

        groundedness = scores.get(
            "groundedness"
        )

        context_relevance = scores.get(
            "context_relevance"
        )

        with st.expander(
            f"{index}. {question}"
        ):

            # ------------------------------------------
            # Answer
            # ------------------------------------------

            st.markdown(
                "### 🤖 Agent Answer"
            )

            st.write(
                result.get(
                    "agent_answer",
                    "No answer available.",
                )
            )

            # ------------------------------------------
            # Ground truth
            # ------------------------------------------

            with st.expander(
                "Expected Answer"
            ):

                st.write(
                    result.get(
                        "expected_output",
                        "No ground truth available.",
                    )
                )

            st.divider()

            # ------------------------------------------
            # Scores
            # ------------------------------------------

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Correctness",
                    (
                        f"{correctness} / 5"
                        if correctness
                        is not None
                        else "N/A"
                    ),
                )

            with col2:

                st.metric(
                    "Groundedness",
                    (
                        f"{groundedness} / 5"
                        if groundedness
                        is not None
                        else "N/A"
                    ),
                )

            with col3:

                st.metric(
                    "Context Relevance",
                    (
                        f"{context_relevance} / 5"
                        if context_relevance
                        is not None
                        else "N/A"
                    ),
                )

            st.markdown(
                "### 🧭 Tool Selection"
            )

            expected_tool = tool_selection.get(
                "expected_tool",
                "N/A",
            )

            actual_tools = tool_selection.get(
                "actual_tools",
                [],
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Expected Tool",
                    expected_tool,
                )

            with col2:
                st.metric(
                    "Actual Tools",
                    (
                        ", ".join(actual_tools)
                        if actual_tools
                        else "None"
                    ),
                )

            with col3:
                correct = tool_selection.get(
                    "correct"
                )

                st.metric(
                    "Correct",
                    (
                        "Yes"
                        if correct is True
                        else "No"
                        if correct is False
                        else "N/A"
                    ),
                )

            # ------------------------------------------
            # Judge reasoning
            # ------------------------------------------

            st.markdown(
                "### 🧑‍⚖️ Judge Reasoning"
            )

            st.markdown(
                "**Correctness**"
            )

            st.write(
                reasoning.get(
                    "correctness",
                    "No reasoning available.",
                )
            )

            st.markdown(
                "**Groundedness**"
            )

            st.write(
                reasoning.get(
                    "groundedness",
                    "No reasoning available.",
                )
            )

            st.markdown(
                "**Context Relevance**"
            )

            st.write(
                reasoning.get(
                    "context_relevance",
                    "No reasoning available.",
                )
            )

            tool_reasoning = reasoning.get(
                "tool_selection",
                {},
            )

            if tool_reasoning:
                st.markdown(
                    "**Tool Selection**"
                )

                st.write(
                    tool_reasoning.get(
                        "reason",
                        "No reasoning available.",
                    )
                )


def render_evaluation():
    """Render the complete evaluation page."""

    st.title(
        "📊 Evaluation"
    )

    st.caption(
        "Evaluation of the Knowledge Copilot "
        "using deterministic retrieval metrics "
        "and LLM-as-judge metrics."
    )

    results = load_evaluation_results()

    if not results:

        st.warning(
            "No evaluation results found."
        )

        st.info(
            "Run the evaluation pipeline first "
            "to generate data/results/llm_eval_report.json."
        )

        return

    metrics = calculate_metrics(
        results
    )

    # Top-level metrics
    render_metric_cards(
        metrics
    )

    st.divider()

    # Score distributions
    render_score_distribution(
        results
    )

    st.divider()

    # Tool selection summary
    render_tool_selection_summary(
        metrics
    )

    st.divider()

    # Individual evaluations
    render_evaluation_details(
        results
    )
