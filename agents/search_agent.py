import os
from typing import Dict, List
from tavily import TavilyClient

class SearchAgent:
    """
    A class responsible for performing web searches using the Tavily API.
    It allows searching for information and retrieving relevant web page content.
    """

    def __init__(self):
        """
        Initializes the SearchAgent and sets up the TavilyClient.
        It expects the Tavily API key to be provided.
        """
        self.client = TavilyClient(api_key="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")
        
    def search_web(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Performs a web search using the Tavily API for a given query.

        Args:
            query (str): The search query string.
            max_results (int): The maximum number of search results to retrieve. Defaults to 3.

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary contains the 'url',
                        'content', and 'title' of a search result.
                        Example: [{"url": "...", "content": "...", "title": "..."}, ...]
        """
        try:
            response = self.client.search(query=query, search_depth="basic", max_results=max_results)
            
            results = []
            if response and "results" in response:
                for r in response["results"]:
                    title = r.get("title", "No Title") 
                    url = r.get("url")
                    content = r.get("content")

                    if url and content: 
                        results.append({"title": title, "url": url, "content": content})
            
            print(f"Web search for '{query}' completed. Found {len(results)} results.")
            return results
        except Exception as e:
            print(f"Error during web search: {e}")
            return []