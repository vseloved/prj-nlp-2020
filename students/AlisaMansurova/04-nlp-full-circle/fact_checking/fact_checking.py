import requests
import json
import en_core_web_md
from bs4 import BeautifulSoup
import re
import os

nlp = en_core_web_md.load()

absDir = os.path.dirname(os.path.abspath(__file__))
dbpedia_data_file_name = './dbpedia_query_res.json'
dbpedia_data_file = os.path.join(absDir, dbpedia_data_file_name)

with open(dbpedia_data_file) as f:
    dbpedia_data = json.load(f)


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


def has_date(sent):
    return re.search('\\d{4}', sent)


def find_token_in_sent(sent, t):
    res = [x for x in sent if x.lower_ == t.lower()]
    return res[0] if res else None


# Build in istitle() fn doesn't work for words with apostrophe ¯\_(ツ)_/¯
def is_title(string):
    return string[0].isupper()


def get_release_date(token):
    year_match = re.search('^\\d{4}', token.text)
    if year_match:
        return year_match.group(0)
    return next((x for x in (get_release_date(c) for c in token.children) if x), None)


def get_album_name(token):
    if token.ent_type == 'PERSON':
        return None
    children = [x for x in token.children if x.text
                and '\n' not in x.text
                and x.ent_type_ != 'DATE']
    child_texts = [x.text for x in children]

    if is_title(token.text) or is_title(token.head.text):
        res = [y for y in (get_album_name(x) for x in children) if y]
        res_flattened = [x for sub in res for x in sub]
        if (token.pos_ != 'AUX'
                or token.pos_ == 'AUX' and 'album' not in child_texts) \
                and token.ent_type != 'PERSON':
            res_flattened.append(token)
        return sorted(res_flattened, key=lambda x: x.idx)

    if 'album' in child_texts:
        res = [get_album_name(x) for x in children if x.text != 'album']
        res_flattened = [x for sub in [y for y in res if y] for x in sub if x]
        return res_flattened
    return None


def get_album_data_from_wiki_page(doc):
    sents = list(doc.sents)
    albums = []
    for i in range(0, len(sents)):
        sent = sents[i]
        if (sent.text.find(' released') != -1 or sent.text.find('Released') != -1) \
                and has_date(sent.text):
            first_token = sent[0]
            album_name = None
            released_token = find_token_in_sent(sent, 'released')
            if first_token.pos_ == 'VERB' or first_token.pos_ == 'AUX' and i:
                prev_text = sents[i - 1].text.strip()
                a_names = get_album_name(sents[i - 1].root)
                if a_names:
                    album_name = ' '.join([x.text for x in a_names])
            else:
                a_names = get_album_name(sents[i].root)
                if a_names:
                    album_name = ' '.join([x.text for x in a_names])

            if album_name:
                album_name = ' '.join(
                    [x for x in album_name.split(' ') if is_title(x) or len(x) < 4])
                album_name = album_name.replace(" ' ", " 'n' ").replace(
                    ' !', '!').replace(' ?', '?').replace(' .', '').replace(
                        '(', '').replace(')', '').strip()
                release_year = get_release_date(released_token)
                year = release_year if type(
                    release_year) == str else release_year.text if release_year else ''
                albums.append({'album': album_name, 'release_years': year})

                # Last resort
                titles = re.findall(
                    '([A-Z][a-z]+[\\s\\w\\.\\.\\.\']+([A-Z][a-z]+)?(?:\\s+\\(\\d+\\)))', sent.text)
                for v in titles:
                    res = []
                    parts = re.split('(\\(\\d+\\))', v[0])
                    title = parts[0]
                    year = parts[1].replace('(', '').replace(')', '')
                    album_name = ' '.join([x for x in title.split(
                        ' ') if x and (is_title(x) or len(x) < 4)])
                    if album_name not in albums:
                        albums.append(
                            {'album': album_name, 'release_years': year})
    return albums


def get_results_from_wiki():
    res = []
    for page in actual_data:
        doc = nlp(page)
        albums = get_album_data_from_wiki_page(doc)
        for album in albums:
            existing = next((x for x in res if x['album'] == album['album']
                             and x['release_years'] != album['release_years']), None)
            if existing:
                existing['release_years'] = f"{existing['release_years']}|{album['release_years']}"
            res.append(album)
    return sorted(res, key=lambda i: i['release_years'])


def get_match_results(dbpedia_data, wiki_data):
    match = []
    for exp in dbpedia_data:
        for wd in wiki_data:
            if exp['album'] == wd['album'] and wd['album'] not in [x['album'] for x, _ in match]:
                exp_years = exp['release_years'].split('|')
                act_years = wd['release_years'].split('|')
                if exp_years == act_years:
                    match.append((wd, 1))
                else:
                    weight = round(
                        len([x for x in act_years if x in exp_years])/len(exp_years), 2)
                    match.append((wd, weight))
    matched_album_names = [x['album'] for x, _ in match]
    false_pos = [x for x in wiki_data if x['album'] not in matched_album_names]
    false_neg = [x for x in dbpedia_data if x['album']
                 not in matched_album_names]

    match_score = sum([w for _, w in match])/len(match)

    return {
        'matched_perc': round(len(matched_album_names)/len(dbpedia_data) * match_score, 2),
        'recall': round(len(matched_album_names)/(len(matched_album_names) + len(false_neg)), 2),
        'precicion': round(len(matched_album_names)/(len(matched_album_names) + len(false_pos)), 2),
        'false_pos_list': false_pos,
        'false_neg_list': false_neg,
    }


band_page_content = get_page_content('Black_Sabbath')

all_q_data = [x for x in dbpedia_data['results']['bindings']]
album_uris = [x['album_uri']['value'] for x in all_q_data]
album_pages_content = [get_page_content(
    x.rsplit('/', 1)[-1]) for x in album_uris]

actual_data = album_pages_content
actual_data.append(band_page_content)
expected_data = [{k: v['value'] for k, v in x.items() if k != 'album_uri'}
                 for x in all_q_data]


wiki_data = get_results_from_wiki()

res = get_match_results(expected_data, wiki_data)
print(res)
