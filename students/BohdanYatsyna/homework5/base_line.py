from operator import itemgetter
import json
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

import stanza

from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from time import time
from datetime import datetime


def load_dataset(inbound_data_path):
    with open(inbound_data_path) as json_file:
        return json.load(json_file)


# Пошук кращих параметрів для алгоритму
def benchmark(dev_dataset, test_dataset, pipeline, parameters, label=''):
    now = datetime.now()
    date_time = now.strftime("%m-%d-%Y__%H-%M-%S")
    with open('./iterations/' + pipeline[2].__class__.__name__ + '-' + label + '--' + date_time, 'w+') as f:
        grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1, verbose=1)

        print("Performing grid search...")
        print("pipeline:", [name for name, _ in pipeline.steps])
        print("pipeline:", [name for name, _ in pipeline.steps], file=f)
        print("\n", file=f)
        print(parameters, file=f)
        print("\n", file=f)

        print("parameters:")
        print(parameters)
        t0 = time()
        grid_search.fit(dev_dataset['data'], dev_dataset['target'])
        print("done in %0.3fs" % (time() - t0))
        print()
        print("Best score: %0.3f" % grid_search.best_score_)
        print("Best score: %0.3f" % grid_search.best_score_, file=f)
        print("Best parameters set:")
        best_parameters = grid_search.best_estimator_.get_params()
        for param_name in sorted(parameters.keys()):
            print("\t%s: %r" % (param_name, best_parameters[param_name]))
            print("\t%s: %r" % (param_name, best_parameters[param_name]), file=f)

        print("\n", file=f)

        predicted = grid_search.predict(test_dataset['data'])
        clf_repport = classification_report(test_dataset['target'], predicted)
        print(clf_repport)
        print(clf_repport, file=f)

### SGD
pipelineSGD = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier()),
])

# uncommenting more parameters will give better exploring power but will
# increase processing time in a combinatorial way
parametersSGD = {
    'vect__max_df': (0.5, 0.75, 1.0),
    'vect__max_features': (None, 500, 1000, 2000, 5000),
    'vect__ngram_range': ((1, 1), (1, 2), (1, 3)),  # unigrams or bigrams or thrigrams
    'tfidf__use_idf': (True, False),
    'tfidf__norm': ('l1', 'l2'),
    # 'clf__max_iter': (20,),
    'clf__alpha': (0.00001, 0.000001),
    'clf__penalty': ('l2', 'elasticnet'),
    'clf__max_iter': (80, 100, 200),
}

pipelineNB = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', MultinomialNB()),
])

parametersNB = {
    'vect__max_df': (0.5, 0.75, 1.0),
    'vect__max_features': (None, 500, 1000, 2000, 5000),
    'vect__ngram_range': ((1, 1), (1, 2), (1, 3)),  # unigrams or bigrams or thrigrams
    'tfidf__use_idf': (True, False),
    'tfidf__norm': ('l1', 'l2'),
    'clf__alpha': (0.00001, 0.000001),
}
### Perceptron -  In fact, Perceptron() is equivalent to SGDClassifier(loss="perceptron", eta0=1, learning_rate="constant", penalty=None)

pipelineSVM = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', SVC()),
])
parametersSVM = {
    'vect__max_df': (0.5, 0.75, 1.0),
    'vect__max_features': (None, 500, 1000, 2000, 5000),
    'vect__ngram_range': ((1, 1), (1, 2), (1, 3)),  # unigrams or bigrams or thrigrams
    'tfidf__use_idf': (True, False),
    'tfidf__norm': ('l1', 'l2'),
    'clf__kernel': ('linear', 'rbf'),
    'clf__C': [1, 10]
}

if __name__ == "__main__":

    print("=== SGDClassifier As Is===")
    dev_set = load_dataset('./cleaned_data/uk/dev_set.json')
    test_set = load_dataset('./cleaned_data/uk/test_set.json')

    dev_dataset = {}
    test_dataset = {}

    dev_dataset['data'] = list(map(itemgetter(1), dev_set))
    dev_dataset['target'] = list(map(itemgetter(0), dev_set))

    test_dataset['data'] = list(map(itemgetter(1), test_set))
    test_dataset['target'] = list(map(itemgetter(0), test_set))
    # multiprocessing requires the fork to happen in a __main__ protected
    # block
    parameters = parametersSGD
    pipeline = pipelineSGD
    benchmark(dev_dataset, test_dataset, pipeline, parameters)

    print("=== SGDClassifier Tokenized===")
    dev_set = load_dataset('./cleaned_data/uk/tok_dev_set.json')
    test_set = load_dataset('./cleaned_data/uk/tok_test_set.json')

    dev_dataset = {}
    test_dataset = {}

    dev_dataset['data'] = list(map(itemgetter(1), dev_set))
    dev_dataset['target'] = list(map(itemgetter(0), dev_set))

    test_dataset['data'] = list(map(itemgetter(1), test_set))
    test_dataset['target'] = list(map(itemgetter(0), test_set))
    parameters = parametersSGD
    pipeline = pipelineSGD
    benchmark(dev_dataset, test_dataset, pipeline, parameters, label="tok")

    print("=== SGDClassifier Lemma ===")
    dev_set = load_dataset('./cleaned_data/uk/lem_dev_set.json')
    test_set = load_dataset('./cleaned_data/uk/lem_test_set.json')

    dev_dataset = {}
    test_dataset = {}

    dev_dataset['data'] = list(map(itemgetter(1), dev_set))
    dev_dataset['target'] = list(map(itemgetter(0), dev_set))

    test_dataset['data'] = list(map(itemgetter(1), test_set))
    test_dataset['target'] = list(map(itemgetter(0), test_set))
    parameters = parametersSGD
    pipeline = pipelineSGD
    benchmark(dev_dataset, test_dataset, pipeline, parameters, label="lem")
    #
    # print("=== MultinomialNB ===")
    # parameters = parametersNB
    # pipeline = pipelineNB
    # benchmark(pipeline, parameters)

    # print("=== SVM ===")
    # parameters = parametersSVM

    # pipeline = pipelineSVM
    #
    # benchmark(pipeline, parameters)
    # find the best parameters for both the feature extraction and the
    # classifier
