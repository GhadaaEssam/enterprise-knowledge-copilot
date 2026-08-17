"""src/tools/tool_registry.py"""

from typing import Any, Callable, Dict, List


INTERNAL_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_internal_documentation",
        "description": (
            "PRIMARY knowledge source. Searches the company's internal "
            "documentation, engineering guides, standards, processes, "
            "technical documentation, and private knowledge base. "
            "Use this tool FIRST for questions that may be answered "
            "by internal documentation. Prefer this tool over web search "
            "when the answer may exist in the company's documentation."
        ),       
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Keywords or a specific question "
                        "to search within internal documentation."
                    ),
                },
                "num_results": {
                    "type": "integer",
                    "description": (
                        "Optional number of results to return. "
                        "Defaults to 5."
                    ),
                },
            },
            "required": [],
        },
    },
}

WEB_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": (
            "SECONDARY knowledge source. Searches the public internet "
            "for current or external information. Use ONLY when the user "
            "explicitly requests web information, when current information "
            "is required, or when internal documentation does not contain "
            "enough information to answer the question."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Keywords or a specific question "
                        "to search on the web."
                    ),
                },
                "num_results": {
                    "type": "integer",
                    "description": (
                        "Optional number of results to return. "
                        "Defaults to 5."
                    ),
                },
            },
            "required": [],
        },
    },
}

class ToolRegistry:

    def __init__(self):
        self._schemas: List[Dict[str, Any]] = []
        self._handlers: Dict[str, Callable] = {}

    def register(self, schema: Dict[str, Any], handler: Callable) -> None:
        """Registers a tool's JSON schema alongside its executable Python function."""
        tool_name = schema["function"]["name"]
        self._schemas.append(schema)
        self._handlers[tool_name] = handler

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Returns all registered tool schemas to pass into the LLM."""
        return self._schemas

    def execute(self, tool_name: str, **kwargs) -> Any:
        """Executes the Python handler registered for a given tool name."""
        if tool_name not in self._handlers:
            raise ValueError(f"Tool '{tool_name}' is not registered.")

        return self._handlers[tool_name](**kwargs)
