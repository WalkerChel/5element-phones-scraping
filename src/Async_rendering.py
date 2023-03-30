import asyncio
import csv
import time
import httpx
from bs4 import BeautifulSoup as Bs
# import csv

CSV = 'phones_Async.csv'
HOST = "https://5element.by"
URL = "https://5element.by/catalog/377-smartfony?items=100"
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/110.0.0.0 Safari/537.36 OPR/96.0.0.0 (Edition Yx 06)'
          }


def time_logg(funk):
    async def wrapper(*args, **kwargs):
        a = time.time()
        await funk(*args, **kwargs)
        print(f'\nTime passed: {(time.time()-a): .2f}')
    return wrapper


def save_doc(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Name of the product', "price (BYN)", 'link', 'image link'])
        for item in items:
            writer.writerow([item['title'], item['price'], item['link_product'], item['image']])


# async def proces_request(request: httpx.Response):
#    pass


async def proces_response(response: httpx.Response):
    result = await response.aread()
    soup = Bs(result, 'html.parser')
    content = soup.find_all('div', class_='catalog-item ec-product-item')
    global phones
    for item in content:
        phones.append(
            {
                'title': item.find('a', class_='c-text').get_text(strip=True),
                'price': item.find('div', class_='c-price').get_text(strip=True).replace(".", ","),
                'link_product': HOST + item.find('a', class_='c-text').get('href'),
                'image': item.find('div', class_="swiper-wrapper").find('link').get('href'),
            }
        )


async def get_params(url: str, params=None):
    params = {"page": None} if params is None else params
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, event_hooks={'response': [proces_response]})\
            as htx:
        request: httpx.Response = await htx.get(url, params=params)
        # TODO fix exception when there are too many requests
        if request.status_code != 200:
            return await get_params(url, params=params)


@time_logg
async def main():
    pagination = int(input("Write number of pages:").strip())
    tasks = []
    for page in range(1, pagination+1):
        tasks.append(get_params(URL, params={"page": page}))

    await asyncio.gather(*tasks)
    save_doc(phones, CSV)


phones = []

if __name__ == "__main__":
    asyncio.run(main())
