import os
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from pydantic import BaseModel, Field
from readability import Document
import trafilatura
from tavily import TavilyClient

load_dotenv()

# 1. Initialize client globally to reuse connection pools
TAVILY_CLIENT = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# 2. Define strict schemas for LLM tool inputs
class WebSearchInput(BaseModel):
    query: str = Field(..., description="The search query to look up on the web.")

class ScrapeWebInput(BaseModel):
    url: str = Field(..., description="The fully qualified URL to scrape (e.g., https://example.com).")


@tool("web_search", args_schema=WebSearchInput)
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs, and snippets."""
    try:
        results = TAVILY_CLIENT.search(query=query, max_results=5)
        
        # Handle empty results gracefully
        if not results.get('results'):
            return "No results found for the query."

        out = [
            f"Title: {r.get('title', 'No Title')}\nURL: {r.get('url', '')}\nSnippet: {r.get('content', '')[:300]}"
            for r in results['results']
        ]
        return "\n----\n".join(out)
        
    except Exception as e:
        return f"Search API error: {str(e)}"


@tool("scrape_web", args_schema=ScrapeWebInput)
def scrape_web(url: str) -> str:
    """Scrape and extract clean readable content from a URL using multiple extraction strategies."""
    
    # Validate URL structure to prevent SSRF or crash loops
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return f"Invalid URL format: {url}. Please provide a fully qualified URL starting with http:// or https://."

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        # Guard against downloading large binaries or PDFs
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' not in content_type and 'text/plain' not in content_type:
            return f"Unsupported content type: {content_type}. Can only scrape HTML or text web pages."

        html = response.text

        # Strategy 1: Trafilatura
        extracted = trafilatura.extract(html, include_comments=False, include_tables=False)
        if extracted and len(extracted.strip()) > 200:
            return re.sub(r'\s+', ' ', extracted)[:5000]

        # Strategy 2: Readability
        doc = Document(html)
        soup = BeautifulSoup(doc.summary(), "html.parser")
        
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
            
        text = soup.get_text(separator=" ", strip=True)
        if text and len(text.strip()) > 200:
            return re.sub(r'\s+', ' ', text)[:5000]

        # Strategy 3: Fallback full page extraction
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
            
        text = soup.get_text(separator=" ", strip=True)
        cleaned = re.sub(r'\s+', ' ', text)
        
        return cleaned[:5000] if cleaned else "Could not extract meaningful content from the page."

    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."
    except requests.exceptions.RequestException as e:
        return f"Network or HTTP error occurred: {str(e)}"
    except Exception as e:
        return f"Unexpected error during scraping: {str(e)}"