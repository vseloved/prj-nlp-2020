import json
import requests

category_url = 'https://bt.rozetka.com.ua/blenders/c80155/'

category_id = 80155
max_page = 34

product_list_url = "https://xl-catalog-api.rozetka.com.ua/v2/goods/get?front-type=xl&category_id={}&page={}&sort=rank&lang=ua"

proxy = {"http": "", "https": ""}

ids = []

for page in range(1, max_page):
    url = product_list_url.format(category_id, page)
    r = requests.get(url=url, proxies=proxy)

    for id in r.json()['data']['ids']:
        ids.append(id)

    with open('product_ids.json', 'w', encoding='utf-8') as f:
        json.dump(ids, f, ensure_ascii=False, indent=4)
