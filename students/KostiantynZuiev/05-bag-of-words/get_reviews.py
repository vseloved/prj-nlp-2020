import time
import json
import requests
from random import randint



REVIEWS_URL = 'https://product-api.rozetka.com.ua/v3/comments/get?front-type=xl&goods={}&page={}&sort=date&limit=10&lang=ru'

reviews = []
with open("goods.txt", "r") as f:
    for line in f:
        print(line)
        for i in range(1, 1000):
            r = requests.get(REVIEWS_URL.format(line.strip('\n'), i))
            if r:
                data = json.loads(r.text).get("data")
                if data is None:
                    break
                reviews.extend(data["comments"])
                if data["pages"]["count"] == 0 or data["pages"]["count"] == data["pages"]["selected"]:
                    break
            else:
                break
        time.sleep(randint(1, 5))

with open("reviews.json", "w") as f:
    json.dump(reviews, f)
    

