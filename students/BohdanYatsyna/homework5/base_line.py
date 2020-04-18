from operator import itemgetter
import json
import csv

import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, HashingVectorizer

import stanza

from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.naive_bayes import MultinomialNB, GaussianNB

from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score

def load_dataset(inbound_data_path):
    with open(inbound_data_path) as json_file:
        return json.load(json_file)

dev_set = load_dataset('./cleaned_data/uk/dev_set.json')
test_set = load_dataset('./cleaned_data/uk/test_set.json')

dev_dataset = {}
test_dataset = {}
dev_dataset['data'] = list(map(itemgetter(0),dev_set))
dev_dataset['target'] = list(map(itemgetter(1),dev_set))

test_dataset['data'] = list(map(itemgetter(0),test_set))
test_dataset['target'] = list(map(itemgetter(1),test_set))


sdgc = SGDClassifier(loss="log", random_state = 42, tol = None)

print(dev_set)