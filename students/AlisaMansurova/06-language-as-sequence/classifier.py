
import random
import os
import re
import json
import numpy as np
import spacy
import pandas
from functools import reduce
from sklearn.preprocessing import FunctionTransformer
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_validate, cross_val_predict
from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score

absDir = os.path.dirname(os.path.abspath(__file__))
train_tokens_file_name = './train_tokens.json'
train_tokens_file = os.path.join(absDir, train_tokens_file_name)
train_labels_file_name = './train_labels.json'
train_labels_file = os.path.join(absDir, train_labels_file_name)
ngrams_file_name = './trigrams.json'
ngrams_file = os.path.join(absDir, ngrams_file_name)


def get_classifier():
    pipe = Pipeline([
        ('dict_vect', DictVectorizer()),
        ('lrc', LogisticRegression(random_state=42, multi_class='multinomial',
                                   max_iter=100, solver='sag', n_jobs=50))])

    return pipe


def check_seq_in_ngrams(tokens, i, ngrams):
    token = tokens[i]
    next_token = tokens[i + 1] if i + 1 < len(tokens) else None

    for i, ngram in enumerate(ngrams):
        tks = ngram['tks']
        for i, t in enumerate(tks):
            if t['tg'] == 0 and t['tt'] == token and tks[i + 1]['tt'] == next_token:
                return ngram['sc']


""" start feature extractors"""


def word_feature_extractor(tokens, i):
    token = tokens[i]
    features = {}
    features['word'] = token.text
    return features


def adj_words_feature_extractor(tokens, i):
    token = tokens[i]
    features = {}

    tk_len = len(tokens)

    features['word-1'] = tokens[i - 1].text if i > 1 else '<S>'
    features['word-2'] = tokens[i - 1].text if i > 2 else '<S>'
    features['word+1'] = tokens[i + 1].text if i + 1 < tk_len else '<S>'
    features['word+2'] = tokens[i + 2].text if i + 2 < tk_len else '<S>'
    return features


def pos_feature_extractor(tokens, i):
    token = tokens[i]
    features = {}

    features['POS'] = token.pos_
    return features


def adj_pos_feature_extractor(tokens, i):
    token = tokens[i]
    features = {}

    tk_len = len(tokens)

    features['POS-1'] = tokens[i - 1].pos_ if i > 1 else 'NONE'
    features['POS-2'] = tokens[i - 2].pos_ if i > 2 else 'NONE'
    features['POS+1'] = tokens[i + 1].pos_ if i + 1 < tk_len else 'NONE'
    features['POS+2'] = tokens[i + 2].pos_ if i + 2 < tk_len else 'NONE'
    return features


def shape_feature_extractor(tokens, i):
    token = tokens[i]

    def get_shape(w):
        if w.isupper():
            return 'is_upper'
        elif w.istitle():
            return 'is_title'
        elif w.islower():
            return 'is_lower'
        elif w.isdigit():
            return 'is_digit'
        elif w.isalpha():
            return 'is_alpha'
        else:
            return 'other'

    features = {}

    tk_len = len(tokens)

    features['shape'] = get_shape(token.text)
    features['shape-1'] = get_shape(tokens[i - 1].text) if i > 1 else 'other'
    features['shape-2'] = get_shape(tokens[i - 2].text) if i > 2 else 'other'
    features['shape+1'] = get_shape(tokens[i +
                                           1].text) if i + 1 < tk_len else 'other'
    features['shape+2'] = get_shape(tokens[i +
                                           2].text) if i + 2 < tk_len else 'other'
    return features


def ngrams_feature_extractor(ngrams):
    def inner(tokens, i):
        token = tokens[i]
        features = {}

        features['seq_in_ngrams'] = check_seq_in_ngrams(tokens, i, ngrams)
        return features
    return inner


""" end feature extractors"""


def get_features(tokens, extractors):
    features = []
    seen_features = {}

    for i in range(len(tokens)):
        curr_token = tokens[i]
        if curr_token not in seen_features.keys():
            feat = {}
            for extractor in extractors:
                feat.update(extractor(tokens, i))
            seen_features[curr_token] = feat
            features.append(feat)
        else:
            features.append(seen_features[curr_token])
    return features


def get_cross_validation_report(cls, X_train, y_train):
    scoring = {'accuracy': make_scorer(accuracy_score),
               'precision_true': make_scorer(precision_score, average=None, labels=[True]),
               'precision_false': make_scorer(precision_score, average=None, labels=[False]),
               'precision_macro': make_scorer(precision_score, average='macro'),
               'precision_weighted': make_scorer(precision_score, average='weighted'),
               'recall_true': make_scorer(recall_score, average=None, labels=[True]),
               'recall_false': make_scorer(recall_score, average=None, labels=[False]),
               'recall_macro': make_scorer(recall_score, average='macro'),
               'recall_weighted': make_scorer(recall_score, average='weighted'),
               'f1_true': make_scorer(f1_score, average=None, labels=[True]),
               'f1_false': make_scorer(f1_score, average=None, labels=[False]),
               'f1_macro': make_scorer(f1_score, average='macro'),
               'f1_weighted': make_scorer(f1_score, average='weighted'),
               }
    res = cross_validate(cls, X_train, y_train, scoring=scoring)

    def get_score(field):
        return round(res[field].mean(), 2)

    accuracy = get_score('test_accuracy')
    precision_false = get_score('test_precision_false')
    precision_true = get_score('test_precision_true')
    recall_false = get_score('test_recall_false')
    recall_true = get_score('test_recall_true')
    f1_false = get_score('test_f1_false')
    f1_true = get_score('test_f1_true')
    precision_macro = get_score('test_precision_macro')
    precision_weighted = get_score('test_precision_weighted')
    recall_macro = get_score('test_recall_macro')
    recall_weighted = get_score('test_recall_weighted')
    f1_macro = get_score('test_f1_macro')
    f1_weighted = get_score('test_f1_weighted')

    scores = ['precision', 'recall', 'f1-score']
    labels = ['False', 'True', '', 'accuracy', 'macro avg', 'weighted avg']

    data = np.array([[precision_false, recall_false, f1_false],
                     [precision_true, recall_true, f1_true],
                     ['', '', ''],
                     ['', '', accuracy],
                     [precision_macro, recall_macro, f1_macro],
                     [precision_weighted, recall_weighted, f1_weighted],
                     ])
    print(pandas.DataFrame(data, labels, scores))


def get_cross_validation_result(cls, train_tokens, feature_extractors):
    train_features = get_features(train_tokens, feature_extractors)
    get_cross_validation_report(cls, train_features, train_labels)


# main
with open(train_tokens_file) as f:
    train_tokens = json.load(f)
with open(train_labels_file) as f:
    train_labels = json.load(f)
with open(ngrams_file) as f:
    ngrams = json.load(f)


train_features = get_features(train_tokens)
cls = get_classifier()

feature_extractors = [word_feature_extractor]
get_cross_validation_result(cls, train_tokens, feature_extractors)

feature_extractors.append(adj_words_feature_extractor)
get_cross_validation_result(cls, train_tokens, feature_extractors)

feature_extractors.append(pos_feature_extractor)
get_cross_validation_result(cls, train_tokens, feature_extractors)

feature_extractors.append(shape_feature_extractor)
get_cross_validation_result(cls, train_tokens, feature_extractors)
