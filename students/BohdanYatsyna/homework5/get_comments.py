import json
import requests
from tqdm import tqdm
import time

products = []
comments_url = "https://product-api.rozetka.com.ua/v3/comments/get?front-type=xl&goods={}&page={}&sort=date&limit=10&lang=ru"
data_teamplate = './data/{}-{}.json'

proxy = {"http": "", "https": ""}

with open('product_ids.json') as json_file:
    products = json.load(json_file)

failed_ids = []
count = 0

for id in tqdm(products):
    url = comments_url.format(id, 1)
    r = requests.get(url=url, proxies=proxy)
    filename = data_teamplate.format(id, 1)
    with open(filename,'w+', encoding='utf-8') as f:
        f.write(r.text)

    page_count = r.json()["data"]["pages"]["count"]
    time.sleep(1)
    for page_id in range(2, page_count):
        url = comments_url.format(id, page_id)
        r = requests.get(url=url, proxies=proxy)
        filename = data_teamplate.format(id, page_id)
        with open(filename,'w+', encoding='utf-8') as f:
            f.write(r.text)
        time.sleep(1)
