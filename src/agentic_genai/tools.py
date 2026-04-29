from __future__ import annotations

from crewai.tools import BaseTool
from duckduckgo_search import DDGS


def search_web(query: str, max_results: int = 5) -> str:
    results = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            title = item.get("title", "Untitled")
            href = item.get("href", "")
            body = item.get("body", "")
            results.append(f"Title: {title}\nLink: {href}\nSnippet: {body}")

    if not results:
        return "No search results found."

    return "\n\n".join(results)


class DuckDuckGoSearchTool(BaseTool):
    name: str = "duckduckgo_search"
    description: str = (
        "Search the web for recent and reliable information about a topic. "
        "Input should be a concise search query."
    )

    def _run(self, query: str) -> str:
        return search_web(query=query, max_results=5)
