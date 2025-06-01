from typing import List, Dict
import re

class GroupingAgent:
    def group_properties(self, listings: List[Dict]) -> Dict[str, Dict[str, List[Dict]]]:
        groups = {
            "by_district": {},
            "by_price_range": {},
            "by_room_count": {},
            "by_area_range": {},
            "by_year_built": {}
        }
        
        for listing in listings:
            district = self._extract_district(listing.get("place", ""))
            if district:
                if district not in groups["by_district"]:
                    groups["by_district"][district] = []
                groups["by_district"][district].append(listing)
            
            price_str = listing.get("price", "")
            price_range = self._get_price_range(price_str)
            if price_range:
                if price_range not in groups["by_price_range"]:
                    groups["by_price_range"][price_range] = []
                groups["by_price_range"][price_range].append(listing)
            
            room_count = self._extract_room_count(listing.get("title", "") + " " + listing.get("details", ""))
            if room_count:
                if room_count not in groups["by_room_count"]:
                    groups["by_room_count"][room_count] = []
                groups["by_room_count"][room_count].append(listing)
            
            area_str = listing.get("area", "")
            area_range = self._get_area_range(area_str)
            if area_range:
                if area_range not in groups["by_area_range"]:
                    groups["by_area_range"][area_range] = []
                groups["by_area_range"][area_range].append(listing)
            
            year_str = listing.get("year", "")
            year_range = self._get_year_range(year_str)
            if year_range:
                if year_range not in groups["by_year_built"]:
                    groups["by_year_built"][year_range] = []
                groups["by_year_built"][year_range].append(listing)
                
        return groups
    
    def _extract_district(self, place: str) -> str:
        districts = ["Баянзүрх", "Хан-Уул", "Баянгол", "Сүхбаатар", "Чингэлтэй", 
                   "Налайх", "Багануур", "Багахангай"]
        for district in districts:
            if district in place:
                return district
        return None
    
    def _get_price_range(self, price_str: str) -> str:
        try:
            if "сая" in price_str:  
                price = float(re.search(r"[\d.]+", price_str).group()) * 1_000_000
            else:
                price = float(re.sub(r"[^\d]", "", price_str))
            
            if price < 100_000_000:
                return "100 Саяас бага үнэтэй"
            elif 100_000_000 <= price < 300_000_000:
                return "100 саяас - 300 сая"
            elif 300_000_000 <= price < 500_000_000:
                return "300 саяас - 500 сая"
            else:
                return "500 саяас их"
        except:
            return None
    
    def _extract_room_count(self, text: str) -> str:
        text = text.lower()
        if "1 өрөө" in text or "1-р өрөө" in text:
            return "1 room"
        elif "2 өрөө" in text or "2-р өрөө" in text:
            return "2 rooms"
        elif "3 өрөө" in text or "3-р өрөө" in text:
            return "3 rooms"
        elif "4 өрөө" in text or "4-р өрөө" in text:
            return "4 rooms"
        elif "5 өрөө" in text or "5-р өрөө" in text:
            return "5+ rooms"
        return None
    
    def _get_area_range(self, area_str: str) -> str:
        try:
            area = float(re.search(r"[\d.]+", area_str).group())
            if area < 40:
                return "Under 40 sqm"
            elif 40 <= area < 60:
                return "40-60 sqm"
            elif 60 <= area < 80:
                return "60-80 sqm"
            else:
                return "Over 80 sqm"
        except:
            return None
    
    def _get_year_range(self, year_str: str) -> str:
        try:
            year_match = re.search(r"\b\d{4}\b", year_str)
            if year_match:
                year = int(year_match.group())
                if year < 2000:
                    return "Pre-2000"
                elif 2000 <= year < 2010:
                    return "2000-2010"
                elif 2010 <= year < 2020:
                    return "2010-2020"
                else:
                    return "Post-2020"
        except:
            return None