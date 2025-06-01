import pandas as pd
from tavily import TavilyClient

def search_tavily(query, api_key):
    client = TavilyClient(api_key)
    response = client.search(
        query=query,
        include_domains=["www.unegui.mn"]
    )
    return response

def main():
    TAVILY_API_KEY = "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"
    query = "Зайсанд 100 m2 аас бага байр"
    
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

    if apartments:
        pd.DataFrame(apartments).to_excel("apartments.xlsx", index=False)

if __name__ == "__main__":
    main()
