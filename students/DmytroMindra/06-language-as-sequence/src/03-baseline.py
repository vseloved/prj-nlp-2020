import json

import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

#
#
#

TOKENS_FILENAME = '../data/raw-data/tokens_dataset.json'
LABELS_FILENAME = '../data/raw-data/labels_dataset.json'
RUN_ON_TEST_FILENAME = '../../../../tasks/06-language-as-sequence/run-on-test.json'


def top_features(vectorizer, clf, n):
    """Prints features with the highest coefficient values, per class"""
    feature_names = vectorizer.get_feature_names()
    for i, class_label in enumerate(clf.classes_):
        top = np.argsort(clf.coef_[i])
        reversed_top = top[::-1]
        print("%s: %s\n" % (class_label,
                            " ".join(feature_names[j] for j in reversed_top[:n])))


if __name__ == "__main__":
    tokens_data = []
    labels_data = []

    run_on_tokens_data = []
    run_on_labels_data = []



    with open(RUN_ON_TEST_FILENAME) as json_file:
        for sentence in json.load(json_file):
            for token in sentence:
                run_on_tokens_data.append({'text': token[0]})
                run_on_labels_data.append(token[1])


    with open(TOKENS_FILENAME) as json_file:
        for sentence in json.load(json_file):
            for token in sentence:
                tokens_data.append(token)

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

    lrc = LogisticRegression(random_state=42, solver="sag", multi_class="multinomial",
                             max_iter=100, verbose=1)
    lrc.fit(train_features_vectorized, train_labels)

    #top_features(vec, lrc, 20)



    predicted_labels = lrc.predict(test_features_vectorized)
    print(predicted_labels[:10])

    print(classification_report(test_labels, predicted_labels))
