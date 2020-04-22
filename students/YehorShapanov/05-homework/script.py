from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import json 
from langdetect import detect

class Comment:
    def __init__(self, rating, text, url):
        self.rating = rating
        self.text = text
        self.url = url

product_re = re.compile(r'\/p(\d+)\/')
def dump_to_json(data, file_name):
    with open(file_name+'.json', 'w') as f:
        json.dump(data, f)

def read_from_json(file_name):
    data = None
    with open(file_name) as json_file:
        data = json.load(json_file)
    return data

def process_goods(html):
    products = set()
    soup = BeautifulSoup(html, 'html.parser')
    spans = soup.findAll(class_='goods-tile__reviews-link')
    for span in spans:
        p = span.find_parent()
        pp = p.find_parent()
        h = pp.get('href')
        products.add(h)

    return list(products)

re_rating = re.compile(r'\s(\d)\s[\S\D]{2}\s(\d)\"')
def process_product(html, url):
    comms = set()
    soup = BeautifulSoup(html, 'html.parser')
    c = soup.findAll(class_='product-comment')
    for comment in c: 
        rating_div = comment.find(class_='product-comment__rating')
        s = str(rating_div)
        if not re_rating.search(s):
            continue
        r = re_rating.findall(s)[0]
        body_div = comment.find(class_='product-comment__body')
        body = str(body_div.p) if body_div.p != None else ""
        for s in body_div.findAll(class_='product-comment__essentials-label'):
            body += str(s.text)
            body += str(s.next_sibling.text)
        c = Comment(r, body, url)
        comms.add(c)
    return comms

### Selenium webdriver
#driver = webdriver.Firefox(executable_path = '/Users/yehorshapanov/development/geckodriver/geckodriver')

# prods = list()
# driver = webdriver.Firefox(executable_path = '/Users/yehorshapanov/development/geckodriver/geckodriver')
# urls = ["https://rozetka.com.ua/ua/pitanie-i-kormlenie/c3933312/page={}-{}/".format(i, j) for i, j in zip(range(1, 32, 3), range(3, 35, 3))]
# for u in urls:
#     driver.get(u)
#     prods.extend(process_goods(driver.page_source))

# dump_to_json(prods, 'product_links')

# prods = read_from_json('product_links.json')
# comments = list()
# products = prods
# for i, product in enumerate(products):
#     if i%100:
#         print("Parsed {} pages".format(i))
#     if not product:
#         print(product)
#         continue
#     driver.get(product)
#     comments.extend(process_product(driver.page_source, product))
#     print(len(comments))
# dump_to_json([c.__dict__ for c in comments], 'comments')
# driver.quit()

cleanr = re.compile(r'<.*?>')
comments = read_from_json('comments.json')
cleaned_comments = list()
for obj in comments:
    text = re.sub(cleanr, '', obj['text'])
    if len(text)==0:
        continue
    is_uk = False 
    try:
        is_uk = detect(text)=='uk'
    except:
        continue
    if is_uk:
        data = {}
        data['rating']=obj['rating'][0]
        data['text']=text.replace('Переваги:', '+').replace('Недоліки:', '-')
        cleaned_comments.append(data)

print(len(cleaned_comments))
dump_to_json(cleaned_comments, 'cleaned_comments')