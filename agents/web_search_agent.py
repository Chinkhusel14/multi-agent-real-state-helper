import pandas as pd
from tavily import TavilyClient

def search_tavily(query, api_key):
    client = TavilyClient(api_key)
    response = client.search(
        query=query,
        max_results=30,
        include_domains=["www.unegui.mn"]
    )
    return response

def tavily_data(query):
    TAVILY_API_KEY = "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"

    search_results = search_tavily(query, TAVILY_API_KEY)

    apartments = []
    for result in search_results.get('results', []):
        title = result.get('title', 'No title')
        content = result.get('content', 'No content')
        url = result.get('url', 'No URL')

        apartments.append({
            'title': title,
            'content': content,
            'url': url
        })

    return apartments