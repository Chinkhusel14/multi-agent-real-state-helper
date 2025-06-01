from agents.unegui_agent import crawl_listings
from agents.faiss_agent import FAISSAgent

from dotenv import load_dotenv
load_dotenv()

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
