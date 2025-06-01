# main.py
# from dotenv import load_dotenv # Keep this if you use .env for other things, otherwise remove
from agents.unegui_agent import UneguiAgent
from agents.faiss_agent import FAISSAgent
from agents.grouping_agent import GroupingAgent
from agents.analysis_agent import AnalysisAgent
from agents.report_agent import ReportAgent
from agents.search_agent import SearchAgent
import os

def main():
    """
    This is the main function that orchestrates the entire real estate market analysis workflow.
    It performs the following steps:
    1. Crawls real estate listings from unegui.mn.
    2. Builds a FAISS index for efficient similarity search on the listings.
    3. Groups the crawled listings based on various criteria (e.g., district, price range).
    4. Analyzes each main category (5 groups) to extract insights like average price, common features, and summaries.
    5. Performs a FAISS search for a specific "group" of listings and analyzes it.
    6. Searches the web for additional real estate market trends as references.
    7. Generates a comprehensive PDF report summarizing the findings.
    """
    
    # --- 1. Crawl listings ---
    print("Crawling listings from unegui.mn...")
    unegui_agent = UneguiAgent()
    listings = unegui_agent.crawl_listings(pages=3)
    print(f"Found {len(listings)} listings")
    
    # --- 2. FAISS index creation and general search ---
    print("Creating FAISS index...")
    faiss_agent = FAISSAgent(name="UneguiAgent", max_pages=3)
    faiss_agent.build_faiss_index(listings)
    
    # General FAISS search example (will be displayed in its own section)
    faiss_general_query = "Баянзүрх дүүрэгт 2 өрөө байр" 
    # Extract metadata from Document objects for general results display
    faiss_general_results_docs = faiss_agent.search_faiss(faiss_general_query)
    faiss_general_results = [doc.metadata for doc in faiss_general_results_docs]
    print(f"Found {len(faiss_general_results)} general similar listings for the query: '{faiss_general_query}'.")
    
    # --- 3. Group listings by predefined categories ---
    print("Grouping listings by predefined categories...")
    grouping_agent = GroupingAgent()
    grouped_data = grouping_agent.group_properties(listings)
    print(f"Listings grouped into {len(grouped_data)} main categories.")
    
    # --- 4. Analyze main categories ---
    print("Analyzing main categories...")
    analysis_agent = AnalysisAgent()
    analyses = []
    
    for category_name, sub_groups_dict in grouped_data.items():
        print(f"  Analyzing overall category: {category_name.replace('_', ' ').title()}")
        overall_analysis = analysis_agent.analyze_overall_category(category_name, sub_groups_dict)
        analyses.append(overall_analysis)
    
    print(f"Completed analysis for {len(analyses)} main categories.")

    # --- 5. FAISS-Derived Group Analysis (One Group as requested) ---
    print("\nPerforming FAISS-derived group analysis (one group)...")
    faiss_group_query = "Тансаг зэрэглэлийн 4 өрөө байр Хан-Уул дүүрэгт" # Specific query for a FAISS-derived group
    faiss_grouped_listings_docs = faiss_agent.search_faiss(faiss_group_query)
    
    # IMPORTANT: Extract the original listing dictionaries from the Document objects' metadata
    faiss_grouped_listings = [doc.metadata for doc in faiss_grouped_listings_docs]

    print(f"Found {len(faiss_grouped_listings)} listings for FAISS-derived group: '{faiss_group_query}'.")

    if faiss_grouped_listings:
        # Analyze this specific FAISS-derived group
        faiss_group_analysis = analysis_agent.analyze_group(
            f"FAISS-аас үүссэн бүлэг: '{faiss_group_query}'", # Unique name for this analysis
            faiss_grouped_listings # Pass the list of dictionaries
        )
        analyses.append(faiss_group_analysis)
        print(f"Analysis added for FAISS-derived group: '{faiss_group_query}'.")
    else:
        print(f"No listings found for FAISS-derived group: '{faiss_group_query}'. Skipping analysis.")
    
    # --- 6. Search for web references ---
    print("Searching for web references...")
    search_agent = SearchAgent()
    web_references = search_agent.search_web("Баянзүрх дүүрэгт 2 өрөө байр")
    print(f"Found {len(web_references)} web references.")
    
    # --- 7. Generate report ---
    print("Generating report...")
    report_agent = ReportAgent()
    # Pass faiss_general_results and its query to generate_pdf
    report_filename = report_agent.generate_pdf(
        grouped_data, 
        analyses, 
        web_references, 
        faiss_results={'query': faiss_general_query, 'results': faiss_general_results}
    )
    
    print(f"Report generated: {report_filename}")

if __name__ == "__main__":
    main()