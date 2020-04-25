import requests
import json
import time

CLIMATE_CATEG_ID = 80079

def get_product_ids(category_id):
    url = 'https://xl-catalog-api.rozetka.com.ua/v2/goods/get?category_id={}&page={}'    
    
    page_id = 1
    active = True
    
    while active:
        r = requests.get(url.format(category_id, page_id))
        
        body = r.json()
        data = body['data']
        
        for id in data['ids']:
            yield(id)
        
        if page_id < data['total_pages']:
            page_id += 1
        else:
            active = False
    
def get_comments(product_id):
    url = 'https://product-api.rozetka.com.ua/v3/comments/get?goods={}&page={}'
    
    page_id = 1
    active = True
    
    while active:
        r = requests.get(url.format(product_id, page_id))
        
        body = r.json()
        data = body['data']
        
        for c in data['comments']:
            yield(c)
        
        if page_id < data['pages']['count']:
            page_id += 1
        else:
            active = False

def format_comment(item):                      
    return {
        'id': item['id'],
        'name': item['usertitle'],
        'rate': item['mark'],
        'text': item['text'],
        'advantages': item['dignity'],
        'shortcomings': item['shortcomings'],   
        'positive_votes_count': item['votes']['positive'],
        'negative_votes_count': item['votes']['negative']
    }

def load_data():
    with open('comments.json', 'w') as out:
        count = 0
        
        for p_id in get_product_ids(CLIMATE_CATEG_ID):
            for c in get_comments(p_id):
                out.write(json.dumps(format_comment(c)) + '\n')
                if count % 10 == 0: print(count)
                count += 1
                time.sleep(1)

                
if __name__== '__main__':
    load_data()