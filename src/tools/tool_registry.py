"""src/tools/tool_registry.py"""

from typing import Any, Callable, Dict, List


INTERNAL_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_internal_documentation",
        "description": "Searches internal company documentation, technical guides, standards, and private knowledge bases.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keywords or specific question to search within internal documentation.",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of documentation chunks to retrieve (default: 5).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}


WEB_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Searches the live public internet for recent information, external news, public facts, or general knowledge.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up on the web.",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of web search results to retrieve (default: 5).",
                    "default": 5,
                },
            },
            "required": ["query"],
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