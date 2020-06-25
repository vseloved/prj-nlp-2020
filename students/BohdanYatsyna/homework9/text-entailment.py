import argparse
from datetime import datetime

import features

import sklearn.linear_model as lm
import spacy
from spacy.tokens import Token
import wandb
from fileio import read_jsonnl
from process import get_sentences
from report import wandb_classification_report
from spacy_custom import add_negation
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import Normalizer, MinMaxScaler
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from tqdm import tqdm
import nltk


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
        clf_model = GradientBoostingClassifier(verbose=1, tol=0.00001, n_estimators=200)

    if model_name == 'adaboost':
        clf_model = AdaBoostClassifier(n_estimators=500, learning_rate=0.01, random_state=42,
                                   base_estimator=DecisionTreeClassifier(max_depth=8,
                                                                         min_samples_leaf=10, random_state=42))
    if model_name == 'sgd':
        clf_model = SGDClassifier(alpha=0.00001, n_jobs=-1)

    return clf_model


def train_model(cls, wandb):

    if wandb.config.norm:
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
    return clf


config_wandb = {
    'solver': 'sag',
    'model': 'gbc',
    'norm': 0,
    'f_lemma_verb': 1,
    'f_lemma_noun': 1,
    'f_lemma_adj': 1,
    'f_lemma_adv': 1,
    'f_noun_prases': 1,
    'f_ner': 1,
    'f_bleu_avg': 1,
    'f_bleu_1': 1,
    'f_bleu_2': 1,
    'f_bleu_3': 1,
    'f_bleu_4': 1,
    'f_rouge1': 1,
    'f_rouge2': 1,
    'f_rougel': 1,
    'f_wer': 1,
    'f_sim_lema': 1,
    'f_sim_verb': 1,
    'f_len_sent1': 1,
    'f_len_sent2': 1,
    'f_syn': 1,
}
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Textual entalailment trainer")
    parser.add_argument('--batch_size', help='Batch size (default=1000)', default=8192)
    parser.add_argument('--train_file', help='Train file location ', default="snli_1.0/snli_1.0_train.jsonl")
    parser.add_argument('--dev_file', help='Train file location ', default="snli_1.0/snli_1.0_dev.jsonl")
    parser.add_argument('--test_file', help='Train file location ', default="snli_1.0/snli_1.0_test.jsonl")
    parser.add_argument('--proba', help='If True - app work as sample with cutted data', default=False)
    parser.add_argument('--n_jobs', help='Number of workers (default=1) ', default=12)
    parser.add_argument('--solver', help='type of solver for model (default=sag)', default='sag')
    parser.add_argument('--model', help='model type', default='gbc')
    parser.add_argument('--norm', help='Normalizer On/Off (default=False)', default=False)
    # features
    parser.add_argument('--f_lemma', help='f_lemma', default=1)
    parser.add_argument('--f_lemma_verb', help='f_lemma_verb', default=1)
    parser.add_argument('--f_lemma_noun', help='f_lemma_noun', default=1)
    parser.add_argument('--f_lemma_adj', help='f_lemma_adj', default=1)
    parser.add_argument('--f_lemma_adv', help='f_lemma_adv', default=1)
    parser.add_argument('--f_noun_prases', help='f_noun_prases', default=1)
    parser.add_argument('--f_ner', help='f_ner', default=1)
    parser.add_argument('--f_bleu_avg', help='f_bleu_avg', default=1)
    parser.add_argument('--f_bleu_1', help='f_bleu_1', default=1)
    parser.add_argument('--f_bleu_2', help='f_bleu_2', default=1)
    parser.add_argument('--f_bleu_3', help='f_bleu_3', default=1)
    parser.add_argument('--f_bleu_4', help='f_bleu_4', default=1)
    parser.add_argument('--f_rouge1', help='f_rouge1', default=1)
    parser.add_argument('--f_rouge2', help='f_rouge2', default=1)
    parser.add_argument('--f_rougel', help='f_rougel', default=1)
    parser.add_argument('--f_wer', help='f_wer', default=1)
    parser.add_argument('--f_sim_lema', help='f_sim_lema', default=1)
    parser.add_argument('--f_sim_verb', help='f_sim_verb', default=1)
    parser.add_argument('--f_len_sent1', help='f_len_sent1', default=1)
    parser.add_argument('--f_len_sent2', help='f_len_sent2', default=1)
    parser.add_argument('--f_syn', help='f_syn', default=1)



    nltk.download('wordnet')

    spacy.prefer_gpu()

    Token.set_extension("is_negative", default=False)
    nlp = spacy.load("en_core_web_md")
    nlp.add_pipe(add_negation)
    print(nlp.pipe_names)

    opts = parser.parse_args()

    config_wandb = {
        'solver': opts.solver,
        'model': opts.model,
        'norm': opts.norm,
        'f_lemma_verb': opts.f_lemma_verb,
        'f_lemma_noun': opts.f_lemma_noun,
        'f_lemma_adj': opts.f_lemma_adj,
        'f_lemma_adv': opts.f_lemma_adv,
        'f_noun_prases': opts.f_noun_prases,
        'f_ner': opts.f_ner,
        'f_bleu_avg': opts.f_bleu_avg,
        'f_bleu_1': opts.f_bleu_1,
        'f_bleu_2': opts.f_bleu_2,
        'f_bleu_3': opts.f_bleu_3,
        'f_bleu_4': opts.f_bleu_4,
        'f_rouge1': opts.f_rouge1,
        'f_rouge2': opts.f_rouge2,
        'f_rougel': opts.f_rougel,
        'f_wer': opts.f_wer,
        'f_sim_lema': opts.f_sim_lema,
        'f_sim_verb': opts.f_sim_verb,
        'f_len_sent1': opts.f_len_sent1,
        'f_len_sent2': opts.f_len_sent2,
        'f_syn': opts.f_syn,
    }

    wandb.init(project='homework9', name="features variation - 6 fixed params", config=config_wandb)

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
        train_features.append(features.exctract(sent1, sent2, wandb.config))

    for sent1, sent2 in tqdm(zip(dev_processed_sent1, dev_processed_sent2), desc='Prepare dev features '):
        dev_features.append(features.exctract(sent1, sent2, wandb.config))

    for sent1, sent2 in tqdm(zip(test_processed_sent1, test_processed_sent2), desc='Prepare test features '):
        test_features.append(features.exctract(sent1, sent2, wandb.config))

    model = get_model(wandb.config.model)

    clf = train_model(model, wandb)

    wandb_classification_report(clf, dev_features, test_features, dev_labels, test_labels, wandb)


    # do your work here
    end_time = datetime.now()
    print('\n\nDuration: {}\n\n'.format(end_time - start_time))
