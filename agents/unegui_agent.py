import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional # Added Optional for clarity on None returns

class UneguiAgent:
    """
    A web scraping agent designed to crawl real estate listings from unegui.mn.
    It extracts key information from listing pages and detailed property pages.
    """

    BASE_URL = 'https://www.unegui.mn/'

    def __init__(self):
        """
        Initializes the UneguiAgent. Currently, no specific attributes are needed
        beyond the BASE_URL, but this provides a consistent class structure.
        """
        pass # No specific initialization logic needed for this agent yet

    def crawl_listings(self, pages: int = 1) -> List[Dict]:
        """
        Crawls real estate listings from unegui.mn for a specified number of pages.
        It extracts summary information from the main listing pages and then
        navigates to individual listing URLs to gather more detailed property attributes.

        Args:
            pages (int): The number of pages to crawl. Defaults to 1.

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary represents a single
                        real estate listing with extracted details.
        """
        all_listings_data: List[Dict] = [] # Initialize an empty list to store all crawled data

        # Loop through the specified number of pages
        for i in range(1, pages + 1):
            # Construct the URL for the current listing page
            url = f'{self.BASE_URL}l-hdlh/l-hdlh-zarna/oron-suuts-zarna/?page={i}'
            print(f"Crawling page: {url}") # Print current page being crawled

            try:
                # Send an HTTP GET request to the URL
                response = requests.get(url, timeout=10) # Added timeout for robustness
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching page {url}: {e}")
                continue # Skip to the next page if there's an error

            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all individual advertisement containers on the page
            ads = soup.find_all('div', class_='advert js-item-listing')

            if not ads:
                print(f"No listings found on page {i}. Ending crawl.")
                break # Stop if no ads are found, might indicate end of listings

            # Iterate through each found advertisement
            for ad in ads:
                # Initialize a dictionary to store data for the current advertisement
                ad_data: Dict = {
                    'title': None,
                    'price': None,
                    'place': None,
                    'date': None,
                    'area': None,
                    'balcony': None,
                    'total_floor': None,
                    'details': None,
                    'year': None,
                    'floor': None,
                    'window_count': None,
                    'url': None
                }

                # Extract basic information from the main listing card
                title_tag = ad.find('a', class_='advert__content-title')
                ad_data['title'] = title_tag.get_text(strip=True) if title_tag else None

                date_tag = ad.find('div', class_='advert__content-date')
                ad_data['date'] = date_tag.get_text(strip=True) if date_tag else None

                place_tag = ad.find('div', class_='advert__content-place')
                ad_data['place'] = place_tag.get_text(strip=True) if place_tag else None

                price_tag = ad.find('a', class_='advert__content-price _not-title')
                # Extract the href attribute for the detailed listing URL
                href = price_tag['href'] if price_tag and 'href' in price_tag.attrs else None
                ad_data['price'] = price_tag.get_text(strip=True) if price_tag else None
                # Construct the full URL for the detailed listing
                additional_url = self.BASE_URL + href if href else None
                ad_data['url'] = additional_url

                # If a detailed URL is found, crawl the individual listing page for more details
                if additional_url:
                    try:
                        print(f"  Fetching details from: {additional_url}") # Indicate detail fetching
                        detail_response = requests.get(additional_url, timeout=10)
                        detail_response.raise_for_status()
                        soup2 = BeautifulSoup(detail_response.text, 'html.parser')

                        # Extract general details/description
                        detail_section = soup2.find('div', class_='js-description')
                        ad_data['details'] = detail_section.get_text(strip=True) if detail_section else None

                        # Extract specific characteristics from the 'chars-column' section
                        additional_section = soup2.find('ul', class_='chars-column')
                        if additional_section:
                            keys = additional_section.find_all('span', class_='key-chars')
                            values = additional_section.find_all(class_='value-chars')
                            
                            for k, v in zip(keys, values):
                                key_text = k.get_text(strip=True).lower()
                                val_text = v.get_text(strip=True)
                                
                                # Map extracted keys to the ad_data dictionary fields
                                if 'талбай:' in key_text:
                                    ad_data['area'] = val_text
                                elif 'тагт:' in key_text:
                                    ad_data['balcony'] = val_text
                                elif 'ашиглалтанд орсон он:' in key_text:
                                    ad_data['year'] = val_text
                                elif 'хэдэн давхарт:' in key_text:
                                    ad_data['floor'] = val_text
                                elif 'цонхны тоо:' in key_text:
                                    ad_data['window_count'] = val_text
                                elif 'барилгын давхар:' in key_text:
                                    ad_data['total_floor'] = val_text
                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching details from {additional_url}: {e}")
                    except Exception as e:
                        print(f"Error parsing details from {additional_url}: {e}")
                
                all_listings_data.append(ad_data) # Add the completed listing data to the list

            time.sleep(1) # Pause for 1 second between page requests to be polite to the server

        return all_listings_data