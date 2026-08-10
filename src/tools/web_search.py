"""src/tools/web_search.py"""

import logging
from typing import Any, Dict, List, Optional
from ddgs import DDGS

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Tool for executing web searches via DuckDuckGo."""

    def __init__(self, max_results: int = 5, region: str = "wt-wt"):
        """
        Initialize the web search tool.
        
        Args:
            max_results: Default maximum number of search results to return.
            region: Search region code (e.g., 'wt-wt' for worldwide, 'us-en', 'uk-en').
        """
        self.max_results = max_results
        self.region = region

    def search(
        self,
        query: str,
        num_results: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Execute web search query.

        Args:
            query: The search term or question.
            num_results: Optional override for maximum search results.

        Returns:
            List of dictionaries containing title, href, and body/snippet.
        """
        limit = num_results if num_results is not None else self.max_results
        results: List[Dict[str, Any]] = []

        try:
            with DDGS() as ddgs:
                ddg_results = list(
                    ddgs.text(
                        query,
                        region=self.region,
                        max_results=limit,
                    )
                )

            for doc in ddg_results:
                results.append(
                    {
                        "title": doc.get("title", "Untitled"),
                        "source": doc.get("href", "N/A"),
                        "text": doc.get("body", ""),
                    }
                )

        except Exception as e:
            logger.error(f"Error executing web search for query '{query}': {e}")
            return []

        return results

    def format_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Formats raw web search results into a clean string for the LLM context.

        Args:
            search_results: List of result dictionaries from search().

        Returns:
            Formatted string of external web documents.
        """
        if not search_results:
            return "No relevant web search results found."

        sections = []
        for i, doc in enumerate(search_results, 1):
            title = doc.get("title", "Untitled")
            source = doc.get("source", "N/A")
            text = doc.get("text", "")

            sections.append(
                f"[{i}] Web Document: {title}\nURL: {source}\nContent:\n{text}"
            )

        return "\n\n---\n\n".join(sections)