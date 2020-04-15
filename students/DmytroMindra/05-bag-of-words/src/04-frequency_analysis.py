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


nlp_was_initialized = False
nlp = None

TRAINING_SET_PATH = "../data/datasets/training_set.json"
LEMMATIZED_TRAINING_SET_PATH = "../data/datasets/lemmatized_training_set.json"
TOKENIZED_TRAINING_SET_PATH = "../data/datasets/tokenized_training_set.json"

EVAL_SET_PATH = "../data/datasets/eval_set.json"
LEMMATIZED_EVAL_SET_PATH = "../data/datasets/lemmatized_eval_set.json"
TOKENIZED_EVAL_SET_PATH = "../data/datasets/tokenized_eval_set.json"

TONE_DICT_PATH = "../data/tone-dict-uk.tsv"

def get_tone_dict():
    with open(TONE_DICT_PATH) as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in reader:
            print(row)


def initialize_nlp():
    global nlp_was_initialized
    global nlp

    if nlp_was_initialized:
        return
    stanza.download('uk')
    nlp = stanza.Pipeline('uk')
    nlp_was_initialized = True

def get_lemmas(text):
    doc = nlp(text)
    lemmas = []
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.pos != 'PUNCT':
                text = word.lemma
                lemmas.append(text)

    return " ".join(lemmas)


def get_tokens(text):
    return text


def recalculate_lemmatized_dataset(inbound_data_path, outbound_data_path):
    initialize_nlp()

    dataset = {}

    with open(inbound_data_path) as json_file:
        data = json.load(json_file)

    training_data = []
    training_targets = []

    print ("Recalculating lemmatized", outbound_data_path)
    counter = 0
    total = len(data)
    for item in data:
        rating = item[0]
        text = item[1]
        lemmas = get_lemmas(text)
        training_targets.append(rating)
        training_data.append(lemmas)
        counter+=1
        if counter%100 ==0:
            print (counter,'/',total)

    dataset['training_data'] = training_data
    dataset['training_targets'] = training_targets

    with open(outbound_data_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)


def recalculate_tokenized_dataset(inbound_data_path, outbound_data_path):
    dataset = {}

    with open(inbound_data_path) as json_file:
        data = json.load(json_file)

    training_data = []
    training_targets = []

    total = len(data)
    print ("Recalculating tokenized", outbound_data_path)
    counter = 0

    for item in data:
        rating = item[0]
        text = item[1]
        tokens = get_tokens(text)
        training_targets.append(rating)
        training_data.append(tokens)
        if counter%100 ==0:
            print (counter,'/',total)
        counter +=1

    dataset['training_data'] = training_data
    dataset['training_targets'] = training_targets

    with open(outbound_data_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)

def load_dataset(inbound_data_path):
    with open(inbound_data_path) as json_file:
        return json.load(json_file)

def execute_iteration(training_path, eval_path):
    training_data = load_dataset(training_path)
    eval_data = load_dataset(eval_path)

    training_dataset = {}
    eval_dataset = {}

    training_dataset['training_data'] = training_data['training_data']
    training_dataset['training_targets'] = training_data['training_targets']

    eval_dataset['training_data'] =  eval_data['training_data']
    eval_dataset['training_targets'] = eval_data['training_targets']

    sdgc = SGDClassifier(loss='hinge', penalty='l2', alpha = 0.0001, random_state = 42,max_iter = 5, tol = None)

    text_clf = Pipeline([
        ('vect', CountVectorizer(ngram_range=(1,2))),
        ('tfidf', TfidfTransformer()),
        ('clf', sdgc)])

    scores = cross_val_score(text_clf, training_dataset['training_data'], training_dataset['training_targets'], cv=5, scoring='f1_macro')
    print('', scores)
    print('average', np.average(scores))

    text_clf.fit(training_data['training_data'], training_data['training_targets'])
    predicted = text_clf.predict(eval_dataset['training_data'])
    print(classification_report(eval_dataset['training_targets'], predicted))

if __name__ == '__main__':

    # uncomment to generate lemmatized data files for iteration 2
    # print('recalculate lemmatized datasets')
    recalculate_lemmatized_dataset(TRAINING_SET_PATH, LEMMATIZED_TRAINING_SET_PATH)
    recalculate_lemmatized_dataset(EVAL_SET_PATH, LEMMATIZED_EVAL_SET_PATH)

    # uncomment to generate tokenized data files for iteration 1
    # print('recalculate tokenized datasets')
    # recalculate_tokenized_dataset(TRAINING_SET_PATH,TOKENIZED_TRAINING_SET_PATH)
    # recalculate_tokenized_dataset(EVAL_SET_PATH,TOKENIZED_EVAL_SET_PATH)

    print ('0: Baseline:')
    execute_iteration(TOKENIZED_TRAINING_SET_PATH, TOKENIZED_EVAL_SET_PATH)

    print ('1: Lemmatized')
    execute_iteration(LEMMATIZED_TRAINING_SET_PATH, LEMMATIZED_EVAL_SET_PATH)