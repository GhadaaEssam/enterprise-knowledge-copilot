"""src/evaluation/judge.py

LLM-as-judge scoring functions plus deterministic agent-routing checks.

Metrics:
1. correctness        - LLM judged against ground truth
2. groundedness       - LLM judged against retrieved context
3. context_relevance  - LLM judged: is the retrieved context relevant
                         to the user's question?
4. tool_selection     - deterministic: all evaluation questions come
                         from internal documentation, so the expected
                         tool is search_internal_documentation.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from src.evaluation.judge_prompts import (
    CONTEXT_RELEVANCE_JUDGE_PROMPT,
    GROUNDEDNESS_JUDGE_PROMPT,
    CORRECTNESS_JUDGE_PROMPT,
)

logger = logging.getLogger(__name__)

INTERNAL_TOOL_NAME = "search_internal_documentation"
WEB_TOOL_NAME = "search_web"


@dataclass
class JudgeResult:
    axis: str
    score: Optional[int]
    reasoning: str
    raw_response: str = field(repr=False, default="")


# ============================================================
# Robust JSON parsing
# ============================================================

def _extract_json_object(text: str) -> Optional[str]:
    """Extract the first balanced JSON object from model output."""

    if not text:
        return None

    text = text.strip()

    # Remove Markdown fences
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    start = text.find("{")

    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for i in range(start, len(text)):

        char = text[i]

        if in_string:

            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == '"':
                in_string = False

            continue

        if char == '"':
            in_string = True

        elif char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:
                return text[start : i + 1]

    return None


def _repair_json(raw: str) -> Optional[dict[str, Any]]:
    """Try several increasingly tolerant strategies to parse judge output."""

    if not raw:
        return None

    candidate = _extract_json_object(raw)

    if candidate is None:
        return None

    # Strict JSON
    try:
        parsed = json.loads(candidate)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # Repair invalid backslashes
    repaired = re.sub(
        r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})',
        r"\\\\",
        candidate,
    )

    try:
        parsed = json.loads(repaired)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # Raw decoder
    try:
        decoder = json.JSONDecoder()
        parsed, _ = decoder.raw_decode(repaired)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # Last-resort score extraction
    score_match = re.search(
        r'"score"\s*:\s*([1-5])',
        candidate,
        flags=re.IGNORECASE,
    )

    if score_match:

        reasoning_match = re.search(
            r'"reasoning"\s*:\s*"(.*)',
            candidate,
            flags=re.IGNORECASE | re.DOTALL,
        )

        reasoning = (
            reasoning_match.group(1).strip()
            if reasoning_match
            else "Reasoning could not be parsed."
        )

        reasoning = reasoning.rstrip("}")

        return {
            "score": int(score_match.group(1)),
            "reasoning": reasoning,
        }

    return None


def _validate_result(
    parsed: dict[str, Any],
    axis: str,
    raw: str,
) -> JudgeResult:
    """Validate the parsed judge response."""

    try:
        score = int(parsed["score"])

    except (
        KeyError,
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            f"Invalid or missing score: {exc}"
        ) from exc

    if not 1 <= score <= 5:
        raise ValueError(
            f"score out of range: {score}"
        )

    reasoning = str(
        parsed.get("reasoning", "")
    ).strip()

    return JudgeResult(
        axis=axis,
        score=score,
        reasoning=reasoning,
        raw_response=raw,
    )


# ============================================================
# LLM judge
# ============================================================

def _call_judge(
    llm_client,
    model: str,
    prompt: str,
    axis: str,
) -> JudgeResult:
    """Call the LLM judge and robustly parse its response."""

    def make_call(
        use_json_mode: bool = True,
    ) -> str:

        kwargs = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0,
        }

        if use_json_mode:
            kwargs["response_format"] = {
                "type": "json_object"
            }

        response = (
            llm_client
            .chat
            .completions
            .create(**kwargs)
        )

        return (
            response.choices[0]
            .message
            .content
            or ""
        )

    # --------------------------------------------------------
    # First attempt
    # --------------------------------------------------------

    try:

        try:
            raw = make_call(
                use_json_mode=True
            )

        except Exception as json_mode_error:

            logger.warning(
                "JSON mode failed for axis=%s, "
                "retrying without response_format: %s",
                axis,
                json_mode_error,
            )

            raw = make_call(
                use_json_mode=False
            )

    except Exception as e:

        logger.exception(
            "Judge call failed for axis=%s",
            axis,
        )

        return JudgeResult(
            axis=axis,
            score=None,
            reasoning=f"Judge call failed: {e}",
        )

    # --------------------------------------------------------
    # Parse response
    # --------------------------------------------------------

    parsed = _repair_json(raw)

    if parsed is not None:

        try:

            return _validate_result(
                parsed,
                axis,
                raw,
            )

        except ValueError as e:

            logger.warning(
                "Invalid judge result for axis=%s: %s | raw=%r",
                axis,
                e,
                raw,
            )

    # --------------------------------------------------------
    # Retry with explicit JSON instruction
    # --------------------------------------------------------

    retry_prompt = f"""
Return ONLY valid JSON.

Your previous response could not be parsed.

The required format is exactly:

{{
  "score": 1,
  "reasoning": "brief explanation"
}}

Rules:
- score must be an integer from 1 to 5
- reasoning must be a JSON string
- escape every backslash inside reasoning
- do not use Markdown
- do not add any text before or after the JSON

Original evaluation task:

{prompt}
"""

    try:

        try:
            retry_raw = make_call(
                use_json_mode=True
            )

        except Exception:

            retry_raw = make_call(
                use_json_mode=False
            )

    except Exception:

        logger.exception(
            "Judge retry failed for axis=%s",
            axis,
        )

        return JudgeResult(
            axis=axis,
            score=None,
            reasoning=(
                "Unparseable judge output: "
                f"{raw[:500]}"
            ),
            raw_response=raw,
        )

    retry_parsed = _repair_json(
        retry_raw
    )

    if retry_parsed is not None:

        try:

            return _validate_result(
                retry_parsed,
                axis,
                retry_raw,
            )

        except ValueError:
            pass

    logger.warning(
        "Failed to parse judge output for axis=%s "
        "after retry. Original raw=%r | Retry raw=%r",
        axis,
        raw,
        retry_raw,
    )

    return JudgeResult(
        axis=axis,
        score=None,
        reasoning=(
            "Unparseable judge output. "
            f"Raw response: {retry_raw[:500]}"
        ),
        raw_response=retry_raw,
    )


# ============================================================
# Deterministic tool selection
# ============================================================

def evaluate_tool_selection(
    tool_calls: list[dict],
) -> dict[str, Any]:
    """
    Deterministic tool-selection evaluation.

    All 100 evaluation questions were generated from internal
    documentation, so the expected source is always:

        search_internal_documentation

    No LLM call is needed.
    """

    tool_names = [
        tc.get("name")
        for tc in tool_calls
        if tc.get("name")
    ]

    internal_used = (
        INTERNAL_TOOL_NAME
        in tool_names
    )

    web_used = (
        WEB_TOOL_NAME
        in tool_names
    )

    no_tool_called = (
        len(tool_names) == 0
    )

    # Expected tool for every current evaluation case
    expected_tool = INTERNAL_TOOL_NAME

    correct = internal_used

    unnecessary_web_search = (
        web_used
        and internal_used
    )

    return {
        "expected_tool": expected_tool,
        "actual_tools": sorted(set(tool_names)),
        "internal_search_used": internal_used,
        "web_search_used": web_used,
        "no_tool_called": no_tool_called,
        "correct": correct,
        "unnecessary_web_search": unnecessary_web_search,
        "accuracy": 1.0 if correct else 0.0,
    }


# ============================================================
# Context relevance
# ============================================================

def judge_context_relevance(
    llm_client,
    judge_model: str,
    question: str,
    tool_calls: list[dict],
) -> JudgeResult:
    """
    Judge whether the retrieved context as a whole is relevant
    to the user's question.

    This is different from deterministic Hit Rate/MRR:
    retrieval evaluation measures whether the target chunk was
    retrieved, while this judge evaluates the usefulness of the
    context actually supplied to the LLM.
    """

    if not tool_calls:

        context = (
            "(no tools were called -- "
            "no retrieved context)"
        )

    else:

        context = "\n\n".join(
            (
                f"[{tc.get('name', 'unknown_tool')}]\n"
                f"{str(tc.get('output', ''))[:4000]}"
            )
            for tc in tool_calls
        )

    prompt = (
        CONTEXT_RELEVANCE_JUDGE_PROMPT.format(
            question=question,
            retrieved_context=context,
        )
    )

    return _call_judge(
        llm_client,
        judge_model,
        prompt,
        axis="context_relevance",
    )


# ============================================================
# Groundedness
# ============================================================

def judge_groundedness(
    llm_client,
    judge_model: str,
    answer: str,
    tool_calls: list[dict],
) -> JudgeResult:

    if not tool_calls:

        context = (
            "(no tools were called -- "
            "no retrieved context)"
        )

    else:

        context = "\n\n".join(
            (
                f"[{tc.get('name', 'unknown_tool')}]\n"
                f"{str(tc.get('output', ''))[:4000]}"
            )
            for tc in tool_calls
        )

    prompt = GROUNDEDNESS_JUDGE_PROMPT.format(
        retrieved_context=context,
        answer=answer,
    )

    return _call_judge(
        llm_client,
        judge_model,
        prompt,
        axis="groundedness",
    )


# ============================================================
# Correctness
# ============================================================

def judge_correctness(
    llm_client,
    judge_model: str,
    question: str,
    expected_output: str,
    agent_answer: str,
) -> JudgeResult:

    prompt = CORRECTNESS_JUDGE_PROMPT.format(
        question=question,
        expected_output=(
            expected_output
            or "(no ground truth text provided)"
        ),
        agent_answer=(
            agent_answer
            or "(agent produced no answer)"
        ),
    )

    return _call_judge(
        llm_client,
        judge_model,
        prompt,
        axis="correctness",
    )


# ============================================================
# Complete trajectory evaluation
# ============================================================

def judge_trajectory(
    llm_client,
    judge_model: str,
    question: str,
    trajectory: dict[str, Any],
) -> dict[str, Any]:
    """
    Evaluate one trajectory using:

    - correctness (LLM judge)
    - groundedness (LLM judge)
    - context relevance (LLM judge)
    - tool selection accuracy (deterministic)
    """

    answer = trajectory.get(
        "answer",
        "",
    )

    tool_calls = trajectory.get(
        "tool_calls",
        [],
    )

    correctness = judge_correctness(
        llm_client,
        judge_model,
        question,
        trajectory.get(
            "expected_output",
            "",
        ),
        answer,
    )

    groundedness = judge_groundedness(
        llm_client,
        judge_model,
        answer,
        tool_calls,
    )

    context_relevance = judge_context_relevance(
        llm_client,
        judge_model,
        question,
        tool_calls,
    )

    tool_selection = evaluate_tool_selection(
        tool_calls
    )

    return {
        "question": question,
        "answer": answer,
        "stop_reason": trajectory.get(
            "stop_reason"
        ),
        "iterations": trajectory.get(
            "iterations"
        ),

        "scores": {
            "correctness": correctness.score,
            "groundedness": groundedness.score,
            "context_relevance": (
                context_relevance.score
            ),
            "tool_selection_accuracy": (
                tool_selection["accuracy"]
            ),
        },

        "reasoning": {
            "correctness": correctness.reasoning,
            "groundedness": groundedness.reasoning,
            "context_relevance": (
                context_relevance.reasoning
            ),
            "tool_selection": {
                "expected_tool": (
                    tool_selection["expected_tool"]
                ),
                "actual_tools": (
                    tool_selection["actual_tools"]
                ),
                "reason": (
                    "Internal documentation was the "
                    "expected source for this evaluation "
                    "dataset."
                ),
            },
        },

        "tool_selection": tool_selection,
    }