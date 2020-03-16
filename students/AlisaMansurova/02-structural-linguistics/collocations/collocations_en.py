import en_core_web_md
import os

absDir = os.path.dirname(os.path.abspath(__file__))
data_dir = '../../../../tasks/02-structural-linguistics/data/'
tasksDir = os.path.join(absDir, data_dir)
BLOG_FILE = os.path.join(tasksDir, 'blog2008.txt')

nlp = en_core_web_md.load()

with open(BLOG_FILE) as f:
    corpus = f.readlines()

syns_row = ['say', 'tell', 'speak', 'claim', 'communicate',
            'state', 'talk', 'pronounce', 'enunciate', 'utter', 'verbalize']


def find_all_adv_ly_rec(children):
    for ch in children:
        if ch.pos_ == 'ADV' and ch.text.endswith('ly'):
            return ([ch.text.lower()] + find_all_adv_ly_rec(ch.children))
    return []


def find_ly_adv(doc):
    for token in doc:
        if token.pos_ == 'VERB' and token.lemma_ in syns_row:
            res = find_all_adv_ly_rec(token.children)
            if res:
                return (token.lemma_, res)


def order_advs(advs):
    with_freq = {x: advs.count(x) for x in advs}
    return sorted(with_freq.items(), key=lambda x: x[1], reverse=True)[:10]


def print_result(res):
    for verb in res.keys():
        print(f'{verb}: {str(order_advs(res[verb]))[1:-1]}')


def do_find(corpus):
    res = {}
    for sample in corpus:
        doc = nlp(sample)
        advs = find_ly_adv(doc)
        if advs:
            lemma, adv = advs
            if res.get(lemma):
                res[lemma] += adv
            else:
                res[lemma] = adv
    print_result(res)


def find_all_adv_debug(corpus, s, e):
    do_find(corpus[s:e])


def find_all_adv(corpus):
    do_find(corpus)


# main
find_all_adv(corpus)
