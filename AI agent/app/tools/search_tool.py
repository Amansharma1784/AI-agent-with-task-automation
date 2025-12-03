import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("Missing Tavily API Key in .env file")

tavily = TavilyClient(api_key=TAVILY_API_KEY)

def web_search(query: str):

    """
    Real web search using Tavily API.
    Returns the top relevant web pages with metadata and links.
    """
    result = tavily.search(
        query=query,
        max_results=5,
        include_images=False,
        include_answer=True
    )
    # print("--------",result)
    return {
        "query": query,
        "results": result.get("results", []),
        "answer": result.get("answer", None),
        "sources": [item.get("url") for item in result.get("results", [])]
    }
