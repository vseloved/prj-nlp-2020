import json

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

import stanza


from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier

from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score

stanza.download('uk')
nlp = stanza.Pipeline('uk')

TRAINING_SET_PATH = "../data/datasets/training_set.json"
LEMMATIZED_TRAINING_SET_PATH = "../data/datasets/lemmatized_training_set.json"
TOKENIZED_TRAINING_SET_PATH = "../data/datasets/tokenized_training_set.json"

EVAL_SET_PATH = "../data/datasets/eval_set.json"
LEMMATIZED_EVAL_SET_PATH = "../data/datasets/processed_eval_set.json"
TOKENIZED_EVAL_SET_PATH = "../data/datasets/processed_eval_set.json"

def get_lemmas(text):
    doc = nlp(text)
    lemmas = []
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.pos != 'PUNCT':
                lemmas.append(word.lemma)
    return " ".join(lemmas)

def get_tokens(text):
    return text


def recalculate_lemmatized_dataset(inbound_data_path, outbound_data_path):
    dataset = {}

    with open(inbound_data_path) as json_file:
        data = json.load(json_file)

    training_data = []
    training_targets = []

    for item in data:
        rating = item[0]
        text = item[1]
        lemmas = get_lemmas(text)
        training_targets.append(rating)
        training_data.append(lemmas)

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

    for item in data:
        rating = item[0]
        text = item[1]
        tokens = get_tokens(text)
        training_targets.append(rating)
        training_data.append(tokens)

    dataset['training_data'] = training_data
    dataset['training_targets'] = training_targets

    with open(outbound_data_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)

def load_dataset(inbound_data_path):
    with open(inbound_data_path) as json_file:
        return json.load(json_file)

if __name__ == '__main__':

    # uncomment to generate lemmatized data files for iteration 2
    # recalculate_lemmatized_dataset(TRAINING_SET_PATH, LEMMATIZED_TRAINING_SET_PATH)
    # recalculate_lemmatized_dataset(EVAL_SET_PATH, LEMMATIZED_EVAL_SET_PATH)

    # uncomment to generate tokenized data files for iteration 1
    # recalculate_tokenized_dataset(TRAINING_SET_PATH,TOKENIZED_TRAINING_SET_PATH)
    # recalculate_tokenized_dataset(EVAL_SET_PATH,TOKENIZED_EVAL_SET_PATH)

    training_data = load_dataset(TOKENIZED_TRAINING_SET_PATH)
    eval_data = load_dataset(TOKENIZED_EVAL_SET_PATH)

    training_dataset = {}
    eval_dataset = {}

    training_dataset['training_data'] = training_data['training_data']
    training_dataset['training_targets'] = training_data['training_targets']

    eval_dataset['training_data'] =  eval_data['training_data']
    eval_dataset['training_targets'] = eval_data['training_targets']

    naive_bayes = MultinomialNB()
    svm = SGDClassifier(loss='hinge', penalty='l2', alpha = 0.0001, random_state = 42,max_iter = 5, tol = None)


    text_clf_bayes = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', naive_bayes)])

    text_clf_svm = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', svm)])

    scores = cross_val_score(text_clf_svm, training_dataset['training_data'], training_dataset['training_targets'], cv=5, scoring='f1_macro')
    print('SGDClassifier', scores)
    print('SGDClassifier, average', np.average(scores))

    text_clf_svm.fit(training_data['training_data'], training_data['training_targets'])

    predicted = text_clf_svm.predict(eval_dataset['training_data'])

    print(classification_report(eval_dataset['training_targets'], predicted))