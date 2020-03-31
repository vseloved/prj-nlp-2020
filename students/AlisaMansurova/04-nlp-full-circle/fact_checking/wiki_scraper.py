import requests
from bs4 import BeautifulSoup


def get_page_content(title):
    response = requests.get(
        'https://en.wikipedia.org/w/api.php',
        params={
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'extracts',
            'exsectionformat': 'raw',
        }
    ).json()

    pages = [x['extract'] for x in response['query']['pages'].values()]
    html_text = '\n'.join(pages)
    soup = BeautifulSoup(html_text, 'html.parser')
    p = [x.text for x in soup.findAll('p')]
    q = [x.text for x in soup.findAll('blockquote')]
    content = '\n'.join(p + q)
    return content


band_page_content = get_page_content('Katatonia')
alb = get_page_content('Dance_of_December_Souls')
# print(alb)
