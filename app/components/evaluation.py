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
        / "eval_data"
        / "eval_report.json"
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

    col1, col2 = st.columns(2)

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

        retrieval = result.get(
            "retrieval",
            {},
        )

        reasoning = result.get(
            "reasoning",
            {},
        )

        correctness = scores.get(
            "correctness"
        )

        groundedness = scores.get(
            "groundedness"
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
            "to generate eval_data/eval_report.json."
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

    # Individual evaluations
    render_evaluation_details(
        results
    )