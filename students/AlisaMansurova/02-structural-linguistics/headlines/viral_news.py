import en_core_web_md
import os
from nltk.corpus import sentiwordnet as swn

absDir = os.path.dirname(os.path.abspath(__file__))
data_dir = '../../../../tasks/02-structural-linguistics/data/'
tasksDir = os.path.join(absDir, data_dir)
EXAMINER_HEADLINES_FILE = os.path.join(tasksDir, 'examiner-headlines.txt')

nlp = en_core_web_md.load()

with open(EXAMINER_HEADLINES_FILE, 'r') as f:
    corpus = f.readlines()


def has_entities(doc):
    entities = ['ORG', 'PERSON', 'GPE', 'TIME', 'MONEY', 'PRODUCT']
    ents = [x.label_ in entities for x in doc.ents]
    return any(ents)


def get_syns_tag(univ_tag):
    if univ_tag == 'ADJ':
        return 'a'
    if univ_tag == 'NOUN':
        return 'n'
    if univ_tag == 'VERB':
        return 'v'
    if univ_tag == 'ADV':
        return 'r'

# FIXME: debug case with mom abuse


def get_sentiment(doc):
    pos_sum = 0.0
    neg_sum = 0.0

    for token in doc:
        pos = get_syns_tag(token.pos_)

        if pos:
            synsets = list(swn.senti_synsets(token.text, pos))
            pos_score = [x.pos_score() for x in synsets]
            neg_score = [x.neg_score() for x in synsets]
            if pos_score:
                pos_agv = sum(pos_score)/len(pos_score)
                if pos_agv > 0.5:
                    pos_sum += pos_agv
            if neg_score:
                neg_agv = sum(neg_score)/len(neg_score)
                if neg_agv > 0.5:
                    neg_sum += neg_agv

    if pos_sum or neg_sum:
        return pos_sum > neg_sum
    return None


def is_adj_or_adv_comp_sup(doc):
    return any((x.pos_ == 'ADJ' or x.pos_ == 'ADV')
               and x.text.lower() != x.lemma_.lower() for x in doc)


def do_count(corpus):
    all_ents = 0
    all_sents = 0
    all_super_adj = 0

    for sample in corpus:
        doc = nlp(sample)

        has_ents = has_entities(doc)
        sents = get_sentiment(doc)
        is_super_adj = is_adj_or_adv_comp_sup(doc)

        if has_ents:
            all_ents += 1
        if sents:
            all_sents += 1
        if is_super_adj:
            all_super_adj += 1
    res = {
        'entities': all_ents/len(corpus),
        'sentiment': all_sents/len(corpus),
        'is_super_adj': all_super_adj/len(corpus)
    }

    return res


def count_debug(corpus, s, e):
    return do_count(corpus[s:e])


def count_all(corpus):
    return do_count(corpus)


# main
print(count_all(corpus))
