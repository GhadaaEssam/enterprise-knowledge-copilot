"""src/tools/handlers.py

Thin adapter functions matching the JSON schemas in tool_registry.py
(query, num_results) to the actual tool classes. These are what get
registered with ToolRegistry and what the LLM's tool_calls ultimately
invoke.

Each handler returns the FORMATTED STRING (via format_context) that goes
straight into the tool message content the LLM sees -- not the raw dict
list. Keep the raw-vs-formatted distinction in mind if you need
structured data (e.g. chunk_id) downstream for eval: it must be present
in the formatted string too, since that's all agent.py logs in
tool_calls[i]["output"].
"""

from src.tools.internal_search import InternalSearchTool
from src.tools.web_search import WebSearchTool

# Instantiate once at import time -- both tools hold open resources
# (DB connection / DDGS session per call) that are cheap to reuse across
# calls within a process.
_internal_tool = InternalSearchTool()
_web_tool = WebSearchTool()


def search_internal_documentation(query: str, num_results: int = 5) -> str:
    results = _internal_tool.search(query=query, num_results=num_results)
    return _internal_tool.format_context(results)


def search_web(query: str, num_results: int = 5) -> str:
    results = _web_tool.search(query=query, num_results=num_results)
    return _web_tool.format_context(results)