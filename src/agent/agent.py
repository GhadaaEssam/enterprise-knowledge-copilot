# src/agent/agent.py

import json
import logging
import time
from typing import Any

from src.agent.prompt import SYSTEM_INSTRUCTIONS
from src.monitoring.pricing import calculate_cost

logger = logging.getLogger(__name__)


class KnowledgeAgent:

    def __init__(
        self,
        tool_registry,
        llm_client,
        model: str = "openai/gpt-oss-20b",
        instructions: str = SYSTEM_INSTRUCTIONS,
        max_iterations: int = 4,
        tracker=None,
    ):
        self.tool_registry = tool_registry
        self.llm_client = llm_client
        self.model = model
        self.instructions = instructions
        self.max_iterations = max_iterations
        self.tracker = tracker

        self.messages: list[dict] = []

    def ask(
        self,
        question: str,
        clear_history: bool = True,
    ) -> dict[str, Any]:

        request_start = time.perf_counter()

        request_id = None

        if self.tracker:
            request_id = self.tracker.start_request(
                question=question,
                model=self.model,
            )

        if clear_history:
            self.messages = [
                {
                    "role": "system",
                    "content": self.instructions,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ]
        else:
            self.messages.append(
                {
                    "role": "user",
                    "content": question,
                }
            )

        tool_call_log: list[dict] = []

        iteration = 0
        final_answer = ""
        stop_reason = "completed"

        total_input_tokens = 0
        total_output_tokens = 0
        total_tokens = 0
        total_cost = 0.0

        while True:

            iteration += 1

            if iteration > self.max_iterations:

                final_answer = (
                    "I wasn't able to reach a confident answer "
                    "within the allowed number of steps. "
                    "Please try rephrasing your question."
                )

                stop_reason = "max_iterations"

                logger.warning(
                    "KnowledgeAgent hit max_iterations=%s "
                    "for question=%r",
                    self.max_iterations,
                    question,
                )

                break

            # LLM CALL
            llm_start = time.perf_counter()
            try:
                response = (
                    self.llm_client
                    .chat
                    .completions
                    .create(
                        model=self.model,
                        messages=self.messages,
                        tools=self.tool_registry.get_schemas(),
                        tool_choice="auto",
                    )
                )

            except Exception as e:
                logger.exception(
                    "LLM call failed on iteration %s",
                    iteration,
                )
                final_answer = (
                    "The assistant hit an internal error "
                    "and could not complete the request."
                )
                stop_reason = "llm_error"
                break

            llm_duration_ms = (
                time.perf_counter() - llm_start
            ) * 1000

            # TOKEN USAGE

            usage = getattr(response, "usage", None)

            input_tokens = getattr(
                usage,
                "prompt_tokens",
                0,
            ) or 0

            output_tokens = getattr(
                usage,
                "completion_tokens",
                0,
            ) or 0

            call_total_tokens = getattr(
                usage,
                "total_tokens",
                0,
            ) or 0

            call_cost = calculate_cost(
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_tokens += call_total_tokens
            total_cost += call_cost

            # SAVE LLM TELEMETRY

            if self.tracker and request_id:

                self.tracker.record_llm_call(
                    request_id=request_id,
                    iteration=iteration,
                    model=self.model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=call_total_tokens,
                    duration_ms=llm_duration_ms,
                    estimated_cost=call_cost,
                )

            response_message = response.choices[0].message

            # NORMALIZE ASSISTANT MESSAGE

            assistant_entry = {
                "role": "assistant",
                "content": response_message.content,
            }

            if response_message.tool_calls:

                assistant_entry["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in response_message.tool_calls
                ]

            self.messages.append(assistant_entry)

            tool_calls = response_message.tool_calls

            # ------------------------------------------
            # TOOL CALLS
            # ------------------------------------------

            if tool_calls:

                for tool_call in tool_calls:

                    function_name = (
                        tool_call.function.name
                    )

                    raw_args = (
                        tool_call.function.arguments
                    )

                    try:
                        function_args = json.loads(raw_args)

                    except json.JSONDecodeError as e:

                        tool_output = (
                            f"Error: could not parse arguments "
                            f"for {function_name}: {e}"
                        )

                        function_args = None

                        tool_success = False

                    else:

                        tool_start = time.perf_counter()

                        try:

                            tool_output = (
                                self.tool_registry.execute(
                                    function_name,
                                    **function_args,
                                )
                            )

                            tool_success = True

                        except Exception as e:

                            logger.exception(
                                "Tool execution failed: %s(%s)",
                                function_name,
                                function_args,
                            )

                            tool_output = (
                                f"Error executing "
                                f"{function_name}: {e}"
                            )

                            tool_success = False

                        tool_duration_ms = (
                            time.perf_counter()
                            - tool_start
                        ) * 1000

                    if function_args is None:
                        tool_duration_ms = 0.0

                    query = ""

                    if function_args:
                        query = function_args.get(
                            "query",
                            "",
                        )

                    # TOOL TELEMETRY
                    if self.tracker and request_id:

                        self.tracker.record_tool_call(
                            request_id=request_id,
                            iteration=iteration,
                            tool_name=function_name,
                            query=query,
                            duration_ms=tool_duration_ms,
                            success=tool_success,
                            result_size=len(
                                str(tool_output)
                            ),
                        )

                    tool_call_log.append(
                        {
                            "iteration": iteration,
                            "name": function_name,
                            "arguments": function_args,
                            "output": tool_output,
                        }
                    )

                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": str(
                                tool_output
                            ),
                        }
                    )

                continue

            # FINAL ANSWER
            final_answer = (
                response_message.content or ""
            )

            break

        # ----------------------------------------------
        # REQUEST FINISHED
        # ----------------------------------------------

        response_time_ms = (
            time.perf_counter()
            - request_start
        ) * 1000

        status = (
            "success"
            if stop_reason == "completed"
            else "error"
        )

        if self.tracker and request_id:

            self.tracker.finish_request(
                request_id=request_id,
                answer=final_answer,
                response_time_ms=response_time_ms,
                iterations=iteration,
                stop_reason=stop_reason,
                status=status,
                total_input_tokens=total_input_tokens,
                total_output_tokens=total_output_tokens,
                total_tokens=total_tokens,
                estimated_cost=total_cost,
            )

        # ----------------------------------------------
        # RETURN
        # ----------------------------------------------

        return {
            "answer": final_answer,
            "messages": self.messages,
            "tool_calls": tool_call_log,
            "iterations": iteration,
            "stop_reason": stop_reason,

            "request_id": request_id,
            "metrics": {
                "response_time_ms": round(
                    response_time_ms,
                    2,
                ),
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "total_tokens": total_tokens,
                "estimated_cost": total_cost,
            },
        }