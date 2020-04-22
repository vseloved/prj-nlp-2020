import time
import json
import requests
from random import randint

CATEGORIES = [
    80125, 80203, 80124,
    80222, 80122, 80123,
    80121, 80177,
]

GOODS_URL = 'https://xl-catalog-api.rozetka.com.ua/v2/goods/get?front-type=xl&category_id={}&page={}&sort=rank&lang=ru'

with open("goods.txt", "w") as f:
    for category in CATEGORIES:
        for i in range(1, 34):
            r = requests.get(GOODS_URL.format(category, i))
            if r:
                goods_ids = json.loads(r.text)["data"]["ids"]
                for g in goods_ids:
                    f.write(f'{g}\n')
                time.sleep(randint(1, 5))

