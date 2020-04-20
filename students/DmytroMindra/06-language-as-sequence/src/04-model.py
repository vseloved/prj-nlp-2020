import json

import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


TOKENS_FILENAME = '../data/tokens_dataset.json'
LABELS_FILENAME = '../data/labels_dataset.json'
RUN_ON_TEST_FILENAME = '../../../../tasks/06-language-as-sequence/run-on-test.json'
NGRAMS_FILENAME = '../data/ngrams.json'


RUN_ON_TEST_TOKENS_FILENAME = '../data/run_on_test_tokens_dataset.json'
RUN_ON_TEST_LABELS_FILENAME = '../data/run_on_test_labels_dataset.json'



def top_features(vectorizer, clf, n):
    """Prints features with the highest coefficient values, per class"""
    feature_names = vectorizer.get_feature_names()
    for i, class_label in enumerate(clf.classes_):
        top = np.argsort(clf.coef_[i])
        reversed_top = top[::-1]
        print("%s: %s\n" % (class_label,
                            " ".join(feature_names[j] for j in reversed_top[:n])))


def add_ngram_data(token, ngrams):
    text = token['text']
    next = token['right_token']

    text_freq = 1
    next_freq = 1

    if text.lower() in ngrams:
        text_freq = ngrams[text.lower()]

    if next.lower() in ngrams['<S>']:
        next_freq = ngrams['<S>'][next.lower()]

    token['ngram'] = text_freq/next_freq

if __name__ == "__main__":
    tokens_data = []
    labels_data = []

    run_on_tokens_data = []
    run_on_labels_data = []

    ngrams = None

    with open(NGRAMS_FILENAME) as json_file:
        ngrams = json.load(json_file)

    with open(RUN_ON_TEST_TOKENS_FILENAME) as json_file:
        for sentence in json.load(json_file):
            for token in sentence:
                run_on_tokens_data.append(token)

    with open(RUN_ON_TEST_LABELS_FILENAME) as json_file:
        for sentence in json.load(json_file):
            for label in sentence:
                run_on_labels_data.append(label)


    with open(TOKENS_FILENAME) as json_file:
        for sentence in json.load(json_file):
            for token in sentence:
   #             add_ngram_data(token, ngrams)
                tokens_data.append(token)


    #with open(RUN_ON_TEST_LABELS_FILENAME) as json_file:
    with open(LABELS_FILENAME) as json_file:
        for sentence in json.load(json_file):
            for label in sentence:
                labels_data.append(label)


    total_size = len(tokens_data)
    trainset_size = round(len(tokens_data) * 0.7)
    testset_size = total_size - trainset_size
    print('trainset size', trainset_size)
    print('evalset size', testset_size)

    train_features = tokens_data[:trainset_size]
    test_features = tokens_data[trainset_size:]

    print ('train features', len(train_features))
    print('test features', len(test_features))

    train_labels = labels_data[:trainset_size]
    test_labels = labels_data[trainset_size:]

    vectorizer = DictVectorizer()
    vec = vectorizer.fit(train_features)
    print("Total number of features: ", len(vec.get_feature_names()))

    train_features_vectorized = vec.transform(train_features)
    test_features_vectorized = vec.transform(test_features)
    run_on_features_vectorized = vec.transform(run_on_tokens_data)

    lrc = LogisticRegression(random_state=42, solver="sag", multi_class="multinomial",
                             max_iter=100, verbose=1)
    lrc.fit(train_features_vectorized, train_labels)

    #top_features(vec, lrc, 20)




    predicted_labels = lrc.predict(run_on_features_vectorized)
    print(classification_report(run_on_labels_data, predicted_labels))
