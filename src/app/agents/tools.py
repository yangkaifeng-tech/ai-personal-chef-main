from langchain_tavily import TavilySearch

from app.core.config import settings


def create_web_search_tool() -> TavilySearch:
    """Create the recipe search tool used by the personal chef agent."""
    return TavilySearch(
        max_results=settings.search.max_results,
        topic=settings.search.topic,
    )
