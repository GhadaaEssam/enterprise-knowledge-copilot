"""src/evaluation/judge.py
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from src.evaluation.judge_prompts import (
    TOOL_SELECTION_JUDGE_PROMPT,
    RETRIEVAL_RELEVANCE_JUDGE_PROMPT,
    GROUNDEDNESS_JUDGE_PROMPT,
    HELPFULNESS_JUDGE_PROMPT,
    CORRECTNESS_JUDGE_PROMPT,
)

logger = logging.getLogger(__name__)


@dataclass
class JudgeResult:
    axis: str
    score: Optional[int]  # None if the judge call/parse failed
    reasoning: str
    raw_response: str = field(repr=False, default="")

def _extract_json_object(text: str) -> Optional[str]:
    """Extract the first balanced JSON object from model output.

    Handles output such as:

        Here is my evaluation:
        {"score": 4, "reasoning": "..."}
        Hope this helps.

    Also handles Markdown code fences.
    """

    text = text.strip()

    # Remove common Markdown fences.
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

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

    # Incomplete/truncated JSON.
    return None


def _repair_json(raw: str) -> Optional[dict[str, Any]]:
    """Try several increasingly tolerant strategies to parse judge output."""

    if not raw:
        return None

    candidate = _extract_json_object(raw)

    if candidate is None:
        return None

    # ---------------------------------------------------------------
    # Attempt 1: strict JSON
    # ---------------------------------------------------------------
    try:
        parsed = json.loads(candidate)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

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

    try:
        decoder = json.JSONDecoder()
        parsed, _ = decoder.raw_decode(repaired)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

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

        # Remove a likely trailing JSON delimiter.
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
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid or missing score: {exc}") from exc

    if not 1 <= score <= 5:
        raise ValueError(f"score out of range: {score}")

    reasoning = str(parsed.get("reasoning", "")).strip()

    return JudgeResult(
        axis=axis,
        score=score,
        reasoning=reasoning,
        raw_response=raw,
    )


def _call_judge(
    llm_client,
    model: str,
    prompt: str,
    axis: str,
) -> JudgeResult:
    """Call the LLM judge and robustly parse its response.
    """

    def make_call(use_json_mode: bool = True) -> str:
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
            kwargs["response_format"] = {"type": "json_object"}

        response = llm_client.chat.completions.create(**kwargs)

        return response.choices[0].message.content or ""

    try:
        try:
            raw = make_call(use_json_mode=True)

        except Exception as json_mode_error:
            logger.warning(
                "JSON mode failed for axis=%s, retrying without "
                "response_format: %s",
                axis,
                json_mode_error,
            )

            raw = make_call(use_json_mode=False)

    except Exception as e:
        logger.exception("Judge call failed for axis=%s", axis)

        return JudgeResult(
            axis=axis,
            score=None,
            reasoning=f"Judge call failed: {e}",
        )


    parsed = _repair_json(raw)

    if parsed is not None:
        try:
            return _validate_result(parsed, axis, raw)

        except ValueError as e:
            logger.warning(
                "Invalid judge result for axis=%s: %s | raw=%r",
                axis,
                e,
                raw,
            )


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
        retry_raw = make_call(use_json_mode=True)

    except Exception:
        try:
            retry_raw = make_call(use_json_mode=False)

        except Exception as e:
            logger.exception(
                "Judge retry failed for axis=%s",
                axis,
            )

            return JudgeResult(
                axis=axis,
                score=None,
                reasoning=f"Unparseable judge output: {raw[:500]}",
                raw_response=raw,
            )

    retry_parsed = _repair_json(retry_raw)

    if retry_parsed is not None:
        try:
            result = _validate_result(
                retry_parsed,
                axis,
                retry_raw,
            )

            logger.info(
                "Successfully recovered judge output on retry for axis=%s",
                axis,
            )

            return result

        except ValueError:
            pass

    logger.warning(
        "Failed to parse judge output for axis=%s after retry. "
        "Original raw=%r | Retry raw=%r",
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

def judge_tool_selection(
    llm_client,
    judge_model: str,
    question: str,
    tool_calls: list[dict],
) -> JudgeResult:

    if not tool_calls:
        summary = "(no tools were called)"

    else:
        summary = "\n".join(
            (
                f"{i + 1}. "
                f"{tc['name']}"
                f"(query="
                f"{tc['arguments'].get('query') if tc['arguments'] else 'PARSE_ERROR'!r}"
                f")"
            )
            for i, tc in enumerate(tool_calls)
        )

    prompt = TOOL_SELECTION_JUDGE_PROMPT.format(
        question=question,
        tool_calls_summary=summary,
    )

    return _call_judge(
        llm_client,
        judge_model,
        prompt,
        axis="tool_selection",
    )


def judge_retrieval_relevance(
    llm_client,
    judge_model: str,
    tool_call: dict,
) -> JudgeResult:

    query = (
        tool_call["arguments"].get("query", "")
        if tool_call["arguments"]
        else "(unparsed args)"
    )

    prompt = RETRIEVAL_RELEVANCE_JUDGE_PROMPT.format(
        query=query,
        tool_name=tool_call["name"],
        tool_output=str(tool_call["output"])[:4000],
    )

    return _call_judge(
        llm_client,
        judge_model,
        prompt,
        axis="retrieval_relevance",
    )


def judge_groundedness(
    llm_client,
    judge_model: str,
    answer: str,
    tool_calls: list[dict],
) -> JudgeResult:

    if not tool_calls:
        context = "(no tools were called -- no retrieved context)"

    else:
        context = "\n\n".join(
            f"[{tc['name']}]\n{str(tc['output'])[:4000]}"
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


def judge_helpfulness(
    llm_client,
    judge_model: str,
    question: str,
    answer: str,
) -> JudgeResult:

    prompt = HELPFULNESS_JUDGE_PROMPT.format(
        question=question,
        answer=answer,
    )

    return _call_judge(
        llm_client,
        judge_model,
        prompt,
        axis="helpfulness",
    )


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

def judge_trajectory(
    llm_client,
    judge_model: str,
    question: str,
    trajectory: dict[str, Any],
) -> dict[str, Any]:
    """Run all judges against one agent trajectory."""

    answer = trajectory["answer"]
    tool_calls = trajectory["tool_calls"]

    tool_selection = judge_tool_selection(
        llm_client,
        judge_model,
        question,
        tool_calls,
    )

    retrieval_scores = [
        judge_retrieval_relevance(
            llm_client,
            judge_model,
            tc,
        )
        for tc in tool_calls
    ]

    groundedness = judge_groundedness(
        llm_client,
        judge_model,
        answer,
        tool_calls,
    )

    helpfulness = judge_helpfulness(
        llm_client,
        judge_model,
        question,
        answer,
    )

    valid_retrieval = [
        r.score
        for r in retrieval_scores
        if r.score is not None
    ]

    avg_retrieval = (
        sum(valid_retrieval) / len(valid_retrieval)
        if valid_retrieval
        else None
    )

    return {
        "question": question,
        "answer": answer,
        "stop_reason": trajectory.get("stop_reason"),
        "iterations": trajectory.get("iterations"),
        "scores": {
            "tool_selection": tool_selection.score,
            "retrieval_relevance_avg": avg_retrieval,
            "groundedness": groundedness.score,
            "helpfulness": helpfulness.score,
        },
        "reasoning": {
            "tool_selection": tool_selection.reasoning,
            "retrieval_relevance": [
                {
                    "query": (
                        tc["arguments"].get("query")
                        if tc["arguments"]
                        else None
                    ),
                    "score": r.score,
                    "reasoning": r.reasoning,
                }
                for tc, r in zip(tool_calls, retrieval_scores)
            ],
            "groundedness": groundedness.reasoning,
            "helpfulness": helpfulness.reasoning,
        },
    }