import json
import urllib
import requests
import os
import hashlib
from sklearn.metrics import classification_report
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import en_core_web_md
from nltk.stem.porter import PorterStemmer

nlp = en_core_web_md.load()


def filter_unknowns(data):
    return [x for x in data if x['gold_label'] != '-']


with open('../../../../../corpora/snli_1.0/snli_1.0_train.jsonl') as f:
    train_data = filter_unknowns([json.loads(line) for line in f.readlines()])

with open('../../../../../corpora/snli_1.0/snli_1.0_dev.jsonl') as f:
    dev_data = filter_unknowns([json.loads(line) for line in f.readlines()])

with open('../../../../../corpora/snli_1.0/snli_1.0_test.jsonl') as f:
    test_data = filter_unknowns([json.loads(line) for line in f.readlines()])


''' Utils '''


def compose(*funcs):
    def inner(*arg):
        res = {}
        for f in funcs:
            res.update(f(*arg))
        return res
    return inner


def filter_stop_words(doc):
    return [x for x in doc if not (x.pos_ == 'DET' or x.pos_ == 'NUM'
                                   or x.is_stop and x.dep_ != 'ROOT')]


def normalize_sent(func):
    def inner(s1, s2):
        return func(filter_stop_words(s1), filter_stop_words(s2))
    return inner


def get_classifier():
    pipe = Pipeline([
        ('dict_vect', DictVectorizer()),
        ('lrc', LogisticRegression(random_state=42, multi_class='multinomial',
                                   max_iter=100, solver='sag', n_jobs=-1))])

    return pipe


def get_intersection(ents1, ents2):
    setA = set(ents1)
    setB = set(ents2)
    universe = setA | setB
    if not setB:
        return 'NONE'

    return len(setA & setB)/(len(setB))


def get_tokens_similarity(toks1, toks2):
    setA = set(toks1)
    setB = set(toks2)
    universe = set(toks1) | set(toks2)
    sim = [x.similarity(y)
           for x in setA for y in setB if x.has_vector and y.has_vector]
    return len(sim)/(len(universe))


def get_ngrams(text):
    res = []
    for i in range(0, len(text), 3):
        if i > 0 and i + 3 <= len(text):
            res.append(text[i:i + 3])
        elif i > 0 and i + 3 > len(text):
            res.append(text[i:i + 3] + '</S>')
        else:
            res.append('<S>' + text[i:i + 3])
    return res


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


''' Working with concepts'''


def get_concepts_for_roots(data):
    ex_conc = []

    def get_concepts_for_sent(sent):
        s_conc = None
        if os.path.isfile('./concs.txt'):
            with open('./concs.txt') as f:
                ex_conc = [x.rstrip() for x in f.readlines()]
        else:
            ex_conc = []
        for tok in nlp(sent):
            if tok.lemma_ not in ex_conc and tok.dep_ == 'ROOT':
                s_conc = get_concepts(tok.lemma_)['edges']
                with open('./concs.txt', 'a') as f:
                    f.write(tok.lemma_ + '\n')
                ex_conc.append(tok.lemma_)

        return s_conc

    conc = []
    for i, item in enumerate(data):
        conc.append(get_concepts_for_sent(item['sentence1']))
        conc.append(get_concepts_for_sent(item['sentence2']))
    return conc


def get_concepts(concept):
    offset = 0
    req = requests.get('http://api.conceptnet.io/c/en/' +
                       concept + '?offset=' + str(offset) + '&limit=100').json()
    all_edges = req
    return all_edges


def get_conc(data, path):
    valid_relations = ['Synonym', 'RelatedTo', 'FormOf', 'IsA', 'PartOf', 'UsedFor', 'CapableOf',
                       'Antonym', 'DefinedAs', 'SimilarTo', 'EtymologicallyRelatedTo',
                       'ReceivesAction']
    if not os.path.isdir(path):
        os.mkdir(path)
    chunk = list(chunks(data, 500))
    i = 0
    for ch in chunk:
        train_conc_root = get_concepts_for_roots(ch)
        with open(f'./{path}/{i}.json', 'w') as f:
            non_null = [x for x in train_conc_root if x]
            filtered = [x for conc in non_null for x in conc if x['rel']['label'] in valid_relations
                        and x['start']['language'] == 'en' and x['end']['language'] == 'en']
            json.dump(filtered, f)
            i += 1


def merge_concepts(dirs):
    res = []
    for d in dirs:
        files = os.listdir(d)
        for file in files:
            with open(os.path.join(d, file)) as f:
                cont = json.load(f)
                res += cont
    return res


def normalize_concepts(concepts):
    res = []
    for concept in concepts:
        if concept['start']['language'] == 'en':
            res.append({concept['start']['label'].lower(): concept})
    return res


def get_concepts_local(word):
    all_concepts = merge_concepts(['train_conc', 'dev_conc', 'test_conc'])
    normalized = normalize_concepts(all_concepts)
    return [v for dic in normalized for k, v in dic.items() if k == word]


# with open('./all_concepts.json', 'w') as f:
#     all_concepts = merge_concepts(['train_conc', 'dev_conc', 'test_conc'])
#     normalized = normalize_concepts(all_concepts)
#     json.dump(normalized, f)


def get_rels(word):
    concepts = get_concepts_local(word)

    synonyms = []
    related = []
    forms = []
    hyponyms = []
    meronyms = []
    holonyms = []
    capabilities = []
    causes = []
    antonyms = []
    meanings = []
    similarities = []
    common_origins = []
    can_be_done_to = []

    def _check_rel(rel_type, rel_list):
        if concept['rel']['label'] == rel_type:
            lab = concept['end']['label']
            if lab not in rel_list:
                rel_list.append(lab)

    for concept in concepts:
        _check_rel('Synonym', synonyms)
        _check_rel('RelatedTo', related)
        _check_rel('FormOf', forms)
        _check_rel('IsA', hyponyms)
        _check_rel('PartOf', meronyms)
        _check_rel('UsedFor', holonyms)
        _check_rel('CapableOf', capabilities)
        _check_rel('Antonym', antonyms)
        _check_rel('DefinedAs', meanings)
        _check_rel('SimilarTo', similarities)
        _check_rel('EtymologicallyRelatedTo', common_origins)
        _check_rel('ReceivesAction', can_be_done_to)

    return {
        'synonyms': synonyms,
        'related': related,
        'forms': forms,
        'hyponyms': hyponyms,
        'meronyms': meronyms,
        'holonyms': holonyms,
        'capabilities': capabilities,
        'antonyms': antonyms,
        'meanings': meanings,
        'similarities': similarities,
        'common_origins': common_origins,
        'can_be_done_to': can_be_done_to,
    }


''' Feature extractors '''


def feature_extractor_base(doc1, doc2):
    feats = {}
    feats['similarity'] = doc1.similarity(doc2)

    return feats


@normalize_sent
def feature_extractor_ner(doc1, doc2):
    def _inner(doc):
        return [x.ent_type_ for x in doc]
    feats = {}

    feats['ner'] = get_intersection(_inner(doc1), _inner(doc2))

    return feats


@normalize_sent
def feature_extractor_word(doc1, doc2):
    def _lemm(doc):
        return [x.lemma_ for x in doc]

    def _noun(doc):
        return [x.lemma_ for x in doc if x.pos_ == 'NOUN']

    def _verb(doc):
        return [x.lemma_ for x in doc if x.pos_ == 'VERB']

    feats = {}

    feats['lemma'] = get_intersection(_lemm(doc1), _lemm(doc2))
    feats['noun'] = get_intersection(_noun(doc1), _noun(doc2))
    feats['verb'] = get_intersection(_verb(doc1), _verb(doc2))

    return feats


@normalize_sent
def feature_extractor_spacy_sim(doc1, doc2):
    feats = {}

    feats['similar'] = get_tokens_similarity(doc1, doc2)

    return feats


@normalize_sent
def feature_extractor_ngrams(doc1, doc2):
    def _ng_pos(doc):
        return get_ngrams(' '.join([x.pos_ for x in doc]))

    def _ng_dep(doc):
        return get_ngrams(' '.join([x.dep_ for x in doc]))

    def _ng_lemma(doc):
        return get_ngrams(' '.join([x.lemma_ for x in doc]))

    feats = {}

    feats['ngr-pos'] = get_intersection(_ng_pos(doc1), _ng_pos(doc2))
    feats['ngr-dep'] = get_intersection(_ng_dep(doc1), _ng_dep(doc2))
    feats['ngr-lemma'] = get_intersection(_ng_lemma(doc1), _ng_lemma(doc2))

    return feats


@normalize_sent
def feature_extractor_stemm(doc1, doc2):
    stemmer = PorterStemmer()

    def _stem_v(doc):
        return [stemmer.stem(x.text) for x in doc if x.pos_ == 'VERB']

    def _stem_n(doc):
        return [stemmer.stem(x.text) for x in doc if x.pos_ == 'NOUN']

    feats = {}

    feats['stemm-v'] = get_intersection(_stem_v(doc1), _stem_v(doc2))
    feats['stemm-n'] = get_intersection(_stem_n(doc1), _stem_n(doc2))

    return feats


@normalize_sent
def feature_extractor_neg(doc1, doc2):
    def _get_neg(doc):
        neg = ['not', 'n\'t', 'neither', 'nor', 'never', 'none', 'nowhere']
        neg_processed = []
        neg_ind = 100500
        for tok in doc:
            if tok.lower_ in neg:
                neg_ind = tok.i
            elif tok.pos_ == 'PUNCT':
                neg_ind = 100500
                neg_processed.append(tok.lemma_)
            elif tok.i > neg_ind:
                neg_processed.append('NOT_' + tok.lemma_)
            else:
                neg_processed.append(tok.lemma_)
        return neg_processed

    feats = {}
    feats['neg'] = get_intersection(_get_neg(doc1), _get_neg(doc2))
    return feats


def feature_extractor_deps(doc1, doc2):
    def _inner_1(doc):
        return [x.dep for x in doc]

    def _inner_2(doc):
        return [x.head.dep for x in doc]

    feats = {}

    feats['dep'] = get_intersection(_inner_1(doc1), _inner_1(doc2))
    feats['head-dep'] = get_intersection(_inner_2(doc1), _inner_2(doc2))

    return feats


def feature_extractor_semant(cache):
    def inner(doc1, doc2):
        feats = {}

        def _get_rels(doc):
            for tok in doc:
                if tok.dep_ == 'ROOT':
                    if tok.lemma_ not in cache:
                        rels = get_rels(tok.lemma_)
                        cache[tok.lemma_] = rels
                        return rels
                    else:
                        return cache[tok.lemma_]

        rels1 = _get_rels(doc1)
        rels2 = _get_rels(doc2)
        root1_tok = [x for x in doc1 if x.dep_ == 'ROOT'][0]
        root2_tok = [x for x in doc2 if x.dep_ == 'ROOT'][0]
        root1 = root1_tok.lemma_
        root2 = root2_tok.lemma_

        neg = ['not', 'n\'t', 'neither', 'nor', 'never', 'none', 'nowhere']

        feats['syn'] = len([x for x in set(rels2['synonyms'])
                            if x == root1 and doc2[root2_tok.i - 1].text not in neg]) + \
            len([x for x in set(rels1['synonyms'])
                 if x == root2 and doc1[root1_tok.i - 1].text not in neg])
        feats['mean'] = len([x for x in set(rels2['meanings'])
                             if x == root1 or x in rels1['meanings']])
        feats['sim'] = len(
            [x for x in set(rels2['similarities']) if x == root1])
        feats['form'] = len([x for x in set(rels2['forms'])
                             if x == root1 or x in rels1['forms']])
        feats['ant'] = len(
            [x for x in set(rels2['antonyms']) if x in rels1['antonyms']])

        return feats
    return inner


''' Reporting '''


clf = get_classifier()


def get_data(docs, raw_data, feature_extractor):
    features = []
    labels = []

    for i, doc_pair in enumerate(docs):
        nlp1, nlp2 = doc_pair

        features.append(feature_extractor(nlp1, nlp2))
        labels.append(raw_data[i]['gold_label'])

    return features, labels


def print_result(train_docs, test_docs, train_raw_data, test_raw_data, feature_extractor):
    X_train, y_train = get_data(train_docs, train_raw_data, feature_extractor)
    X_dev, y_dev = get_data(test_docs, test_raw_data, feature_extractor)
    clf.fit(X_train, y_train)
    print(classification_report(y_dev, clf.predict(X_dev)))


''' Optimization helpers '''


def get_nlps(data):
    docs = []
    for i, sent in enumerate(data):
        docs.append((nlp(sent['sentence1']), nlp(sent['sentence2'])))
    return docs


''' Main '''
train_docs = get_nlps(train_data)
dev_docs = get_nlps(dev_data)
test_docs = get_nlps(test_data)

# baseline
print_result(train_docs, test_docs, train_data,
             test_data, feature_extractor_base)

# it 1
feature_extractor = compose(feature_extractor_base, feature_extractor_ner)
print_result(train_docs, test_docs, train_data, test_data, feature_extractor)

# ut 2
feature_extractor = compose(feature_extractor_base,
                            feature_extractor_word)
print_result(train_docs, test_docs, train_data, test_data, feature_extractor)

# it 3
feature_extractor = compose(feature_extractor_base,
                            feature_extractor_word,
                            feature_extractor_ngrams,
                            )
print_result(train_docs, test_docs, train_data, test_data, feature_extractor)

# it 4
feature_extractor = compose(feature_extractor_base,
                            feature_extractor_word,
                            feature_extractor_ngrams,
                            feature_extractor_neg
                            )
print_result(train_docs, test_docs, train_data, test_data, feature_extractor)

# it 5
feature_extractor = compose(feature_extractor_base,
                            feature_extractor_word,
                            feature_extractor_ngrams,
                            feature_extractor_deps
                            )
print_result(train_docs, test_docs, train_data, test_data, feature_extractor)

# it 6
feature_extractor = compose(feature_extractor_base,
                            feature_extractor_word,
                            feature_extractor_ngrams,
                            feature_extractor_deps,
                            feature_extractor_stemm
                            )
print_result(train_docs, test_docs, train_data, test_data, feature_extractor)

# it 7
feature_extractor = compose(feature_extractor_base,
                            feature_extractor_word,
                            feature_extractor_ngrams,
                            feature_extractor_deps,
                            feature_extractor_semant({})
                            )
print_result(train_docs, test_docs, train_data, test_data, feature_extractor)

# it 8
feature_extractor = compose(feature_extractor_base,
                            feature_extractor_word,
                            feature_extractor_ngrams,
                            feature_extractor_deps,
                            feature_extractor_spacy_sim,
                            )
print_result(train_docs, test_docs, train_data, test_data, feature_extractor)
