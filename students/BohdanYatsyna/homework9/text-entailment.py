import argparse
from datetime import datetime

import features
import sklearn.linear_model as lm
import spacy
import wandb
from fileio import read_jsonnl
from process import get_sentences
from report import wandb_classification_report
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from tqdm import tqdm


def get_model(model_name):
    clf_model = None
    if model_name == 'log':
        clf_model = lm.LogisticRegression(random_state=42, solver=wandb.config.solver, max_iter=600, tol=0.00001, n_jobs=-1)

    if model_name == 'knn':
        clf_model = KNeighborsClassifier(n_neighbors=4, n_jobs=-1)

    if model_name == 'dtree':
        clf_model = DecisionTreeClassifier(random_state=42)

    if model_name == 'rtree':
        clf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

    if model_name == 'svm':
        clf_model = SVC(random_state=42, probability=True, tol=0.00001)

    if model_name == 'nb':
        clf_model = GaussianNB()

    if model_name == 'gbc':
        clf_model = GradientBoostingClassifier()

    if model_name == 'adaboost':
        clf_model = AdaBoostClassifier(n_estimators=500, learning_rate=0.01, random_state=42,
                                   base_estimator=DecisionTreeClassifier(max_depth=8,
                                                                         min_samples_leaf=10, random_state=42))
    if model_name == 'sgd':
        clf_model = SGDClassifier(alpha=0.00001, n_jobs=-1)

    return clf_model


def train_model(cls, X_train, y_train, X_test, y_test, name, wandb):

    if wandb.config.tfidf:
        clf = Pipeline([
            ('vect', DictVectorizer()),
            ('tf-idf', TfidfTransformer()),
            ('cls', cls)
        ])
    else:
        clf = Pipeline([
            ('vect', DictVectorizer()),
            ('cls', cls)
        ])
    clf.fit(train_features, train_labels)
    wandb_classification_report(clf, X_train, X_test, y_train, y_test, name, wandb)


config_defaults = {
    'solver': 'sag',
    'model': 'log',
    'tfidf': 0
}
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Textual entalailment trainer")
    parser.add_argument('--batch_size', help='Batch size (default=1000)', default=10000)
    parser.add_argument('--train_file', help='Train file location ', default="snli_1.0/snli_1.0_train.jsonl")
    parser.add_argument('--dev_file', help='Train file location ', default="snli_1.0/snli_1.0_dev.jsonl")
    parser.add_argument('--test_file', help='Train file location ', default="snli_1.0/snli_1.0_test.jsonl")
    parser.add_argument('--proba', help='If True - app work as sample with cutted data', default=False)
    parser.add_argument('--n_jobs', help='Number of workers (default=1) use all cores', default=1)
    parser.add_argument('--solver', help='type of solver for model (default=sag)', default='sag')
    parser.add_argument('--model', help='model type', default='log')
    parser.add_argument('--tfidf', help='Use TF-IDF True/False (default=False)', default=False)

    nlp = spacy.load("en_core_web_lg", disable=['ner'])

    opts = parser.parse_args()

    wandb.init(name="Added feature VERB and removed stop words", config=config_defaults)
    wandb.config.solver = opts.solver
    wandb.config.model = opts.model
    wandb.compat.tfidf = opts.tfidf

    # measure execution time
    start_time = datetime.now()

    train_data = read_jsonnl(opts.train_file)
    dev_data = read_jsonnl(opts.dev_file)
    test_data = read_jsonnl(opts.test_file)

    # Use catted sample of data for test your code
    if opts.proba:
        train_data = train_data[:30000]
        dev_data = dev_data[:2000]
        test_data = test_data[:2000]

    train_processed_sent1, train_processed_sent2, train_labels = get_sentences(nlp, train_data, opts.batch_size,
                                                                               opts.n_jobs, "Train data -", "train")
    dev_processed_sent1, dev_processed_sent2, dev_labels = get_sentences(nlp, dev_data, opts.batch_size, opts.n_jobs,
                                                                         "Dev data -", "dev")
    test_processed_sent1, test_processed_sent2, test_labels = get_sentences(nlp,test_data, opts.batch_size, opts.n_jobs, "Test data -", "test")
    train_features, dev_features, test_features = [], [], []

    for sent1, sent2 in tqdm(zip(train_processed_sent1, train_processed_sent2), desc='Prepare train features '):
        train_features.append(features.exctract(sent1, sent2))

    for sent1, sent2 in tqdm(zip(dev_processed_sent1, dev_processed_sent2), desc='Prepare dev features '):
        dev_features.append(features.exctract(sent1, sent2))

    model = get_model(wandb.config.model)

    train_model(model, train_features, train_labels, dev_features, dev_labels, model.__class__.__name__, wandb)
    # do your work here
    end_time = datetime.now()
    print('\n\nDuration: {}\n\n'.format(end_time - start_time))
