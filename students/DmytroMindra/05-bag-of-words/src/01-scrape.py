import requests
import json
import time

DATA_FILE_PATH_TEMPLATE = '../data/raw_data/{}-{}.json'

# Monitors
# CATEGORY_ID = 80089
# Notebooks
# CATEGORY_ID = 80004
# Mbile Phones
# CATEGORY_ID = 80003
# CATEGORY_ID = 130309
# CATEGORY_ID = 80172
CATEGORY_ID = 80087




PAGE_COUNT = 30

LIST_CATEGORY_TEMPLATE = "https://xl-catalog-api.rozetka.com.ua/v2/goods/get?front-type=xl&category_id={}&page={}&sort=rank&lang=ua"
PRODUCT_COMMENTS_TEMPLATE = "https://product-api.rozetka.com.ua/v3/comments/get?front-type=xl&goods={}&page={}&sort=date&limit=10&lang=ru"

# the most reliable source of proxies:
# https://free-proxy-list.net/anonymous-proxy.html


proxies = \
    {
        "http": "",
        "https": "",
    }


def get_product_ids():
    ids = []

    for page in range(1, PAGE_COUNT):
        url = LIST_CATEGORY_TEMPLATE.format(CATEGORY_ID, page)
        r = make_http_request(url)

        for id in r.json()['data']['ids']:
            ids.append(id)

        with open('../data/product_ids_notebooks.json', 'w', encoding='utf-8') as f:
            json.dump(ids, f, ensure_ascii=False, indent=4)


def get_product_comments(product_id):
    print('scraping page ', 1, 'product', product_id)
    url = PRODUCT_COMMENTS_TEMPLATE.format(product_id, 1)
    r = make_http_request(url)
    filename = DATA_FILE_PATH_TEMPLATE.format(product_id, 1)
    write_to_file(filename, r.text)

    page_count = r.json()["data"]["pages"]["count"]

    for pageNo in range(2, page_count):
        print('scraping page ', pageNo, 'product', product_id)
        url = PRODUCT_COMMENTS_TEMPLATE.format(product_id, pageNo)
        r = make_http_request(url)
        filename = DATA_FILE_PATH_TEMPLATE.format(product_id, pageNo)
        write_to_file(filename, r.text)


def write_to_file(filename, text):
    f = open(filename, 'w')
    f.write(text)
    f.close()


def get_product_ids_from_file():
    with open('../data/product_ids_notebooks.json') as json_file:
        return json.load(json_file)


def make_http_request(url):
    return requests.get(url=url, proxies=proxies)


if __name__ == '__main__':

    get_product_ids()
    failed_ids = []
    count = 0
    for id in get_product_ids_from_file():
        try:
            print(count, 'Scraping product ID#', id)
            count += 1
            get_product_comments(id)
            time.sleep(1)
        except Exception as ex:
            print(type(ex))
            print(ex.args)
            print(ex)
            failed_ids.append(id)
            with open('../data/failed_ids.json', 'w', encoding='utf-8') as f:
                json.dump(failed_ids, f, ensure_ascii=False, indent=4)
