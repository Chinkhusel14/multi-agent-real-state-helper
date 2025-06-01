from agents.unegui_agent import crawl_listings
from agents.faiss_agent import FAISSAgent
from agents.chain_of_thought import analyze_apartments
from agents.web_search_agent import tavily_data
from dotenv import load_dotenv
load_dotenv()

query = 'Зайсанд 100 m2 аас бага байр'
# 1. Crawl listings (deep mode)
listings = crawl_listings(pages=3)

# 2. Create agent instance
agent = FAISSAgent(name="UneguiAgent", max_pages=3)

# 3. Build FAISS index
agent.build_faiss_index(listings)

# 4. Example search
results = agent.search_faiss("Баянзүрх дүүрэгт 2 өрөө байр")
for r in results:
    print(r.page_content)

# 5. Web search
web_data = tavily_data(query=query)

# 6. Chain of thought
data = analyze_apartments(query,listings)