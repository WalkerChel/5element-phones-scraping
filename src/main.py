import time

import httpx
from bs4 import BeautifulSoup as BS
import csv

CSV = 'phones.csv'
HOST = "https://5element.by"
URL = "https://5element.by/catalog/377-smartfony/"
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 OPR/96.0.0.0 (Edition Yx 06)'
          }

def get_params(url, params = ''):
    page_responce = httpx.get(url, headers=HEADERS, params=params)
    return page_responce


def get_content(html):
    soup = BS(html, 'html.parser')
    items = soup.find_all('div', class_='catalog-item ec-product-item')
    phones = []

    for item in items:
        phones.append(
            {
                'title': item.find('a', class_='c-text').get_text(strip=True),
                'price': item.find('div', class_='c-price').get_text(strip=True).replace(".", ","),
                'link_product': HOST + item.find('a', class_='c-text').get('href'),
                'image': item.find('div', class_="swiper-wrapper").find('link').get('href'),
            }
        )
    return phones

def save_doc(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Name of the product', "price (BYN)", 'link', 'image link'])
        for item in items:
            writer.writerow([item['title'], item['price'], item['link_product'], item['image']])

def parser():
    pagination = input('Write number of pages:')
    pagination = int(pagination.strip())
    html = get_params(URL)
    a = time.time()
    if html.status_code == 200:
        phones = []
        for page in range(1, pagination + 1):
            print(f'Page number {page}')
            html = get_params(URL, params={'page': page})
            phones.extend(get_content(html.text))
            save_doc(phones, CSV)
        # print(phones)
    else:
        print('Error')
        print(html)
    b = time.time()-a
    n = b//60
    m = (b % 60) / 60
    print(f'Scraping {pagination} pages took {b: .2f} seconds or {(n + m): .2f} minutes')


if __name__ == "__main__":
    parser()
