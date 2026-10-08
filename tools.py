from langchain.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv
import logging
import os

#configuration for logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s|%(levelname)s|%(message)s",
)

load_dotenv()

@tool
def web_search(topic: str) -> str:
    """Search the web for a given topic and return relevant results."""

    logging.info("Searching the web for topic: %s", topic)
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY is not configured.")

    response = TavilyClient(api_key=api_key).search(topic)
    return str(response)
