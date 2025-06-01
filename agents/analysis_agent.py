import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
import google.generativeai as genai
import os
import json
import re

class AnalysisAgent:
    """
    An agent responsible for performing analysis on real estate data.
    It can group data, calculate statistics, and generate insights and
    improvement suggestions using an LLM.
    """

    def __init__(self):
        """
        Initializes the AnalysisAgent with a hardcoded Google Generative AI API key.
        WARNING: Hardcoding API keys is not recommended for production or public code.
        """
        genai.configure(api_key="AIzaSyBXVyX1sE0NBLkjbDr0VcTaSOAi_AFkg3I")
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def group_data(self, data: List[Dict]) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Groups real estate listing data by various attributes like number of rooms,
        district, and year.

        Args:
            data (List[Dict]): A list of dictionaries, where each dictionary
                               represents a real estate listing.

        Returns:
            Dict[str, Dict[str, List[Dict]]]: A nested dictionary containing
                                              grouped data.
                                              Example: {"by_rooms": {"1 room": [...], ...},
                                                        "by_district": {"Bayanzurkh": [...], ...}}
        """
        grouped_data: Dict[str, Dict[str, List[Dict]]] = {
            "by_rooms": {},
            "by_district": {},
            "by_year": {}
        }

        for listing in data:
            # Group by rooms
            if 'title' in listing and listing['title']:
                room_match = re.search(r'(\d+)\s*өрөө', listing['title'])
                if room_match:
                    num_rooms = room_match.group(1) + " өрөө"
                    if num_rooms not in grouped_data["by_rooms"]:
                        grouped_data["by_rooms"][num_rooms] = []
                    grouped_data["by_rooms"][num_rooms].append(listing)

            # Group by district
            if 'place' in listing and listing['place']:
                district = listing['place'].split(',')[0].strip()
                if district:
                    if district not in grouped_data["by_district"]:
                        grouped_data["by_district"][district] = []
                    grouped_data["by_district"][district].append(listing)

            # Group by year
            if 'year' in listing and listing['year']:
                year = str(listing['year']).split('.')[0] # Take only the year part if it's "2020.0"
                if year.isdigit():
                    if year not in grouped_data["by_year"]:
                        grouped_data["by_year"][year] = []
                    grouped_data["by_year"][year].append(listing)

        return grouped_data

    def _extract_numeric_price(self, price_str: Optional[str]) -> Optional[float]:
        """
        Extracts a numeric price from a price string, handling Mongolian Tugrik (MNT)
        and common formatting issues, including spaces as thousands separators.
        Converts all to standard numeric representation in Tugrik (MNT).

        Args:
            price_str (str): The price string (e.g., "300 сая ₮", "1.5 тэрбум ₮", "590 680 ₮", "300,000₮").

        Returns:
            Optional[float]: The price as a float, or None if extraction fails.
        """
        if not price_str:
            return None

        clean_price_initial = price_str.replace('₮', '').strip()

        if 'сая' in clean_price_initial:
            value_part = clean_price_initial.replace('сая', '').strip()
            cleaned_value_part = value_part.replace(',', '').replace(' ', '')
            try:
                value = float(cleaned_value_part) * 1_000_000
            except ValueError:
                return None
        elif 'тэрбум' in clean_price_initial:
            value_part = clean_price_initial.replace('тэрбум', '').strip()
            cleaned_value_part = value_part.replace(',', '').replace(' ', '')
            try:
                value = float(cleaned_value_part) * 1_000_000_000
            except ValueError:
                return None
        else:
            try:
                value = float(clean_price_initial.replace(',', '').replace(' ', ''))
            except ValueError:
                return None
        return value

    def _calculate_common_features(self, listings: List[Dict]) -> List[str]:
        """
        Calculates the most common features (balcony, total_floor, year, window_count, floor)
        within a list of listings.

        Args:
            listings (List[Dict]): A list of listing dictionaries.

        Returns:
            List[str]: A list of strings describing common features,
                       e.g., ["1 тагттай", "2020 онд ашиглалтанд орсон"].
        """
        if not listings:
            return []

        feature_counts: Dict[str, Dict[str, int]] = {
            'balcony': {},
            'total_floor': {},
            'year': {},
            'window_count': {},
            'floor': {}
        }

        for listing in listings:
            for feature in feature_counts.keys():
                value = listing.get(feature)
                if value:
                    if feature == 'year':
                        value = str(value).split('.')[0]
                    if str(value).isdigit(): # Ensure year is numeric before counting
                        if value not in feature_counts[feature]:
                            feature_counts[feature][value] = 0
                        feature_counts[feature][value] += 1

        common_features: List[str] = []
        num_listings = len(listings)
        threshold = num_listings * 0.4 # Feature must appear in at least 40% of listings to be considered 'common'

        feature_display_names = {
            'balcony': 'тагттай',
            'total_floor': 'нийт давхар',
            'year': 'онд ашиглалтанд орсон',
            'window_count': 'цонхтой',
            'floor': 'давхарт байрладаг'
        }

        for feature, counts in feature_counts.items():
            for value, count in counts.items():
                if count >= threshold:
                    # Specific formatting for each feature
                    if feature == 'balcony':
                        common_features.append(f"{value} {feature_display_names[feature]}")
                    elif feature == 'year':
                         common_features.append(f"{value} {feature_display_names[feature]}")
                    elif feature == 'floor':
                        common_features.append(f"{value} {feature_display_names[feature]}")
                    elif feature == 'window_count':
                        common_features.append(f"{value} {feature_display_names[feature]}")
                    elif feature == 'total_floor':
                        common_features.append(f"{value} {feature_display_names[feature]}")

        return common_features

    def analyze_group(self, group_name: str, listings: List[Dict]) -> Dict:
        """
        Analyzes a specific group of real estate listings, calculating statistics
        and generating dynamic insights using an LLM. This method is now primarily
        for *sub-groups* if detailed analysis is needed, but for 5 main groups,
        use analyze_overall_category.

        Args:
            group_name (str): The name of the group being analyzed (e.g., "3 өрөө", "Bayanzurkh").
            listings (List[Dict]): A list of real estate listings belonging to this group.

        Returns:
            Dict: A dictionary containing the analysis results for the group,
                  including count, average price, price range, common features,
                  LLM-generated summary, and LLM-generated suggestions.
        """
        count = len(listings)
        prices = [self._extract_numeric_price(l.get('price')) for l in listings if l.get('price')]
        prices = [p for p in prices if p is not None and p > 0]

        average_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        common_features = self._calculate_common_features(listings)
        common_features_str = ", ".join(common_features) if common_features else "Мэдээлэл байхгүй"

        # --- Dynamic Analysis and Suggestions using LLM ---
        llm_prompt = f"""
        Үл хөдлөх хөрөнгийн дараах бүлгийг задлан шинжил. Энэ бүлгийн онцлогийг товч бөгөөд чанартайгаар нэгтгэн дүгнэж, энэ бүлэгт багтсан үл хөдлөх хөрөнгөд хамаарах сайжруулах санал, эсвэл стратегийн зөвлөгөөг 3-5 өгүүлбэрт багтаан өгнө үү.
        Хариултаа дараах форматаар өгнө үү:
        Шинжилгээ: [Энд товч шинжилгээний дүгнэлт орно]
        Санал: [Энд 3-5 өгүүлбэрт багтсан санал орно]

        Бүлгийн нэр: {group_name}
        Нийт жагсаалт: {count}
        Дундаж үнэ: {average_price:,.2f} ₮
        Үнийн хэлбэлзэл: {min_price:,.2f} ₮ - {max_price:,.2f} ₮
        Нийтлэг шинж чанарууд: {common_features_str}
        """

        summary_content = "LLM шинжилгээг хийх боломжгүй байсан."
        suggestions_text = "LLM-ээс хариу авахад алдаа гарлаа. Утасны тохиргоо, эсвэл API түлхүүрээ шалгана уу."

        try:
            response = self.model.generate_content(llm_prompt)
            llm_text = response.text.strip()

            summary_match = re.search(r'Шинжилгээ:\s*(.*?)(?=\nСанал:|$)', llm_text, re.DOTALL)
            if summary_match:
                summary_content = summary_match.group(1).strip()
            
            suggestions_section_match = re.search(r'Санал:\s*(.*)', llm_text, re.DOTALL)
            if suggestions_section_match:
                suggestions_text = suggestions_section_match.group(1).strip()
            
            if not summary_content and llm_text:
                summary_content = llm_text.split('\n\n')[0].strip()
            if not suggestions_text and llm_text:
                suggestions_text = llm_text.split('\n\n')[-1].strip()
                if suggestions_text == summary_content: 
                    suggestions_text = ""


        except Exception as e:
            print(f"Error generating analysis/suggestions for '{group_name}' with LLM: {e}")

        analysis = {
            "group_name": group_name,
            "count": count,
            "average_price": average_price,
            "price_range": (min_price, max_price),
            "common_features": common_features,
            "summary": summary_content, 
            "improvement_suggestions": [suggestions_text] if suggestions_text else [] 
        }
        return analysis

    def analyze_overall_category(self, category_name: str, all_sub_groups: Dict[str, List[Dict]]) -> Dict:
        """
        Analyzes an entire category of real estate listings (e.g., "By District", "By Room Count"),
        consolidating all listings within its sub-groups and generating a single analysis.

        Args:
            category_name (str): The name of the category being analyzed (e.g., "by_district").
            all_sub_groups (Dict[str, List[Dict]]): A dictionary of sub-groups within the category,
                                                     where keys are sub-group names (e.g., "Bayanzurkh", "1 өрөө")
                                                     and values are lists of listings.

        Returns:
            Dict: A dictionary containing the analysis results for the entire category.
        """
        all_listings_in_category = []
        for sub_group_name, listings_in_sub_group in all_sub_groups.items():
            all_listings_in_category.extend(listings_in_sub_group)

        count = len(all_listings_in_category)
        prices = [self._extract_numeric_price(l.get('price')) for l in all_listings_in_category if l.get('price')]
        prices = [p for p in prices if p is not None and p > 0] # Filter out None and zero prices

        average_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        common_features = self._calculate_common_features(all_listings_in_category)
        common_features_str = ", ".join(common_features) if common_features else "Мэдээлэл байхгүй"

        # --- Dynamic Analysis and Suggestions using LLM for the overall category ---
        llm_prompt = f"""
        Үл хөдлөх хөрөнгийн дараах бүлгийг (бүлгийн нэр: {category_name.replace('_', ' ').title()}) задлан шинжил. Энэ бүлгийн онцлогийг товч бөгөөд чанартайгаар нэгтгэн дүгнэ.
        Энэхүү бүлэг нь дотроо олон жижиг бүлгүүдээс бүрдсэн бөгөөд нийт {count} жагсаалтыг агуулсан.
        Хариултаа дараах форматаар өгнө үү:
        Шинжилгээ: [Энд 3-5 өгүүлбэрт багтсан товч шинжилгээний дүгнэлт орно]

        Нийт дундаж үнэ: {average_price:,.2f} ₮
        Нийт үнийн хэлбэлзэл: {min_price:,.2f} ₮ - {max_price:,.2f} ₮
        Бүлгийн нийтлэг шинж чанарууд: {common_features_str}
        Хэрэв аль нэг өгсөн мэдээлэл хоосон эсвэл null байвал тэр хэсгийг оруулахгүй дүгнэлт бичээрэй.
        """

        summary_content = "LLM шинжилгээг хийх боломжгүй байсан."
        suggestions_text = "LLM-ээс хариу авахад алдаа гарлаа. Утасны тохиргоо, эсвэл API түлхүүрээ шалгана уу."

        try:
            response = self.model.generate_content(llm_prompt)
            llm_text = response.text.strip()

            summary_match = re.search(r'Шинжилгээ:\s*(.*?)(?=\nСанал:|$)', llm_text, re.DOTALL)
            if summary_match:
                summary_content = summary_match.group(1).strip()
            
            suggestions_section_match = re.search(r'Санал:\s*(.*)', llm_text, re.DOTALL)
            if suggestions_section_match:
                suggestions_text = suggestions_section_match.group(1).strip()
            
            if not summary_content and llm_text:
                summary_content = llm_text.split('\n\n')[0].strip()
            if not suggestions_text and llm_text:
                suggestions_text = llm_text.split('\n\n')[-1].strip()
                if suggestions_text == summary_content:
                    suggestions_text = ""

        except Exception as e:
            print(f"Error generating analysis/suggestions for '{category_name}' overall with LLM: {e}")

        analysis = {
            "group_name": category_name.replace('_', ' ').title(), 
            "count": count,
            "average_price": average_price,
            "price_range": (min_price, max_price),
            "common_features": common_features,
            "summary": summary_content,
            "improvement_suggestions": [suggestions_text] if suggestions_text else []
        }
        return analysis

    def generate_chain_of_thought(self, suggestion: str) -> Dict[str, str]:
        """
        Generates a detailed "chain of thought" for a given improvement suggestion
        using the LLM, breaking down how to approach the suggestion.

        Args:
            suggestion (str): The improvement suggestion to elaborate on.

        Returns:
            Dict[str, str]: A dictionary containing the original suggestion and
                            the detailed chain of thought.
        """
        prompt = f"""
        Дараах сайжруулах саналыг хэрэгжүүлэхэд чиглэсэн алхам алхмаар "бодлын гинж" (chain of thought)-ийг товч бөгөөд 2-3 өгүүлбэрт багтаан тайлбарлаж өгнө үү.
        Санал: "{suggestion}"
        Бодлын гинж:
        """
        try:
            response = self.model.generate_content(prompt)
            return {
                "suggestion": suggestion,
                "chain_of_thought": response.text.strip()
            }
        except Exception as e:
            return {
                "suggestion": suggestion,
                "chain_of_thought": f"Бодлын гинжийг үүсгэхэд алдаа гарлаа: {e}"
            }
