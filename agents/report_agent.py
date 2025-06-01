from fpdf import FPDF
from datetime import datetime
from typing import Dict, List, Any
import os
import unicodedata

class ReportAgent:
    """
    A class responsible for generating a PDF report of real estate market analysis.
    It takes grouped data and analysis results to produce a structured and readable PDF document.
    """

    def __init__(self):
        """
        Initializes the ReportAgent, setting up paths to required font files.
        It expects 'NotoSans-Regular.ttf', 'NotoSans-Bold.ttf', and 'NotoSans-Italic.ttf'
        to be present in a 'font' directory relative to the agent's script location.
        """
        # Determine the directory where this script is located
        script_dir = os.path.dirname(__file__)
        # Construct the path to the 'font' directory
        self.font_dir = os.path.join(script_dir, "font")

        # Define full paths for the required NotoSans font files
        self.regular_font = os.path.join(self.font_dir, "NotoSans-Regular.ttf")
        self.bold_font = os.path.join(self.font_dir, "NotoSans-Bold.ttf")
        self.italic_font = os.path.join(self.font_dir, "NotoSans-Italic.ttf")
        
        # Verify that all required font files exist.
        # This is crucial for FPDF to render text correctly, especially for Unicode characters.
        if not all(os.path.exists(f) for f in [self.regular_font, self.bold_font, self.italic_font]):
            raise FileNotFoundError(
                f"Required font files not found in font directory: {self.font_dir}. "
                "Please ensure NotoSans-Regular.ttf, NotoSans-Bold.ttf, and NotoSans-Italic.ttf are present."
            )

    def _clean_text(self, text: str) -> str:
        """
        Cleans and normalizes text to ensure it is compatible with FPDF,
        especially for handling Unicode characters.

        Args:
            text (str): The input text string.

        Returns:
            str: The cleaned and normalized text string.
        """
        if not isinstance(text, str):
            text = str(text) # Convert non-string inputs to string
        # Normalize Unicode characters to their canonical composed form (NFKC)
        # This helps in consistent rendering and avoids issues with combining characters.
        text = unicodedata.normalize('NFKC', text)
        return text

    def generate_pdf(self, grouped_data: Dict, analyses: List[Dict], web_references: List[Dict] = None, faiss_results: Dict[str, Any] = None) -> str:
        """
        Generates a PDF report containing grouped real estate data and market analyses.

        Args:
            grouped_data (Dict): A dictionary containing categorized real estate listings.
            analyses (List[Dict]): A list of analysis results.
            web_references (List[Dict], optional): A list of dictionaries containing web references. Defaults to None.
            faiss_results (Dict[str, Any], optional): A dictionary containing FAISS search results,
                                                       expected to have 'query' and 'results' keys. Defaults to None.

        Returns:
            str: The filename of the generated PDF report.
        """
        pdf = FPDF()
        
        pdf.add_font("NotoSans", style="", fname=self.regular_font, uni=True)
        pdf.add_font("NotoSans", style="B", fname=self.bold_font, uni=True)
        pdf.add_font("NotoSans", style="I", fname=self.italic_font, uni=True)
        
        pdf.set_font("NotoSans", size=12)
        pdf.set_auto_page_break(True, margin=15)

        pdf.add_page()
        
        # --- Report Title ---
        pdf.set_font("NotoSans", style="B", size=16)
        pdf.cell(0, 10, txt=self._clean_text("Mongolian Real Estate Market Report"), ln=1, align='C')
        pdf.set_font("NotoSans", size=12)
        pdf.cell(0, 10, txt=self._clean_text(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"), ln=1, align='C')
        pdf.ln(10)

        # --- Grouped Data Section ---
        for category, groups in grouped_data.items():
            pdf.set_font("NotoSans", style="B", size=14)
            pdf.set_x(pdf.l_margin)
            pdf.cell(0, 10, txt=self._clean_text(f"{category.replace('_', ' ').title()}"), ln=1)
            pdf.set_font("NotoSans", size=12)
            
            for group_name, listings in groups.items():
                pdf.set_font("NotoSans", style="B", size=12)
                pdf.set_x(pdf.l_margin)
                pdf.cell(0, 10, txt=self._clean_text(f"{group_name}: {len(listings)} үл хөдлөх хөрөнгө"), ln=1)
                pdf.set_font("NotoSans", size=12)
                
                if listings:
                    sample = listings[0]
                    sample_text = (
                        f"Жишээ: {sample.get('title', 'N/A')} - "
                        f"{sample.get('price', 'N/A')} - "
                        f"{sample.get('place', 'N/A')}"
                    )
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 7, txt=self._clean_text(sample_text))
                    pdf.ln(2)
            
            pdf.ln(5)

        # --- Analysis Section ---
        if analyses:
            pdf.add_page()
            pdf.set_font("NotoSans", style="B", size=16)
            pdf.cell(0, 10, txt=self._clean_text("Market Analysis Insights"), ln=1, align='C')
            pdf.ln(10)
            pdf.set_font("NotoSans", size=12)

            for analysis in analyses:
                pdf.set_font("NotoSans", style="B", size=14)
                pdf.set_x(pdf.l_margin)
                pdf.cell(0, 10, txt=self._clean_text(f"Analysis for: {analysis.get('group_name', 'N/A')}"), ln=1)
                pdf.set_font("NotoSans", size=12)
                
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 7, txt=self._clean_text(f"  - Total Listings: {analysis.get('count', 0)}"))
                
                avg_price = analysis.get('average_price')
                if avg_price is not None:
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 7, txt=self._clean_text(f"  - Average Price: {avg_price:,.2f}"))
                
                price_range = analysis.get('price_range')
                if price_range:
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 7, txt=self._clean_text(f"  - Price Range: {price_range[0]:,.2f} - {price_range[1]:,.2f}"))
                
                common_features = analysis.get('common_features')
                if common_features: # Only display if common_features is not empty
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 7, txt=self._clean_text(f"  - Common Features: {', '.join(common_features)}"))
                
                summary = analysis.get('summary')
                if summary:
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 7, txt=self._clean_text(f"  - Дүгнэлт: {summary}"))

                pdf.ln(5)

        # --- FAISS Search Results Section ---
        if faiss_results and 'query' in faiss_results and 'results' in faiss_results:
            pdf.add_page()
            pdf.set_font("NotoSans", style="B", size=16)
            pdf.cell(0, 10, txt=self._clean_text("FAISS Search Results (Similar Listings)"), ln=1, align='C')
            pdf.ln(10)
            pdf.set_font("NotoSans", size=11) # Slightly smaller font for list items

            query_text = self._clean_text(faiss_results['query'])
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 6, txt=f"Хайлтын асуулга: {query_text}", align='L')
            pdf.ln(5)
            listings_to_display = faiss_results['results']

            if listings_to_display:
                for idx, listing in enumerate(listings_to_display[:5]): # Display top 5 for brevity
                    title = self._clean_text(listing.get('title', 'N/A'))
                    price = self._clean_text(listing.get('price', 'N/A'))
                    place = self._clean_text(listing.get('place', 'N/A'))
                    
                    pdf.set_font("NotoSans", style="B", size=11)
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 6, txt=f"{idx + 1}. {title}", align='L')
                    pdf.set_font("NotoSans", size=10)
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 5, txt=f"  Үнэ: {price}", align='L')
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 5, txt=f"  Байршил: {place}", align='L')
                    pdf.ln(3)
            else:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 7, txt=self._clean_text("No similar listings found for this query."), align='L')
            pdf.ln(5)


        # --- Web References Section (if provided) ---
        if web_references:
            pdf.add_page()
            pdf.set_font("NotoSans", style="B", size=16)
            pdf.cell(0, 10, txt=self._clean_text("Web References"), ln=1, align='C')
            pdf.ln(10)
            pdf.set_font("NotoSans", size=10)

            for ref in web_references:
                title = self._clean_text(ref.get('title', 'No Title'))
                url = self._clean_text(ref.get('url', 'No URL'))
                content = self._clean_text(ref.get('content', 'No Content Available'))

                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 5, txt=f"• Гарчиг: {title}", align='L')
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 5, txt=f"  URL: {url}", align='L')
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 5, txt=f"  Агуулга: {content[:200]}...", align='L')
                pdf.ln(3)

        # --- Save PDF ---
        filename = f"real_estate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        print(f"PDF report generated: {filename}")
        return filename