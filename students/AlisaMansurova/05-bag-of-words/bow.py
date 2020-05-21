import json
import os
import pprint
from math import log
from collections import Counter
from random import shuffle
from langdetect import detect
import tokenize_uk
import pymorphy2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_validate
from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score

morph = pymorphy2.MorphAnalyzer(lang='uk')


absDir = os.path.dirname(os.path.abspath(__file__))
data_file_name = './rozetka_uk.json'
data_file = os.path.join(absDir, data_file_name)

with open(data_file) as f:
    ukr_reviews = json.load(f)


class NaiveBayesClassifier:
    def __init__(self, text_processor):
        self.text_processor = text_processor

    def get_features(self):
        feature_words = []

        for review in self.X_data:
            processed = self.text_processor(review['text'])

            for word in processed:
                if word not in feature_words:
                    feature_words.append(word)

        features = {x: i for i, x in enumerate(feature_words)}
        features.update({'UNK': len(features)})

        self.features = features

        return features

    def get_senses(self):
        pos = []
        neg = []
        neut = []

        for review in self.X_data:
            text = self.text_processor(review['text'])
            sens = review['sens']

            if sens == 'neut':
                for t in text:

                    word = t
                    neut.append(word)
            elif sens == 'pos':
                for t in text:
                    word = t
                    pos.append(word)
            else:
                for t in text:
                    word = t
                    neg.append(word)
        return pos, neg, neut

    def get_feature_counts_by_class(self):
        pos, neg, neut = self.get_senses()
        features = self.get_features()

        count = {'pos': [], 'neg': [], 'neut': []}
        cnt_pos = Counter(pos)
        cnt_neg = Counter(neg)
        cnt_neut = Counter(neut)

        for w in features.keys():
            pos_c = cnt_pos[w]
            neg_c = cnt_neg[w]
            neut_c = cnt_neut[w]
            count['pos'].append(pos_c)
            count['neg'].append(neg_c)
            count['neut'].append(neut_c)
        return count

    def get_feature_weights_by_class(self):
        res = {}
        feat_counts = self.get_feature_counts_by_class()

        for k, v in feat_counts.items():
            res[k] = [log(x/len(v)) if x else log(0.1/len(v)) for x in v]
        return res

    def calculate_bias_by_class(self):
        pos = 0
        neg = 0
        neut = 0
        all_count = len(self.X_data)

        for review in self.X_data:
            sens = review['sens']

            if sens == 'neut':
                neut += 1
            elif sens == 'pos':
                pos += 1
            else:
                neg += 1

        return {'pos': round(log(pos/all_count), 4),
                'neg': round(log(neg/all_count), 4),
                'neut': round(log(neut/all_count), 4)
                }

    def predict_class(self, text, weights, bias):
        text_words = self.text_processor(text)
        features = self.features

        p_pos = bias['pos'] + sum(weights['pos'][features.get(
            word, features['UNK'])] for word in text_words)
        p_neg = bias['neg'] + sum(weights['neg'][features.get(
            word, features['UNK'])] for word in text_words)
        p_neut = bias['neut'] + sum(weights['neut'][features.get(
            word, features['UNK'])] for word in text_words)

        p_dict = {'pos': p_pos, 'neg': p_neg, 'neut': p_neut}

        return max(p_dict, key=p_dict.get)

    def fit(self, X_data):
        self.X_data = X_data
        self.bias = self.calculate_bias_by_class()
        self.weights = self.get_feature_weights_by_class()

    def predict(self, y_data):
        res = []

        for review in y_data:
            text = review['text']
            pros = review.get('pros', '')
            cons = review.get('cons', '')
            all_text = text + pros + cons
            res.append(self.predict_class(all_text, self.weights, self.bias))
        return res


def get_corpus(reviews):
    res = []
    for review in reviews:
        rating = review['rating']
        text = review['text']
        pros = review.get('pros')
        cons = review.get('cons')
        
        neut_texts = ['не знаю', 'незнаю', 'не купив', 'не купила',
            'час покаже', 'поки не', 'ще не', 'поки що не', 'трохи', 'трошки', 'але '
            ]
        
        rev_pros = None
        rev_neut = None
        rev_cons = None

        rev_text = {'text': text}
        if pros:
            if any([x for x in neut_texts if x in pros.lower()]):
                rev_neut = {'text': pros, 'sens': 'neut'}
            else:
                rev_pros = {'text': pros, 'sens': 'pos'}
        if cons:
            if any([x for x in neut_texts if x in cons.lower()]):
                rev_neut = {'text': cons, 'sens': 'neut'}
            else:
                rev_cons = {'text': cons, 'sens': 'neg'}

        if rating:
            if rating == 5:
                rev_text['sens'] = 'pos'
            elif rating >= 3:
                rev_text['sens'] = 'neut'
            else:
                rev_text['sens'] = 'neg'
            res.append(rev_text)

        if rev_pros:
            res.append(rev_pros)

        if rev_cons:
            res.append(rev_cons)
            
        if rev_neut:
            res.append(rev_neut)

    pos = [x for x in res if x['sens'] == 'pos']
    neg = [x for x in res if x['sens'] == 'neg']
    neut = [x for x in res if x['sens'] == 'neut']
    print('>> pos', len(pos))
    print('>> neg', len(neg))
    print('>> neut', len(neut))

    res_all = pos + neg + neut
    shuffle(res_all)
    return res_all


def divide_data(data):
    data_len = int(len(data) * 0.7)
    return data[:data_len], data[data_len:]


""" text processors START """


def tokenize_text(text):
    return tokenize_uk.tokenize_uk.tokenize_words(text)


def lowerize_text(text):
    return [word.lower() for word in tokenize_text(text)]


def _lemmatize(text):
    res = []
    for word in tokenize_text(text):
        m_word = morph.parse(word)[0]
        res.append((m_word.normal_form, m_word))
    return res


def lemmatize_text(text):
    return [x for x, _ in _lemmatize(text)]


def filterize_text(text):
    res = []
    lemmatized = _lemmatize(text)

    symbols = ['-', '+', ':', '<', '>', '&']
    invalid_pos = ['CONJ', 'INTJ', 'PREP', 'NPRO']
    invalid_non_oc_pos = ['NUMB,intg', 'NUMB,real', 'ROMN', 'PNCT', 'LATN']

    for word, m_word in lemmatized:
        if len(word) and str(m_word.tag) not in invalid_non_oc_pos and \
                m_word.tag.POS not in invalid_pos and \
                word not in symbols:
            res.append(word)

    return res


def negatiaze_text(text):
    res = []
    words = filterize_text(text)

    for i, word in enumerate(words):
        p = morph.parse(word)[0]
        if (p.tag.POS == 'ADJF' or p.tag.POS == 'VERB' or p.tag.POS == 'INFN') \
                and words[i-1] == 'не':
            res.append(f'не_{word}')
        else:
            res.append(word)

    return res


def ngrammaze_text(text, additional_preproc=None):
    if additional_preproc:
        words = ' '.join(additional_preproc(text))
    else:
        words = text
    return [words[i:i + 3] if i > 0 else '^' + words[i:i + 3] for i in range(0, len(words), 1)]


""" text processors END """


def get_X(reviews):
    return [x['text'] for x in reviews]


def get_y(reviews):
    return [x['sens'] for x in reviews]


def get_classification_report(preprocess_fn, train_data, test_data, y_target):
    cls = NaiveBayesClassifier(preprocess_fn)
    cls.fit(train_data)
    test_predict = cls.predict(test_data)
    print(classification_report(y_target, test_predict))


def get_cross_validation_report(preprocess_fn, X_train, y_train):
    vect = CountVectorizer(tokenizer=preprocess_fn)
    cls_1 = Pipeline([('vect', vect), ('cls', MultinomialNB())])
    scoring = {'accuracy': make_scorer(accuracy_score),
               'precision_pos': make_scorer(precision_score, average=None, labels=['pos']),
               'precision_neut': make_scorer(precision_score, average=None, labels=['neut']),
               'precision_neg': make_scorer(precision_score, average=None, labels=['neg']),
               'precision_macro': make_scorer(precision_score, average='macro'),
               'precision_weighted': make_scorer(precision_score, average='weighted'),
               'recall_pos': make_scorer(recall_score, average=None, labels=['pos']),
               'recall_neut': make_scorer(recall_score, average=None, labels=['neut']),
               'recall_neg': make_scorer(recall_score, average=None, labels=['neg']),
               'recall_macro': make_scorer(recall_score, average='macro'),
               'recall_weighted': make_scorer(recall_score, average='weighted'),
               'f1_pos': make_scorer(f1_score, average=None, labels=['pos']),
               'f1_neut': make_scorer(f1_score, average=None, labels=['neut']),
               'f1_neg': make_scorer(f1_score, average=None, labels=['neg']),
               'f1_macro': make_scorer(f1_score, average='macro'),
               'f1_weighted': make_scorer(f1_score, average='weighted'),
               }
    res = cross_validate(cls_1, X_train, y_train, scoring=scoring)
    
    def get_score(field):
        return round(res[field].mean(), 2)
    
    accuracy = get_score('test_accuracy')
    precision_pos = get_score('test_precision_pos')
    precision_neut = get_score('test_precision_neut')
    precision_neg = get_score('test_precision_neg')
    recall_pos = get_score('test_recall_pos')
    recall_neut = get_score('test_recall_neut')
    recall_neg = get_score('test_recall_neg')
    f1_pos = get_score('test_f1_pos')
    f1_neut = get_score('test_f1_neut')
    f1_neg = get_score('test_f1_neg')
    precision_macro = get_score('test_precision_macro')
    precision_weighted = get_score('test_precision_weighted')
    recall_macro = get_score('test_recall_macro')
    recall_weighted = get_score('test_recall_weighted')
    f1_macro = get_score('test_f1_macro')
    f1_weighted = get_score('test_f1_weighted')

    scores = ['precision', 'recall', 'f1-score']
    labels = ['pos', 'neut', 'neg', '', 'accuracy', 'macro avg', 'weighted avg']

    data = np.array([[precision_pos, recall_pos, f1_pos],
                     [precision_neut, recall_neut, f1_neut],
                     [precision_neg, recall_neg, f1_neg],
                     ['', '', ''],
                     ['', '', accuracy],
                     [precision_macro, recall_macro, f1_macro],
                     [precision_weighted, recall_weighted, f1_weighted],
                     ])
    print(pandas.DataFrame(data, labels, scores))

# main


corpus = get_corpus(ukr_reviews)

train_data, test_data = divide_data(corpus)
X_train = get_X(train_data)
X_test = get_X(test_data)
y_train = get_y(train_data)
y_target = get_y(test_data)

# use custom NaiveByasClassifier; example for tokenize_text preprocessor
get_classification_report(tokenize_text)

# use MultinomialNB; example for tokenize_text preprocessor
get_cross_validation_report(tokenize_text)
