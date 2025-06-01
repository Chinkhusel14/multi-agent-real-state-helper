# agents/unegui_agent.py

import requests
from bs4 import BeautifulSoup
import time

BASE_URL = 'https://www.unegui.mn/'

def crawl_listings(pages=1) -> list:
    data = []

    for i in range(1, pages + 1):
        url = f'{BASE_URL}l-hdlh/l-hdlh-zarna/oron-suuts-zarna/?page={i}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        ads = soup.find_all('div', class_='advert js-item-listing')

        for ad in ads:
            title_tag = ad.find('a', class_='advert__content-title')
            title = title_tag.get_text(strip=True) if title_tag else None

            date_tag = ad.find('div', class_='advert__content-date')
            date = date_tag.get_text(strip=True) if date_tag else None

            place_tag = ad.find('div', class_='advert__content-place')
            place = place_tag.get_text(strip=True) if place_tag else None

            price_tag = ad.find('a', class_='advert__content-price _not-title')
            href = price_tag['href'] if price_tag else None
            price = price_tag.get_text(strip=True) if price_tag else None
            additional_url = BASE_URL + href if href else None

            ad_data = {
                'title': title,
                'price': price,
                'place': place,
                'date': date,
                'area': None,
                'balcony': None,
                'total_floor': None,
                'details': None,
                'year': None,
                'floor': None,
                'window_count': None,
                'url': additional_url
            }

            if additional_url:
                try:
                    response = requests.get(additional_url)
                    soup2 = BeautifulSoup(response.text, 'html.parser')
                    additional_section = soup2.find('ul', class_='chars-column')
                    detail_section = soup2.find('div', class_='js-description')
                    details = detail_section.get_text(strip=True) if detail_section else None
                    ad_data['details'] = details

                    keys = additional_section.find_all('span', class_='key-chars')
                    values = additional_section.find_all(class_='value-chars')
                    for k, v in zip(keys, values):
                        key_text = k.get_text(strip=True).lower()
                        val_text = v.get_text(strip=True)
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
                except Exception as e:
                    print(f"Error parsing {additional_url}: {e}")
            data.append(ad_data)

        time.sleep(1)

    return data
