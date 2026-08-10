# src/agent/agent.py
import json
import logging
from typing import Any

from src.agent.prompt import SYSTEM_INSTRUCTIONS

logger = logging.getLogger(__name__)


class KnowledgeAgent:

    def __init__(
        self,
        tool_registry,
        llm_client,
        model: str = "llama-3.1-8b-instant",
        instructions: str = SYSTEM_INSTRUCTIONS,
        max_iterations: int = 4,
    ):
        self.tool_registry = tool_registry
        self.llm_client = llm_client
        self.model = model
        self.instructions = instructions
        self.max_iterations = max_iterations
        self.messages: list[dict] = []  # Stores full conversation & tool interaction history

    def ask(self, question: str, clear_history: bool = True) -> dict[str, Any]:
        """Executes the agent loop, records tool interactions in self.messages,
        and returns the final answer along with the full trajectory (needed
        for eval: which tools were called, with what args, and what came back).
        """
        if clear_history:
            self.messages = [
                {"role": "system", "content": self.instructions},
                {"role": "user", "content": question},
            ]
        else:
            self.messages.append({"role": "user", "content": question})

        tool_call_log: list[dict] = []
        iteration = 0
        final_answer = ""
        stop_reason = "completed"

        while True:
            iteration += 1

            if iteration > self.max_iterations:
                final_answer = (
                    "I wasn't able to reach a confident answer within the "
                    "allowed number of steps. Please try rephrasing your question."
                )
                stop_reason = "max_iterations"
                logger.warning(
                    "KnowledgeAgent hit max_iterations=%s for question=%r",
                    self.max_iterations,
                    question,
                )
                break

            try:
                response = self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.tool_registry.get_schemas(),
                    tool_choice="auto",
                )
            except Exception as e:
                logger.exception("LLM call failed on iteration %s", iteration)
                final_answer = f"The assistant hit an internal error and could not complete the request: {e}"
                stop_reason = "llm_error"
                break

            response_message = response.choices[0].message

            # Normalize to a plain dict before storing. Two problems with
            # storing the raw SDK object or a full model_dump():
            #   1. It won't survive json.dumps() cleanly for logging/eval traces.
            #   2. Provider response objects can include OUTPUT-only fields
            #      (e.g. Groq/OpenAI-schema "annotations") that the same
            #      provider's endpoint then REJECTS when echoed back as
            #      input on the next turn ("property 'annotations' is
            #      unsupported"). Only role/content/tool_calls are valid
            #      as input, so build the dict explicitly rather than
            #      dumping everything the SDK gave us.
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
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    raw_args = tool_call.function.arguments

                    try:
                        function_args = json.loads(raw_args)
                    except json.JSONDecodeError as e:
                        tool_output = f"Error: could not parse arguments for {function_name}: {e}"
                        function_args = None
                    else:
                        try:
                            tool_output = self.tool_registry.execute(
                                function_name, **function_args
                            )
                        except Exception as e:
                            logger.exception(
                                "Tool execution failed: %s(%s)", function_name, function_args
                            )
                            tool_output = f"Error executing {function_name}: {e}"

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
                            "content": str(tool_output),
                        }
                    )
                # loop again so the model can see the tool results
                continue

            # No tool call requested -> final answer reached
            final_answer = response_message.content or ""
            break

        return {
            "answer": final_answer,
            "messages": self.messages,
            "tool_calls": tool_call_log,
            "iterations": iteration,
            "stop_reason": stop_reason,
        }